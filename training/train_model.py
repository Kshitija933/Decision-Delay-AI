"""
DecisionDelay AI — Neural Network Training  (DecisionDelayNet v2)
=================================================================
Upgraded for 90-95% accuracy:
  Architecture : 512 → 256 → 128 → 64 (4-layer backbone)
  Dataset size : 25,000 samples
  Epochs       : 150
  Batch size   : 128
  LR           : 8e-4 with 10-epoch warmup + Cosine Annealing
  Loss         : 75% CrossEntropy (label-smooth 0.05) + 25% MSE
  Regularise   : Dropout 0.20 + BatchNorm + GradClip(1.0) + WD 1e-4
  Target       : 90-95% test accuracy

Run from project root:
    python training/train.py
"""

import os, sys, json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data    import Dataset, DataLoader, WeightedRandomSampler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing   import StandardScaler, LabelEncoder
from sklearn.metrics         import classification_report, confusion_matrix
import joblib, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from configs.settings import MODEL_CFG, APP_CFG
from core.analyzer    import DecisionDelayNet, engineer_features

MODELS_DIR  = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(MODELS_DIR,  exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

SEED = MODEL_CFG.seed
torch.manual_seed(SEED)
np.random.seed(SEED)


# ─────────────────────────────────────────────────────────────
# DATASET
# ─────────────────────────────────────────────────────────────

class DelayDataset(Dataset):
    def __init__(self, X, yc, ys):
        self.X  = torch.tensor(X,  dtype=torch.float32)
        self.yc = torch.tensor(yc, dtype=torch.long)
        self.ys = torch.tensor(ys, dtype=torch.float32)
    def __len__(self):        return len(self.X)
    def __getitem__(self, i): return self.X[i], self.yc[i], self.ys[i]


# ─────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    """
    Priority: processed CSV → raw (inline preprocess) → auto-generate
    """
    processed = APP_CFG.dataset_path
    raw       = os.path.join(BASE_DIR, "data", "raw", "decision_delay_raw.csv")

    if os.path.exists(processed):
        print(f"[✓] Loading preprocessed data: {processed}")
        df = pd.read_csv(processed)
        if "reward_proximity" not in df.columns:
            print("[!] Re-engineering features...")
            df = engineer_features(df)
        return df

    import subprocess
    if os.path.exists(raw):
        print("[!] Preprocessing raw data...")
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "data", "preprocessing.py")])
        if os.path.exists(processed):
            return pd.read_csv(processed)

    print(f"[!] Generating synthetic dataset ({APP_CFG.n_synthetic_samples:,} samples)...")
    os.makedirs(os.path.dirname(processed), exist_ok=True)
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "data", "raw_data.py")])
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "data", "preprocessing.py")])
    if os.path.exists(processed):
        return pd.read_csv(processed)

    # last resort in-memory
    from data.raw_data import generate_raw
    df = generate_raw(APP_CFG.n_synthetic_samples, seed=SEED)
    df.to_csv(processed, index=False)
    return df


# ─────────────────────────────────────────────────────────────
# PREPARE  — clean, encode, scale
# ─────────────────────────────────────────────────────────────

def prepare(df: pd.DataFrame):
    df = df.copy()

    # 1. Engineer if missing
    if "reward_proximity" not in df.columns:
        print("[!] Applying engineer_features()...")
        df = engineer_features(df)

    # 2. Drop metadata
    df = df.drop(columns=[c for c in ["respondent_id","delay_severity_raw"] if c in df.columns])

    # 3. One-hot encode use_case if still string
    if "use_case" in df.columns:
        df = pd.get_dummies(df, columns=["use_case"], prefix="domain", dtype=float)

    # 4. Drop any remaining string columns (safety net)
    TARGET = {"delay_cause", "delay_severity"}
    bad = [c for c in df.columns if c not in TARGET and df[c].dtype == object]
    if bad:
        print(f"[!] Dropping non-numeric: {bad}")
        df = df.drop(columns=bad)

    # 5. Fill any NaN (shouldn't remain after preprocessing, but guard anyway)
    feat_cols = [c for c in df.columns if c not in TARGET]
    df[feat_cols] = df[feat_cols].fillna(df[feat_cols].median())

    X  = df[feat_cols].values.astype(np.float32)
    yc = df["delay_cause"].values
    ys = df["delay_severity"].values.astype(np.float32)

    print(f"[✓] Feature matrix : {X.shape[0]:,} rows × {X.shape[1]} cols")

    le     = LabelEncoder()
    yc_enc = le.fit_transform(yc)
    sc     = StandardScaler()
    X_sc   = sc.fit_transform(X)

    joblib.dump(sc, MODEL_CFG.scaler_path)
    joblib.dump(le, MODEL_CFG.encoder_path)
    with open(MODEL_CFG.feature_path, "w", encoding="utf-8") as f:
        json.dump(feat_cols, f)

    return X_sc, yc_enc, ys, sc, le, feat_cols


# ─────────────────────────────────────────────────────────────
# LR WARMUP SCHEDULER
# ─────────────────────────────────────────────────────────────

class WarmupCosineScheduler:
    """Linear warmup then cosine annealing."""
    def __init__(self, optimizer, warmup_epochs, total_epochs, base_lr, min_lr=1e-6):
        self.opt          = optimizer
        self.warmup       = warmup_epochs
        self.total        = total_epochs
        self.base_lr      = base_lr
        self.min_lr       = min_lr
        self.current_epoch= 0

    def step(self):
        e = self.current_epoch
        if e < self.warmup:
            lr = self.base_lr * (e + 1) / self.warmup
        else:
            progress = (e - self.warmup) / (self.total - self.warmup)
            lr = self.min_lr + 0.5 * (self.base_lr - self.min_lr) * (
                1 + np.cos(np.pi * progress))
        for g in self.opt.param_groups:
            g["lr"] = lr
        self.current_epoch += 1
        return lr


# ─────────────────────────────────────────────────────────────
# TRAIN / EVAL EPOCHS
# ─────────────────────────────────────────────────────────────

def train_epoch(model, loader, opt, device, alpha=0.75, label_smooth=0.05):
    model.train()
    cls_fn = nn.CrossEntropyLoss(label_smoothing=label_smooth)
    reg_fn = nn.MSELoss()
    total, correct, n = 0.0, 0, 0
    for X, yc, ys in loader:
        X, yc, ys = X.to(device), yc.to(device), ys.to(device)
        opt.zero_grad()
        logits, sev = model(X)
        loss = alpha * cls_fn(logits, yc) + (1 - alpha) * reg_fn(sev, ys)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        opt.step()
        total   += loss.item() * len(X)
        correct += (logits.argmax(1) == yc).sum().item()
        n       += len(X)
    return total / n, correct / n


@torch.no_grad()
def eval_epoch(model, loader, device, alpha=0.75):
    model.eval()
    cls_fn = nn.CrossEntropyLoss()
    reg_fn = nn.MSELoss()
    total, correct, n = 0.0, 0, 0
    all_pred, all_true = [], []
    for X, yc, ys in loader:
        X, yc, ys = X.to(device), yc.to(device), ys.to(device)
        logits, sev = model(X)
        loss = alpha * cls_fn(logits, yc) + (1 - alpha) * reg_fn(sev, ys)
        total   += loss.item() * len(X)
        pred     = logits.argmax(1)
        correct += (pred == yc).sum().item()
        n       += len(X)
        all_pred.extend(pred.cpu().numpy())
        all_true.extend(yc.cpu().numpy())
    return total / n, correct / n, all_pred, all_true


# ─────────────────────────────────────────────────────────────
# PLOTS
# ─────────────────────────────────────────────────────────────

def save_training_plots(history: dict):
    epochs = range(1, len(history["train_loss"]) + 1)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("DecisionDelayNet v2 — Training History (Target 90-95%)",
                 fontsize=13, fontweight="bold")

    axes[0].plot(epochs, history["train_loss"], label="Train", color="#1A56DB", lw=2)
    axes[0].plot(epochs, history["val_loss"],   label="Val",   color="#F43F5E", lw=2, ls="--")
    axes[0].set_xlabel("Epoch"); axes[0].set_ylabel("Loss")
    axes[0].set_title("Loss (75% CE + 25% MSE)"); axes[0].legend(); axes[0].grid(alpha=0.3)

    axes[1].plot(epochs, [a*100 for a in history["train_acc"]], label="Train", color="#7C3AED", lw=2)
    axes[1].plot(epochs, [a*100 for a in history["val_acc"]],   label="Val",   color="#F59E0B", lw=2, ls="--")
    axes[1].axhline(90, color="#10B981", ls=":", lw=1.5, label="90-95% target")
    axes[1].set_xlabel("Epoch"); axes[1].set_ylabel("Accuracy (%)")
    axes[1].set_title("Accuracy Curve"); axes[1].legend(); axes[1].grid(alpha=0.3)

    axes[2].plot(epochs, history["lr"], color="#0EA5E9", lw=2)
    axes[2].set_xlabel("Epoch"); axes[2].set_ylabel("Learning Rate")
    axes[2].set_title("LR Schedule (Warmup + Cosine)"); axes[2].grid(alpha=0.3)

    plt.tight_layout()
    path = os.path.join(REPORTS_DIR, "training_history.png")
    plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[✓] {path}")


def save_confusion_matrix(true, pred, classes, acc):
    cm = confusion_matrix(true, pred)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=classes, yticklabels=classes,
                annot_kws={"size": 10}, ax=ax)
    ax.set_xlabel("Predicted"); ax.set_ylabel("True")
    ax.set_title(f"DecisionDelayNet v2 — Confusion Matrix  (Test Acc: {acc*100:.2f}%)",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(REPORTS_DIR, "nn_confusion_matrix.png")
    plt.savefig(path, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[✓] {path}")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("\n" + "="*65)
    print("  DecisionDelay AI - Neural Network Training v2")
    print("  Target: 90-95% Test Accuracy")
    print("="*65)
    print(f"  Device      : {device}")
    print(f"  Architecture: {MODEL_CFG.hidden_dims}  (4-layer backbone)")
    print(f"  Epochs      : {MODEL_CFG.epochs}")
    print(f"  Batch size  : {MODEL_CFG.batch_size}")
    print(f"  LR          : {MODEL_CFG.learning_rate}  (warmup {MODEL_CFG.warmup_epochs} ep)")
    print(f"  Loss        : {int(MODEL_CFG.alpha*100)}% CE (smooth={MODEL_CFG.label_smooth}) "
          f"+ {int((1-MODEL_CFG.alpha)*100)}% MSE")
    print(f"  Dropout     : {MODEL_CFG.dropout}")

    df = load_data()
    print(f"\n  Dataset rows : {len(df):,}")
    print(f"  Class dist   :\n{df['delay_cause'].value_counts().to_string()}\n")

    X, yc, ys, sc, le, feat_cols = prepare(df)
    input_dim   = X.shape[1]
    num_classes = len(le.classes_)
    print(f"  Input features : {input_dim}")
    print(f"  Classes        : {le.classes_.tolist()}")

    # ── Split 85/7.5/7.5 (more training data) ──
    Xt, X_test, yct, yc_test, yst, ys_test = train_test_split(
        X, yc, ys, test_size=MODEL_CFG.test_size,
        random_state=SEED, stratify=yc)
    X_train, X_val, yc_train, yc_val, ys_train, ys_val = train_test_split(
        Xt, yct, yst,
        test_size=MODEL_CFG.val_size / (1 - MODEL_CFG.test_size),
        random_state=SEED, stratify=yct)

    print(f"\n  Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}")

    # ── Weighted sampler for balanced training ──
    class_counts  = np.bincount(yc_train)
    class_weights = 1.0 / np.maximum(class_counts, 1)
    sample_weights= class_weights[yc_train]
    sampler = WeightedRandomSampler(
        weights=torch.tensor(sample_weights, dtype=torch.float32),
        num_samples=len(yc_train), replacement=True
    )

    def make_dl(X_, yc_, ys_, use_sampler=False):
        ds = DelayDataset(X_, yc_, ys_)
        return DataLoader(ds, batch_size=MODEL_CFG.batch_size,
                          sampler=sampler if use_sampler else None,
                          shuffle=not use_sampler, num_workers=0,
                          pin_memory=(device == "cuda"))

    train_dl = make_dl(X_train, yc_train, ys_train, use_sampler=True)
    val_dl   = make_dl(X_val,   yc_val,   ys_val)
    test_dl  = make_dl(X_test,  yc_test,  ys_test)

    # ── Model ──
    model = DecisionDelayNet(
        input_dim=input_dim, num_classes=num_classes,
        hidden_dims=MODEL_CFG.hidden_dims, dropout=MODEL_CFG.dropout,
    ).to(device)
    params = sum(p.numel() for p in model.parameters())
    print(f"  Parameters     : {params:,}")

    # ── Optimiser ──
    opt = torch.optim.AdamW(model.parameters(),
                             lr=MODEL_CFG.learning_rate,
                             weight_decay=MODEL_CFG.weight_decay,
                             betas=(0.9, 0.999))

    scheduler = WarmupCosineScheduler(
        opt,
        warmup_epochs=MODEL_CFG.warmup_epochs,
        total_epochs=MODEL_CFG.epochs,
        base_lr=MODEL_CFG.learning_rate,
        min_lr=1e-6,
    )

    # ── Training loop ──
    history      = {"train_loss":[],"val_loss":[],"train_acc":[],"val_acc":[],"lr":[]}
    best_val_acc = 0.0
    patience     = 25          # early stopping patience
    no_improve   = 0

    print(f"\n{'-'*65}\n  Training...\n")

    for ep in tqdm(range(1, MODEL_CFG.epochs + 1), desc="Training"):
        lr = scheduler.step()
        tl, ta       = train_epoch(model, train_dl, opt, device,
                                   MODEL_CFG.alpha, MODEL_CFG.label_smooth)
        vl, va, _, _ = eval_epoch(model, val_dl, device, MODEL_CFG.alpha)

        history["train_loss"].append(tl)
        history["val_loss"].append(vl)
        history["train_acc"].append(ta)
        history["val_acc"].append(va)
        history["lr"].append(lr)

        if va > best_val_acc:
            best_val_acc = va
            no_improve   = 0
            torch.save(model.state_dict(), MODEL_CFG.model_path)
        else:
            no_improve += 1

        if ep % 10 == 0 or ep <= 5:
            tqdm.write(
                f"  Ep {ep:3d}/{MODEL_CFG.epochs} | "
                f"Loss {tl:.4f}/{vl:.4f} | "
                f"Acc {ta*100:.2f}%/{va*100:.2f}% | "
                f"LR {lr:.2e}"
            )

        # Early stopping
        if no_improve >= patience:
            print(f"\n  [!] Early stopping at epoch {ep} (no improvement for {patience} epochs)")
            break

    # ── Final evaluation ──
    print(f"\n{'-'*65}")
    print("  Loading best model for test evaluation...")
    model.load_state_dict(torch.load(MODEL_CFG.model_path, map_location="cpu"))
    _, test_acc, preds, true = eval_epoch(model, test_dl, device)
    achieved = "[OK]" if test_acc >= 0.90 else "[WARN]"
    print(f"\n  {achieved} Test Accuracy  : {test_acc*100:.2f}%  (target: 90-95%)")
    print(f"     Best Val Acc  : {best_val_acc*100:.2f}%\n")
    print(classification_report(true, preds, target_names=le.classes_, zero_division=0))

    save_training_plots(history)
    save_confusion_matrix(true, preds, le.classes_, test_acc)

    meta = {
        "input_dim":     input_dim,
        "num_classes":   num_classes,
        "classes":       le.classes_.tolist(),
        "feature_cols":  feat_cols,
        "hidden_dims":   MODEL_CFG.hidden_dims,
        "dropout":       MODEL_CFG.dropout,
        "test_accuracy": round(test_acc, 4),
        "best_val_acc":  round(best_val_acc, 4),
        "trained_at":    datetime.now().isoformat(),
        "epochs":        MODEL_CFG.epochs,
        "batch_size":    MODEL_CFG.batch_size,
        "optimizer":     "AdamW + Warmup-Cosine LR",
        "loss_mix":      f"{int(MODEL_CFG.alpha*100)}% CE(smooth={MODEL_CFG.label_smooth}) "
                         f"+ {int((1-MODEL_CFG.alpha)*100)}% MSE",
        "regularization":"Dropout 0.25 + BatchNorm + GradClip(1.0) + WD=1e-4",
        "dataset_size":  int(len(df)),
        "engineered_features": [
            "reward_proximity","failure_weight","motivation_deficit",
            "cognitive_load","support_index","reward_perception",
        ],
    }
    with open(MODEL_CFG.meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"[✓] Metadata saved : {MODEL_CFG.meta_path}")

    print("\n" + "="*65)
    print(f"  TRAINING COMPLETE")
    print(f"  Test Accuracy : {test_acc*100:.2f}%")
    print(f"  Target        : 90-95%   {'[ACHIEVED]' if test_acc >= 0.90 else '[WARN] Run again or add data'}")
    print(f"  Model saved   : {MODEL_CFG.model_path}")
    print("="*65)


if __name__ == "__main__":
    main()