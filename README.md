OpenHealth 项目说明

---

## 项目结构

```
OpenHealth/
├─ data/                     # 原始数据与处理后数据
│  ├─ raw/                   # 原始日志数据
│  │  ├─ log_2020_01_1681619256789.txt
│  │  └─ top300_20_23_1681699961594.txt
│  ├─ processed/             # 清洗和处理后的数据
│  │  ├─ events_clean/       # 分块清洗后的事件数据
│  │  ├─ repo_health.parquet
│  │  └─ repo_metrics.parquet
│  └─ analysis/              # 校准和分析后的数据
│     ├─ repo_health_calibrated.parquet
│     └─ top300_repo_list.parquet
│
├─ src/                      # 代码主目录
│  ├─ preprocess/            # 数据预处理
│  │  └─ parse_events.py     # 将原始日志解析为标准化事件表
│  ├─ features/              # 特征计算与健康度公式
│  │  ├─ repo_metrics.py     # 仓库指标计算
│  │  └─ health_score.py     # 健康度分数计算公式
│  ├─ analysis/              # 分析与可视化
│  │  ├─ calibrate_health_score.py  # Top300 校准权重
│  │  ├─ extract_top300_repos.py    # 提取 Top300 仓库列表
│  │  └─ visualization.py           # 雷达图、直方图等可视化
├─ static/                # 静态资源
│     └─ main.js              
├─ index.html                # 前端网页入口
├─ app.py                    # Flask 后端程序
└─ README.md                 # 项目说明文档
```

---

## 环境依赖

使用 Python 3.10+，推荐使用虚拟环境（venv）。

必需库：

```bash
pip install flask pandas pyarrow matplotlib seaborn requests
```

MaxKB AI 小助手需要运行本地 MaxKB 并获取 API 地址与 Key。

---

## 项目运行方式

1. **准备数据**

   将原始日志文件放入 `data/raw/`，确保以下文件存在：

   * `log_2020_01_1681619256789.txt`
   * `top300_20_23_1681699961594.txt`

2. **数据预处理**

   ```bash
   python src/preprocess/parse_events.py
   ```

   生成 `data/processed/events_clean/` 分块清洗后的事件数据。

3. **特征计算与健康度公式**

   ```bash
   python src/features/repo_metrics.py
   python src/features/health_score.py
   ```

   生成 `repo_metrics.parquet` 和 `repo_health.parquet`。

4. **校准健康度公式**

   ```bash
   python src/analysis/extract_top300_repos.py
   python src/analysis/calibrate_health_score.py
   ```

   生成 `repo_health_calibrated.parquet`，Top300 仓库平均健康度接近目标值 80。

5. **运行 Flask 后端**

   ```bash
   python src/static/app.py
   ```

   默认访问地址：[http://127.0.0.1:5000](http://127.0.0.1:5000)

6. **网页访问与可视化**

   * 打开浏览器访问 `http://127.0.0.1:5000`
   * 输入仓库地址，页面将展示：

     * 仓库健康雷达图
     * AI 小助手建议
     * 综合健康分数和各维度分数

---

## 注意事项

* 由于数据集过大，需先从data.txt的网盘链接中下载文件，并添加到目标目录还原结构，再运行程序。
* MaxKB AI 小助手需确保本地服务已启动，并在 `app.py` 中配置 API 地址与 Key。
* 数据路径需与项目结构保持一致，否则无法加载数据。
* 若要更新指标或重新计算健康度，可重新运行特征计算和校准脚本。


