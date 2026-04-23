"""
DecisionDelay AI — Core Analyzer v2.1
======================================
DecisionDelayNet v2.1 — 6-layer backbone targeting 93-97% accuracy:
  Input → 1024 → 512 → 256 → 128 → 64 → 32 → [6-class | regression]

Key improvements over v2:
  • 6-layer backbone (was 4) — deeper representations
  • Skip connections in backbone — residual-style gradient flow
  • SiLU (Swish) activation — smoother than GELU in practice
  • Attention-weighted feature aggregation before heads
  • Separate BN per residual path
  • Kaiming He init on all Linear layers
  • 4 extra engineered features (10 total derived)
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import joblib, json, os
from typing import Dict, List, Optional
from configs.settings import MODEL_CFG, APP_CFG


# ════════════════════════════════════════════════════════════════════
# RESIDUAL BLOCK — skip connection for gradient health
# ════════════════════════════════════════════════════════════════════
class ResidualBlock(nn.Module):
    """
    Linear(in→out) → BN → SiLU → Dropout → Linear(out→out) → BN
    + skip projection if in != out.
    """
    def __init__(self, in_dim: int, out_dim: int, dropout: float = 0.18):
        super().__init__()
        self.fc1  = nn.Linear(in_dim,  out_dim)
        self.bn1  = nn.BatchNorm1d(out_dim)
        self.act1 = nn.SiLU()
        self.drop = nn.Dropout(dropout)
        self.fc2  = nn.Linear(out_dim, out_dim)
        self.bn2  = nn.BatchNorm1d(out_dim)

        # Skip projection (only needed when dims change)
        if in_dim != out_dim:
            self.skip = nn.Sequential(
                nn.Linear(in_dim, out_dim, bias=False),
                nn.BatchNorm1d(out_dim),
            )
        else:
            self.skip = nn.Identity()

        self.act_out = nn.SiLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = self.skip(x)
        out = self.fc1(x)
        out = self.bn1(out)
        out = self.act1(out)
        out = self.drop(out)
        out = self.fc2(out)
        out = self.bn2(out)
        return self.act_out(out + residual)


# ════════════════════════════════════════════════════════════════════
# FEATURE ATTENTION — channel-wise gating
# ════════════════════════════════════════════════════════════════════
class FeatureAttention(nn.Module):
    """
    Squeeze-and-Excitation style attention on the bottleneck features.
    Learns which features to amplify before the classification / regression heads.
    """
    def __init__(self, dim: int, reduction: int = 4):
        super().__init__()
        hid = max(dim // reduction, 8)
        self.gate = nn.Sequential(
            nn.Linear(dim, hid),
            nn.ReLU(),
            nn.Linear(hid, dim),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * self.gate(x)


# ════════════════════════════════════════════════════════════════════
# DECISIONDELAYNET v2.1 — Main Model
# ════════════════════════════════════════════════════════════════════
class DecisionDelayNet(nn.Module):
    """
    6-layer residual backbone → attention gate → dual heads.

    Architecture summary:
      Input(19) → ResBlock(1024) → ResBlock(512) → ResBlock(256)
               → ResBlock(128)  → ResBlock(64)   → ResBlock(32)
               → FeatureAttention(32)
               → ClassifierHead(32 → num_classes)
               → RegressionHead(32 → 1)

    Targets: 93-97% test accuracy on 25k-sample balanced dataset.
    """

    def __init__(
        self,
        input_dim:   int,
        num_classes: int = 6,
        hidden_dims: List[int] = None,
        dropout:     float = 0.10,
        dropout_head:float = 0.05,
    ):
        super().__init__()
        if hidden_dims is None:
            hidden_dims = MODEL_CFG.hidden_dims

        # ── Input projection ──────────────────────────────────────────
        self.input_proj = nn.Sequential(
            nn.Linear(input_dim, hidden_dims[0]),
            nn.BatchNorm1d(hidden_dims[0]),
            nn.SiLU(),
            nn.Dropout(dropout * 0.5),
        )

        # ── Residual backbone ─────────────────────────────────────────
        blocks = []
        prev = hidden_dims[0]
        for h in hidden_dims[1:]:
            blocks.append(ResidualBlock(prev, h, dropout=dropout))
            prev = h
        self.backbone = nn.Sequential(*blocks)

        # ── Attention gate ────────────────────────────────────────────
        bottleneck = hidden_dims[-1]
        self.attention = FeatureAttention(bottleneck, reduction=4)

        # ── Classification head ───────────────────────────────────────
        self.classifier = nn.Sequential(
            nn.Linear(bottleneck, bottleneck * 2),
            nn.BatchNorm1d(bottleneck * 2),
            nn.SiLU(),
            nn.Dropout(dropout_head),
            nn.Linear(bottleneck * 2, bottleneck),
            nn.SiLU(),
            nn.Dropout(dropout_head * 0.5),
            nn.Linear(bottleneck, num_classes),
        )

        # ── Regression head ───────────────────────────────────────────
        self.regressor = nn.Sequential(
            nn.Linear(bottleneck, bottleneck),
            nn.SiLU(),
            nn.Dropout(dropout_head),
            nn.Linear(bottleneck, 1),
            nn.Sigmoid(),
        )

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor):
        x = self.input_proj(x)       # (B, 1024)
        x = self.backbone(x)         # (B, 32)
        x = self.attention(x)        # (B, 32) — gated
        logits = self.classifier(x)  # (B, num_classes)
        sev    = self.regressor(x).squeeze(-1)  # (B,)
        return logits, sev


# ════════════════════════════════════════════════════════════════════
# FEATURE ENGINEERING — 10 raw + 10 derived = 20 features (+domain OHE)
# ════════════════════════════════════════════════════════════════════
NUMERIC_FEATURES = [
    "task_difficulty", "time_to_reward", "past_failure_loops",
    "self_efficacy", "stress_level", "goal_clarity",
    "social_support", "intrinsic_motivation", "habit_strength",
    "distraction_level",
]


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derives 10 engineered features from the 10 raw inputs.
    All formula names match the project PDF / paper.
    """
    df = df.copy()
    eps = 1e-8

    # ── Core 6 (PDF-named) ──────────────────────────────────────────
    df["reward_proximity"]   = 1.0 / (df["time_to_reward"] + 1.0)
    df["failure_weight"]     = df["past_failure_loops"] * (10.0 - df["self_efficacy"])
    df["motivation_deficit"] = (10.0 - df["intrinsic_motivation"]) * (10.0 - df["social_support"])
    df["cognitive_load"]     = df["task_difficulty"] + df["stress_level"] + df["distraction_level"]
    df["support_index"]      = df["self_efficacy"] + df["social_support"] + df["habit_strength"]
    df["reward_perception"]  = df["intrinsic_motivation"] / (df["time_to_reward"] + 1.0 + eps)

    # ── 4 Extra high-signal interactions (v2.1 additions) ───────────
    df["efficacy_clarity"]   = df["self_efficacy"] * df["goal_clarity"] / 100.0
    df["burnout_index"]      = df["stress_level"]  * df["distraction_level"] / 100.0
    df["action_potential"]   = (df["intrinsic_motivation"] + df["habit_strength"]
                                + df["goal_clarity"]) / 30.0
    df["barrier_score"]      = (df["task_difficulty"] + df["past_failure_loops"]
                                + (10 - df["self_efficacy"])) / 30.0

    # ── One-hot encode domain ────────────────────────────────────────
    if "use_case" in df.columns:
        df = pd.get_dummies(df, columns=["use_case"], prefix="domain", dtype=float)

    # ── Drop remaining non-numeric (except targets) ──────────────────
    targets = {"delay_cause", "delay_severity"}
    bad = [c for c in df.columns if c not in targets and df[c].dtype == object]
    if bad:
        df = df.drop(columns=bad)

    return df


# ════════════════════════════════════════════════════════════════════
# DELAY ANALYZER — inference wrapper
# ════════════════════════════════════════════════════════════════════
class DelayAnalyzer:
    """
    Loads trained DecisionDelayNet v2.1 and provides:
      - predict(inputs)      → ML prediction
      - predict_mock(inputs) → rule-based fallback (no model needed)
    """

    def __init__(self):
        self.model         = None
        self.scaler        = None
        self.label_encoder = None
        self.feature_cols  = None
        self.meta: Dict    = {}
        self._loaded       = False

    def is_ready(self) -> bool:
        paths = [
            MODEL_CFG.model_path,
            MODEL_CFG.scaler_path,
            MODEL_CFG.encoder_path,
            MODEL_CFG.feature_path,
            MODEL_CFG.meta_path,
        ]
        ready = all(os.path.exists(p) for p in paths)
        if ready and not self._loaded:
            # Check if we should try loading
            return True
        return ready

    def load(self) -> bool:
        if self._loaded:
            return True
        if not self.is_ready():
            return False
        try:
            m_dir = os.path.dirname(MODEL_CFG.model_path)
            print(f"[*] Loading model from {m_dir}...")
            self.scaler        = joblib.load(MODEL_CFG.scaler_path)
            self.label_encoder = joblib.load(MODEL_CFG.encoder_path)
            with open(MODEL_CFG.feature_path, encoding="utf-8") as f:
                self.feature_cols = json.load(f)
            with open(MODEL_CFG.meta_path, encoding="utf-8") as f:
                self.meta = json.load(f)
            
            # Robust extraction of architecture from meta
            h_dims = self.meta.get("hidden_dims", MODEL_CFG.hidden_dims)
            in_dim = self.meta.get("input_dim", len(self.feature_cols))
            
            self.model = DecisionDelayNet(
                input_dim    = in_dim,
                num_classes  = self.meta.get("num_classes", 6),
                hidden_dims  = h_dims,
                dropout      = self.meta.get("dropout", 0.1),
                dropout_head = self.meta.get("dropout_head", 0.05),
            )
            self.model.load_state_dict(
                torch.load(MODEL_CFG.model_path, map_location="cpu", weights_only=True)
            )
            self.model.eval()
            self._loaded = True
            print(f"[✓] DecisionDelayNet {self.meta.get('version','v2')} loaded successfully.")
            return True
        except Exception as e:
            import traceback
            print(f"[!] Model load error: {e}")
            # traceback.print_exc() # Mute for cleaner UI, unless debugging
            return False

    def predict(self, inputs: Dict) -> Dict:
        if not self._loaded:
            if not self.load():
                return self.predict_mock(inputs)

        row      = {k: float(inputs.get(k, 5.0)) for k in NUMERIC_FEATURES}
        row["use_case"] = inputs.get("use_case", "Fitness")
        df       = pd.DataFrame([row])
        df       = engineer_features(df)

        # Align columns
        for col in self.feature_cols:
            if col not in df.columns:
                df[col] = 0.0
        df = df[self.feature_cols]

        try:
            X = self.scaler.transform(df.values.astype(np.float32))
            with torch.no_grad():
                logits, sev_tensor = self.model(torch.tensor(X, dtype=torch.float32))
                sev = float(sev_tensor.numpy()[0])
                
                # SKEPTICISM: If the model predicts absolute zero/one, check against baseline.
                if sev < 0.01 or sev > 0.99:
                    mock_res = self.predict_mock(inputs)
                    # If mock says there is a delay (>10%), but model says 0, use mock.
                    if mock_res["delay_severity"] > 0.10 and sev < 0.01:
                        print(f"[!] Model output suspiciously low ({sev}). Using baseline.")
                        return mock_res
                
                probs = torch.softmax(logits, dim=1).numpy()[0]
                idx   = int(probs.argmax())
                cause = self.label_encoder.inverse_transform([idx])[0]

            # Ensure a 'minimum active visibility' of 5%
            sev = max(float(sev), 0.05)
            
            return {
                "delay_cause":         cause,
                "delay_severity":      round(sev, 4),
                "confidence":          round(float(probs[idx]), 4),
                "class_probabilities": dict(
                    zip(self.label_encoder.classes_, probs.round(4).tolist())
                ),
                "model_type":          "ML Model (Active)",
            }
        except Exception as e:
            print(f"[!] Evaluation failed: {e}. Falling back to baseline.")
            return self.predict_mock(inputs)

    def predict_mock(self, inputs: Dict) -> Dict:
        """Rule-based fallback when model is not yet trained."""
        td  = float(inputs.get("task_difficulty",      5))
        tr  = float(inputs.get("time_to_reward",       5))
        pfl = float(inputs.get("past_failure_loops",   2))
        se  = float(inputs.get("self_efficacy",        5))
        sl  = float(inputs.get("stress_level",         5))
        dl  = float(inputs.get("distraction_level",    5))
        im  = float(inputs.get("intrinsic_motivation", 5))
        gc  = float(inputs.get("goal_clarity",         5))
        ss  = float(inputs.get("social_support",       5))
        hs  = float(inputs.get("habit_strength",       3))

        failure_weight     = pfl * (10 - se)
        cognitive_load     = td + sl + dl
        motivation_deficit = (10 - im) * (10 - ss)
        support_index      = se + ss + hs

        scores = {
            "Fear of Failure":          failure_weight * 0.65 + (10 - se) * 0.35,
            "Overwhelm / Complexity":   cognitive_load * 0.50,
            "Lack of Immediate Reward": tr * 1.3 + motivation_deficit * 0.05,
            "Past Failure Loop":        failure_weight * 0.50 + sl * 0.50,
            "Perfectionism":            (10 - gc) * 0.60 + td * 0.40,
            "Decision Fatigue":         cognitive_load * 0.35 + (10 - ss) * 0.40,
        }
        total = max(sum(scores.values()), 1e-6)
        probs = {k: round(v / total, 4) for k, v in scores.items()}
        cause = max(scores, key=scores.get)
        severity = float(np.clip(
            cognitive_load / 45.0 + failure_weight / 120.0 - support_index / 55.0 + 0.13, 0.05, 1
        ))
        return {
            "delay_cause":         cause,
            "delay_severity":      round(severity, 4),
            "confidence":          probs[cause],
            "class_probabilities": probs,
            "model_type":          "Rule-Based Fallback",
        }