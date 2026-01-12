import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ------------------------------
# 1. 设置项目目录和数据路径
# ------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]  # 回到项目根目录
PROCESSED_DIR = BASE_DIR / "data" / "processed"
ANALYSIS_DIR = BASE_DIR / "data" / "analysis"

# 数据文件
HEALTH_RAW   = PROCESSED_DIR / "repo_health.parquet"
HEALTH_CALIB = ANALYSIS_DIR / "repo_health_calibrated.parquet"
TOP300_LIST  = ANALYSIS_DIR / "top300_repo_list.parquet"

# ------------------------------
# 2. 加载数据
# ------------------------------
print("Loading raw health data...")
health_df = pd.read_parquet(HEALTH_RAW)

print("Loading calibrated health data...")
health_calib_df = pd.read_parquet(HEALTH_CALIB)

print("Loading Top300 repo list...")
top300_df = pd.read_parquet(TOP300_LIST)

# 给健康度数据打上是否属于 Top300 的标签
health_calib_df["is_top300"] = health_calib_df["repo_name"].isin(top300_df["repo_name"])

# ------------------------------
# 3. 基本统计
# ------------------------------
print("\nHealth score statistics (calibrated):")
desc = health_calib_df.groupby("is_top300")["health_score"].describe()
# 保留 count, mean, 50% (median), 75% (p75), 90% 分位数
for col in ["count", "mean", "50%", "75%", "90%"]:
    if col not in desc.columns:
        if col == "50%":
            desc["50%"] = health_calib_df.groupby("is_top300")["health_score"].median()
        elif col == "75%":
            desc["75%"] = health_calib_df.groupby("is_top300")["health_score"].quantile(0.75)
        elif col == "90%":
            desc["90%"] = health_calib_df.groupby("is_top300")["health_score"].quantile(0.90)
print(desc[["count", "mean", "50%", "75%", "90%"]])

# ------------------------------
# 4. 可视化 Top300 vs Others 健康度分布
# ------------------------------
plt.figure(figsize=(10,6))
sns.histplot(
    data=health_calib_df,
    x="health_score",
    hue="is_top300",
    bins=50,
    kde=True,
    palette={True:"orange", False:"blue"},
    alpha=0.6
)
plt.title("Health Score Distribution (Top300 vs Others)")
plt.xlabel("Health Score")
plt.ylabel("Count")
plt.legend(["Others","Top300"])
plt.tight_layout()
plt.show()

