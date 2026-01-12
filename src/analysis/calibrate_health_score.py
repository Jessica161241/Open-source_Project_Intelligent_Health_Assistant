import pandas as pd
from pathlib import Path

# 路径
BASE_DIR = Path(__file__).resolve().parents[2]
HEALTH_PATH = BASE_DIR / "data" / "processed" / "repo_health.parquet"
TOP300_PATH = BASE_DIR / "data" / "analysis" / "top300_repo_list.parquet"
OUT_PATH = BASE_DIR / "data" / "analysis" / "repo_health_calibrated.parquet"

# 配置
TARGET_MEAN = 80.0
MAX_ACTIVITY_WEIGHT = 0.4  # 活跃度最大权重
DIMENSIONS = ["activity_score", "collab_score", "issue_score", "pr_score", "popularity_score"]

def main():
    print("Loading repo health data...")
    health_df = pd.read_parquet(HEALTH_PATH)
    print(f"Total repos loaded: {len(health_df)}")

    print("Loading Top300 repo list...")
    top300_df = pd.read_parquet(TOP300_PATH)
    print(f"Top300 repos loaded: {len(top300_df)}")

    # 匹配Top300
    top_df = health_df[health_df["repo_name"].isin(top300_df["repo_name"])]
    print(f"Matched Top300 repos: {len(top_df)}\n")

    # 当前Top300各维度均值
    dim_means = {d: top_df[d].mean() for d in DIMENSIONS}
    print("Top300 dimension means:")
    for d, val in dim_means.items():
        print(f"  {d:20}: {val:.4f}")

    # 计算初始权重（按均值比例）
    total_mean = sum(dim_means.values())
    weights = {d: dim_means[d] / total_mean for d in DIMENSIONS}

    # 限制活跃度权重
    if weights["activity_score"] > MAX_ACTIVITY_WEIGHT:
        excess = weights["activity_score"] - MAX_ACTIVITY_WEIGHT
        weights["activity_score"] = MAX_ACTIVITY_WEIGHT
        # 按比例分配给其他四个维度
        other_dims = [d for d in DIMENSIONS if d != "activity_score"]
        total_other = sum(weights[d] for d in other_dims)
        for d in other_dims:
            weights[d] += weights[d] / total_other * excess

    # 动态微调：循环缩放，直到Top300平均健康度接近TARGET_MEAN
    calibrated_scores = sum(top_df[d] * weights[d] for d in DIMENSIONS)
    current_mean = calibrated_scores.mean()
    scale_factor = TARGET_MEAN / current_mean

    # 应用缩放系数到所有维度
    calibrated_df = health_df.copy()
    calibrated_df["health_score"] = sum(calibrated_df[d]*weights[d] for d in DIMENSIONS) * scale_factor

    # 输出
    print("\nCalibrated weights (scaled):")
    for d in DIMENSIONS:
        print(f"  {d:20}: {weights[d]*scale_factor:.3f}")
    print(f"\nTop300 mean health score (after calibration): {calibrated_df[calibrated_df['repo_name'].isin(top300_df['repo_name'])]['health_score'].mean():.2f}")

    # 保存
    calibrated_df.to_parquet(OUT_PATH)
    print(f"\nSaved calibrated health scores to:\n{OUT_PATH}")

if __name__ == "__main__":
    main()
