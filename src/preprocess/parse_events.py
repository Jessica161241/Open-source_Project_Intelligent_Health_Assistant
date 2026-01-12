import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_PATH = BASE_DIR / "data" / "raw" / "log_2020_01_1681619256789.txt"
OUT_DIR = BASE_DIR / "data" / "processed" / "events_clean"

OUT_DIR.mkdir(parents=True, exist_ok=True)

USE_COLS = [
    "repo_name",
    "type",
    "actor_login",
    "created_at",
    "issue_created_at",
    "issue_closed_at",
    "pull_merged_at",
    "repo_stargazers_count",
    "repo_forks_count",
    "repo_language",
    "repo_created_at"
]

TIME_COLS = [
    "created_at",
    "issue_created_at",
    "issue_closed_at",
    "pull_merged_at",
    "repo_created_at"
]


def load_and_clean_events_chunked(path: Path, chunksize=200_000):
    for i, chunk in enumerate(
        pd.read_csv(
            path,
            usecols=USE_COLS,
            chunksize=chunksize,
            low_memory=True
        )
    ):
        # 时间列转换
        for col in TIME_COLS:
            chunk[col] = pd.to_datetime(chunk[col], errors="coerce")

        # 去掉 repo_name 为空
        chunk = chunk.dropna(subset=["repo_name"])

        for col in [
            "repo_name",
            "type",
            "actor_login",
            "repo_language"
        ]:
            chunk[col] = chunk[col].astype("string")

        # 每个 chunk 单独写一个 parquet
        out_file = OUT_DIR / f"events_part_{i:03d}.parquet"
        chunk.to_parquet(out_file, engine="pyarrow", index=False)

        print(f"Saved {out_file.name}: {len(chunk)} rows")


if __name__ == "__main__":
    load_and_clean_events_chunked(RAW_PATH)
    print("All chunks processed successfully.")
