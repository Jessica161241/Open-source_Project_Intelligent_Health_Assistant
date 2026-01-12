import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
IN_PATH = BASE_DIR / "data" / "processed" / "repo_metrics.parquet"
OUT_PATH = BASE_DIR / "data" / "processed" / "repo_health.parquet"


def safe_div(a, b):
    return a / b if b > 0 else 0


def normalize(series: pd.Series):
    return (series - series.min()) / (series.max() - series.min() + 1e-9)


if __name__ == "__main__":
    print("Computing repo health score...")

    df = pd.read_parquet(IN_PATH)

    # 生命周期（天）
    df["lifetime_days"] = (
        (df["last_event"] - df["first_event"])
        .dt.days
        .clip(lower=1)
    )

    # 五个基础指标
    df["activity_score"] = df["active_days"] / df["lifetime_days"]
    df["collab_score"] = normalize(df["unique_actors"])

    df["issue_score"] = df.apply(
        lambda r: safe_div(r["issue_closed_count"], r["issue_count"]),
        axis=1
    )

    df["pr_score"] = df.apply(
        lambda r: safe_div(r["pr_merged_count"], r["pr_count"]),
        axis=1
    )

    df["popularity_score"] = normalize(
        np.log1p(df["stargazers"] + df["forks"])
    )

    # 初始权重（之后会用 top300 校准）
    weights = {
        "activity_score": 0.25,
        "collab_score": 0.20,
        "issue_score": 0.20,
        "pr_score": 0.20,
        "popularity_score": 0.15,
    }

    df["health_score"] = sum(
        df[k] * w for k, w in weights.items()
    )

    df["health_score"] = (df["health_score"] * 100).round(2)

    df[
        [
            "repo_name",
            "repo_language",
            "health_score",
            "activity_score",
            "collab_score",
            "issue_score",
            "pr_score",
            "popularity_score",
            "stargazers",
            "forks",
        ]
    ].to_parquet(OUT_PATH, index=False)

    print(f"Saved repo health scores: {df.shape}")
