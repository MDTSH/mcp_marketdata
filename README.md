# mcp_marketdata

公开仓库：滚动 **90 个自然日** 的 MCP 市场数据，供 **MCP Python** 使用。

发布数据在 **[`market_data/`](market_data/README.md)**（GitHub 上的 **market_data 主目录**）。**仅同步** 本机 `Z:\market_data\snapshots`（JSON + HIST + 辅助表），**不会**拷贝父目录 `Z:\market_data` 下的 live / qh / 其它 dump。脚本在 `scripts/`，报告在 `reports/`。

主格式是一日一份的 **`MCP_MARKET_DATA_YYYYMMDD.json`**。`MRawMarketManager` / `MLiveMarketDataStore` / `MMarketDataJsonReader` 的 root 指 `market_data/`，详见 [`market_data/README.md`](market_data/README.md)（含数据分类：FX vol、收益率曲线、HIST、BOND_INFO、dividends 等）。

- 仓库：https://github.com/MDTSH/mcp_marketdata （Public）
- **不使用 Git LFS**（HIST / JSON 均按普通文件提交）
- 本机源目录：`Z:\market_data\snapshots`
- 本机克隆：`D:\work\mcp\github\mcp_marketdata`

## 源 → 发布

`Z:\market_data\snapshots` 里 **JSON、HIST、辅助 CSV 在同一层**。同步后写入本仓库的 `market_data/`，**保持相对路径不变**。

- `MCP_MARKET_DATA_YYYYMMDD.json` — 日主索引
- `price_data_index.*.hist_file` — 如 `BOND_PRICES_HIST.csv`
- 约定 sidecar：`BOND_INFO.csv`、`dividends.csv`、`INSTRUMENT_CLASSIFICATION.csv` 等

源端没有单独的 `hist/`，本仓库也不拆分 `hist/`，也不再使用 `snapshots/` 作为发布目录。

## 窗口规则

- 保留主索引：文件名日期 `YYYYMMDD >= 今天 - 90` 个自然日
- 解析窗口内 JSON 的路径字段，并额外复制源上存在的约定 sidecar
- HIST / 带 as-of 的辅助序列按行裁剪
- `BOND_INFO`、分类、INFO/费率/乘数整表复制；`dividends.csv` 整表复制
- GitHub.com 单文件上限 100MB。`BOND_PRICES_HIST.csv` 在 90 日之后仍可能超限，会再丢掉最旧行直到 &lt;99MB（见 `reports/SYNC_REPORT_*.md`）
- 窗口外的目标 JSON / 未再被引用的数据文件会被删除；**不会删除** `.git` 或 `market_data/README.md`
- 源上的 `current_file` 通常不存在，加载器回退到 `hist_file`

## 周六自动同步

计划任务名：`MCP_MarketData_WeeklySync`

- 每周六本地时间 **06:00**，以当前用户运行（任务为 **Interactive only**：开机且已登录才会跑）
- 自动执行：`prepare_sync.py` → `verify_window.py` → `git add` / `commit` / `push origin`
- **不会** `git push --force`、`--no-verify`、`commit --amend`，也不会改 git config
- 日志：`reports/weekly_sync.log`（已加入 `.gitignore`）
- 每次运行另写 `reports/SYNC_REPORT_YYYYMMDD.md`

若没有变更，跳过 commit / push。

### 停用计划任务

```bat
schtasks /End /TN MCP_MarketData_WeeklySync
schtasks /Change /TN MCP_MarketData_WeeklySync /DISABLE
```

重新启用：

```bat
schtasks /Change /TN MCP_MarketData_WeeklySync /ENABLE
```

删除任务：

```bat
schtasks /Delete /TN MCP_MarketData_WeeklySync /F
```

若创建任务时提示需要提升权限，在 **以管理员身份** 的命令提示符中执行：

```bat
schtasks /Create /TN "MCP_MarketData_WeeklySync" /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\work\mcp\github\mcp_marketdata\scripts\weekly_sync.ps1" /SC WEEKLY /D SAT /ST 06:00 /F
```

## 手工运行

在仓库根目录：

```bat
python scripts\prepare_sync.py --dry-run
python scripts\prepare_sync.py
python scripts\verify_window.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\weekly_sync.ps1
```

`weekly_sync.ps1` 会 push。若只要改本地、暂不上传，只跑 `prepare_sync.py` / `verify_window.py`。

| 参数 | 默认 | 说明 |
|---|---|---|
| `--source` | `Z:\market_data\snapshots` | 源快照目录（禁止传父目录 `Z:\market_data`） |
| `--dest` | `D:\work\mcp\github\mcp_marketdata` | 本仓库根；发布数据写入 `<dest>/market_data` |
| `--days` | `90` | 滚动自然日 |
| `--as-of` | 今天 | 窗口锚点 |
| `--dry-run` | 关 | 只报告，不写 `market_data/` |

`prepare_sync.py` **不会** 自己 `git push`。提交与推送只走 `weekly_sync.ps1`。

## 目录

```
market_data/        # GitHub market_data 主目录 = 仅 snapshots 源
  README.md         # MCP Python、JSON section 分类、相对路径
  MCP_MARKET_DATA_YYYYMMDD.json
  *_HIST.csv / BOND_INFO.csv / dividends.csv / …
reports/            # SYNC_REPORT_YYYYMMDD.md
scripts/
  prepare_sync.py
  verify_window.py
  weekly_sync.ps1
  README.md
README.md
.gitignore
```
