import pandas as pd
from pathlib import Path

# ================== 路径配置 ==================
BASE_DIR = Path(__file__).resolve().parents[2]

RAW_TOP300_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "top300_20_23_1681699961594.txt"
)

OUT_DIR = BASE_DIR / "data" / "analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_PATH = OUT_DIR / "top300_repo_list.parquet"


# ================== 主逻辑 ==================
def extract_top300_repos(
    path: Path,
    chunksize: int = 200_000
):
    """
    从 Top300 事件日志中，流式提取唯一 repo_name
    """
    repo_set = set()
    total_rows = 0

    print("Extracting Top300 repo names...")

    for chunk in pd.read_csv(
        path,
        usecols=["repo_name"],
        chunksize=chunksize,
        low_memory=True
    ):
        total_rows += len(chunk)

        # 去空 + 去重
        names = chunk["repo_name"].dropna().unique()
        repo_set.update(names)

        print(
            f"Processed rows: {total_rows:,} | "
            f"Unique repos: {len(repo_set)}"
        )

    return sorted(repo_set)


# ================== 入口 ==================
if __name__ == "__main__":
    repos = extract_top300_repos(RAW_TOP300_PATH)

    df = pd.DataFrame({
        "repo_name": repos,
        "is_top300": 1
    })

    df.to_parquet(OUT_PATH)

    print("=" * 50)
    print(f"Saved Top300 repo list: {OUT_PATH}")
    print(f"Total Top300 repos: {len(df)}")
