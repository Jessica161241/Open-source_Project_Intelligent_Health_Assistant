import pandas as pd
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed" / "events_clean"
OUT_PATH = PROCESSED_DIR / "repo_metrics.parquet"

# 👉 只读必要列（极大提速 + 降内存）
NEEDED_COLS = [
    "repo_name",
    "type",
    "created_at",
    "actor_login",
    "issue_closed_at",
    "pull_merged_at",
    "repo_language",
    "repo_stargazers_count",
    "repo_forks_count",
]


def iter_event_parts(processed_dir: Path, max_files=10):
    parts = sorted(processed_dir.glob("events_part_*.parquet"))
    if not parts:
        raise FileNotFoundError("No events_part_*.parquet found.")

    for i, p in enumerate(parts):
        if i >= max_files:
            break
        yield p


def update_metrics(metrics, df: pd.DataFrame):
    df["event_date"] = df["created_at"].dt.date

    grouped = df.groupby("repo_name")

    for repo, g in grouped:
        m = metrics[repo]

        m["total_events"] += len(g)
        m["active_days"].update(g["event_date"].dropna().unique())
        m["unique_actors"].update(g["actor_login"].dropna().unique())

        m["first_event"] = min(m["first_event"], g["created_at"].min())
        m["last_event"] = max(m["last_event"], g["created_at"].max())

        m["issue_count"] += (g["type"] == "IssuesEvent").sum()
        m["pr_count"] += (g["type"] == "PullRequestEvent").sum()
        m["issue_closed_count"] += g["issue_closed_at"].notna().sum()
        m["pr_merged_count"] += g["pull_merged_at"].notna().sum()

        # ⚠️ 修复 NA 布尔判断错误
        lang = g["repo_language"].dropna()
        if m["repo_language"] is None and not lang.empty:
            m["repo_language"] = lang.iloc[0]

        m["stargazers"] = max(m["stargazers"], g["repo_stargazers_count"].max())
        m["forks"] = max(m["forks"], g["repo_forks_count"].max())


def finalize_metrics(metrics):
    rows = []

    for repo, m in metrics.items():
        pr_count = m["pr_count"]
        pr_merged = m["pr_merged_count"]

        rows.append({
            "repo_name": repo,
            "total_events": m["total_events"],
            "active_days": len(m["active_days"]),
            "unique_actors": len(m["unique_actors"]),
            "first_event": m["first_event"],
            "last_event": m["last_event"],
            "issue_count": m["issue_count"],
            "issue_closed_count": m["issue_closed_count"],
            "pr_count": pr_count,
            "pr_merged_count": pr_merged,
            "pr_merge_rate": pr_merged / pr_count if pr_count > 0 else 0,
            "repo_language": m["repo_language"],
            "stargazers": m["stargazers"],
            "forks": m["forks"],
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("Streaming repo metrics computation...")

    metrics = defaultdict(lambda: {
        "total_events": 0,
        "active_days": set(),
        "unique_actors": set(),
        "first_event": pd.Timestamp.max,
        "last_event": pd.Timestamp.min,
        "issue_count": 0,
        "issue_closed_count": 0,
        "pr_count": 0,
        "pr_merged_count": 0,
        "repo_language": None,
        "stargazers": 0,
        "forks": 0,
    })

    for p in iter_event_parts(PROCESSED_DIR, max_files=10):
        print(f"Processing {p.name}")
        df = pd.read_parquet(p, columns=NEEDED_COLS)
        update_metrics(metrics, df)
        del df  # 立刻释放内存

    repo_metrics = finalize_metrics(metrics)
    repo_metrics.to_parquet(OUT_PATH)

    print(f"Saved repo metrics: {repo_metrics.shape}")
