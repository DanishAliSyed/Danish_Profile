"""Reproduce this portfolio case study on the original public UCI dataset."""
import argparse
import io
import urllib.request
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
KIND = "credit-default"
CONFIG = {
    "credit-default": (
        "https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip",
        "default of credit card clients.xls",
        "Credit Card Default | Risk Model Evaluation",
        "default payment next month",
        ["LIMIT_BAL", "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
        + [f"{prefix}{i}" for prefix in ("BILL_AMT", "PAY_AMT") for i in range(1, 7)],
    ),
}


def load(path):
    url, filename, *_ = CONFIG[KIND]
    if path:
        raw = Path(path).read_bytes()
    else:
        with urllib.request.urlopen(url, timeout=45) as response:
            with zipfile.ZipFile(io.BytesIO(response.read())) as archive:
                raw = archive.read(filename)
    if filename.endswith(".xls"):
        df = pd.read_excel(io.BytesIO(raw), header=1, engine="xlrd")
    else:
        df = pd.read_csv(io.BytesIO(raw))
    df.columns = [" ".join(str(c).split()) for c in df.columns]
    return df


def evaluate(df):
    _, _, _, target, features = CONFIG[KIND]
    x, y = df[features], df[target].astype(int)
    assert not x.isna().any().any() and set(y.unique()) == {0, 1}
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.30, random_state=42, stratify=y
    )
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    model.fit(x_train, y_train)
    p = model.predict_proba(x_test)[:, 1]
    observed = y_test.to_numpy()
    ranked = np.argsort(-p, kind="stable")
    baseline = float(y_train.mean())
    scores = {
        "rows": len(df), "train_rows": len(y_train), "test_rows": len(observed),
        "test_events": int(observed.sum()), "test_event_rate": float(observed.mean()),
        "roc_auc": roc_auc_score(observed, p), "average_precision": average_precision_score(observed, p),
        "brier": brier_score_loss(observed, p),
        "baseline_brier": brier_score_loss(observed, np.full(len(observed), baseline)),
    }
    capacity = len(observed) // 10
    capacity_events = int(observed[ranked[:capacity]].sum())
    scores.update(top10_capacity=capacity, top10_events=capacity_events,
                  top10_event_capture=capacity_events / int(observed.sum()),
                  top10_event_rate=capacity_events / capacity)
    deciles = []
    for i, positions in enumerate(np.array_split(ranked, 10), 1):
        deciles.append({"risk_band": i, "records": len(positions),
                        "events": int(observed[positions].sum()),
                        "mean_prediction": float(p[positions].mean()),
                        "observed_rate": float(observed[positions].mean())})
    assert sum(r["records"] for r in deciles) == len(observed)
    assert sum(r["events"] for r in deciles) == int(observed.sum())
    return scores, pd.DataFrame(deciles)


def draw(metrics, bands):
    title = CONFIG[KIND][2]
    events = metrics["test_events"]
    observed = bands["observed_rate"].to_numpy() * 100
    predicted = bands["mean_prediction"].to_numpy() * 100
    fig = plt.figure(figsize=(11, 6.2), facecolor="#edf4f7")
    fig.text(.05, .92, title, fontsize=23, color="#142f43", weight="bold")
    fig.text(.05, .862, f"Held-out test set: {metrics['test_rows']:,} records • {events:,} outcomes • highest risk first",
             fontsize=12, color="#47657a")
    ax = fig.add_axes([.10, .22, .84, .54], facecolor="white")
    x = np.arange(1, 11)
    ax.bar(x, observed, .62, color="#177e74", label="Observed event rate")
    ax.plot(x, predicted, "o-", color="#be6346", label="Mean predicted probability", linewidth=2)
    ax.axhline(metrics["test_event_rate"] * 100, color="#557084", linestyle="--",
               label="Overall test event rate")
    ax.set(xticks=x, xlabel="Equal-count risk band (1 = highest risk)", ylabel="Percent")
    ax.legend(loc="upper right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(.05, .085, f"ROC AUC  {metrics['roc_auc']:.3f}   |   Average precision  {metrics['average_precision']:.3f}"
             f"   |   Brier score  {metrics['brier']:.3f}", fontsize=13, color="#142f43", weight="bold")
    fig.text(.05, .044, "Danish Syed  /  Public UCI benchmark  /  Educational case study", fontsize=10, color="#47657a")
    fig.savefig(ROOT / "dashboard.png", dpi=125, facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("--input", help="Optional path to the extracted UCI CSV or XLS")
    metrics, bands = evaluate(load(arg.parse_args().input))
    pd.DataFrame([metrics]).to_csv(ROOT / "metrics.csv", index=False, float_format="%.6f")
    bands.to_csv(ROOT / "risk_bands.csv", index=False, float_format="%.6f")
    draw(metrics, bands)
    print(metrics)
    print(bands.head(2).to_string(index=False))


if __name__ == "__main__":
    main()
