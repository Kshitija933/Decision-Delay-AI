"""
DecisionDelay AI — Master Configuration
All hyperparameters, paths, and app constants in one place.
Targeting 93-97% accuracy via:
  - 25,000 samples, 200 epochs, batch=256
  - Mixup + LabelSmoothing + CosineAnnealing with warmup
  - 6-layer backbone: 1024→512→256→128→64→32
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Directory structure ──────────────────────────────────────────────────
DIRS = {
    "models":  BASE_DIR / "models",
    "reports": BASE_DIR / "reports",
    "data":    BASE_DIR / "data",
    "raw":     BASE_DIR / "data" / "raw",
    "proc":    BASE_DIR / "data" / "processed",
    "logs":    BASE_DIR / "logs",
}
for d in DIRS.values():
    d.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════
# MODEL CONFIG
# ══════════════════════════════════════════════════════════
@dataclass
class ModelConfig:
    # ── Paths ────────────────────────────────────────────
    model_path:   str = str(DIRS["models"] / "decisiondelay_net.pt")
    scaler_path:  str = str(DIRS["models"] / "scaler.pkl")
    encoder_path: str = str(DIRS["models"] / "label_encoder.pkl")
    feature_path: str = str(DIRS["models"] / "feature_cols.json")
    meta_path:    str = str(DIRS["models"] / "model_meta.json")
    ckpt_dir:     str = str(DIRS["models"] / "checkpoints")

    # ── Architecture — 4-layer backbone ─────────────────
    # Wider + deeper for 93-97% target
    hidden_dims:  List[int] = field(default_factory=lambda: [512, 512, 512, 512])
    dropout:      float = 0.10          # Reduced for larger model
    dropout_head: float = 0.05          # Lighter in classification head

    # ── Training hyperparameters ─────────────────────────
    epochs:        int   = 150
    batch_size:    int   = 64           # Smaller batch for more updates
    learning_rate: float = 5e-4         # Smoother convergence
    min_lr:        float = 1e-6         # Cosine annealing floor
    weight_decay:  float = 1e-4
    warmup_epochs: int   = 10           # Linear warmup
    patience:      int   = 30           # Early stopping
    grad_clip:     float = 1.0

    # ── Loss configuration ───────────────────────────────
    alpha:          float = 0.98        # Weight: alpha*CE + (1-alpha)*MSE
    label_smooth:   float = 0.02        # CrossEntropy label smoothing
    mixup_alpha:    float = 0.2         # Mixup augmentation strength
    mixup_prob:     float = 0.5         # Probability of applying mixup

    # ── Data split ───────────────────────────────────────
    test_size:    float = 0.075         # 7.5% test
    val_size:     float = 0.075         # 7.5% val → 85% train

    # ── Misc ─────────────────────────────────────────────
    seed:       int   = 42
    num_workers: int  = 0

    def __post_init__(self):
        os.makedirs(self.ckpt_dir, exist_ok=True)


# ══════════════════════════════════════════════════════════
# APP CONFIG
# ══════════════════════════════════════════════════════════
@dataclass
class AppConfig:
    # Dataset
    n_synthetic_samples: int    = 15_000
    dataset_path:        str    = str(DIRS["proc"] / "decision_delay_processed.csv")
    raw_path:            str    = str(DIRS["raw"]  / "decision_delay_raw.csv")

    # Use cases (inputs)
    use_cases: List[str] = field(default_factory=lambda: [
        "Fitness", "Studying", "Career Choices"
    ])

    # Delay causes (target classes)
    delay_causes: List[str] = field(default_factory=lambda: [
        "Fear of Failure",
        "Overwhelm / Complexity",
        "Lack of Immediate Reward",
        "Past Failure Loop",
        "Perfectionism",
        "Decision Fatigue",
    ])

    # Cause icons for UI
    cause_icons: dict = field(default_factory=lambda: {
        "Fear of Failure":          "😨",
        "Overwhelm / Complexity":   "🌊",
        "Lack of Immediate Reward": "⏳",
        "Past Failure Loop":        "🔁",
        "Perfectionism":            "🎯",
        "Decision Fatigue":         "🧠",
    })

    # Cause colors for UI
    cause_colors: dict = field(default_factory=lambda: {
        "Fear of Failure":          "#F43F5E",
        "Overwhelm / Complexity":   "#7C3AED",
        "Lack of Immediate Reward": "#F59E0B",
        "Past Failure Loop":        "#EF4444",
        "Perfectionism":            "#EC4899",
        "Decision Fatigue":         "#0EA5E9",
    })

    # Input feature ranges for UI
    feature_ranges: dict = field(default_factory=lambda: {
        "task_difficulty":      {"min": 0.0, "max": 10.0, "default": 5.0, "step": 0.1},
        "time_to_reward":       {"min": 0.0, "max": 10.0, "default": 5.0, "step": 0.1},
        "past_failure_loops":   {"min": 0.0, "max": 10.0, "default": 2.0, "step": 0.1},
        "self_efficacy":        {"min": 0.0, "max": 10.0, "default": 5.5, "step": 0.1},
        "stress_level":         {"min": 0.0, "max": 10.0, "default": 4.8, "step": 0.1},
        "goal_clarity":         {"min": 0.0, "max": 10.0, "default": 5.2, "step": 0.1},
        "social_support":       {"min": 0.0, "max": 10.0, "default": 5.0, "step": 0.1},
        "intrinsic_motivation": {"min": 0.0, "max": 10.0, "default": 5.1, "step": 0.1},
        "habit_strength":       {"min": 0.0, "max": 10.0, "default": 3.2, "step": 0.1},
        "distraction_level":    {"min": 0.0, "max": 10.0, "default": 4.9, "step": 0.1},
    })

    # Version
    version: str = "2.1.0"
    app_name: str = "DecisionDelay AI"


# ── Singleton instances ──────────────────────────────────────────────────────
MODEL_CFG = ModelConfig()
APP_CFG   = AppConfig()

class NudgeConfig:
    pass