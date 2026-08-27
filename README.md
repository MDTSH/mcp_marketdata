# mcp_marketdata

公开仓库：滚动 **90 个自然日** 的 MCP 市场数据快照（JSON + 被引用的 HIST CSV）。

- 仓库：https://github.com/MDTSH/mcp_marketdata （Public）
- **不使用 Git LFS**（HIST / JSON 均按普通文件提交）
- 本机源目录：`Z:\market_data\snapshots`
- 本机克隆：`D:\work\mcp\github\mcp_marketdata`

## 源数据布局

`Z:\market_data\snapshots` 里 **JSON 与 HIST 在同一目录**：

- `MCP_MARKET_DATA_YYYYMMDD.json` — 日主索引
- `price_data_index.*.hist_file` / `current_file` — 相对文件名，例如 `BOND_PRICES_HIST.csv`
- `instrument_classification_index.file` — `INSTRUMENT_CLASSIFICATION.csv`

同步后写入本仓库的 `snapshots/`，**保持相对路径不变**，RawMD / LiveStore 仍按「主索引所在目录 + 相对文件名」解析。

源端没有单独的 `hist/` 目录，因此本仓库也不拆分 `hist/`。

## 窗口规则

- 保留主索引：文件名日期 `YYYYMMDD >= 今天 - 90` 个自然日（不是自然月）
- 解析窗口内 JSON 的 HIST / current 引用，只复制这些文件
- HIST CSV 按行裁剪：日期列（多为 `valuation_date`）早于窗口起点的行删除
- 日期解析与 `raw_market_data_loader.py` 的 `YYYYMMDD` / `YYYY-MM-DD` / `YYYY/M/D` 一致，并额外识别源 HIST 实际使用的 `M/D/YYYY`
- GitHub.com 单文件上限 100MB，且本仓库不用 LFS。若某份 HIST 在 90 日裁剪后仍 ≥100MB，会再丢掉该文件最旧的行，直到 <99MB（报告里会写实际起始日）。当前主要是 `BOND_PRICES_HIST.csv`
- 窗口外的目标 JSON / 未再被引用的 HIST 会被删除；**不会删除 `.git`**
- 源上的 `current_file`（如 `BOND_PRICES.csv`）目前通常不存在，加载器会回退到 `hist_file`；校验只把缺失的 **hist_file** 视为失败

## 周六自动同步

计划任务名：`MCP_MarketData_WeeklySync`

- 每周六本地时间 **06:00**，以当前用户运行（任务为 **Interactive only**：开机且已登录才会跑；若要未登录也跑，需在任务计划程序里改成“不管用户是否登录”并输入 Windows 密码）
- 自动执行：`prepare_sync.py` → `verify_window.py` → `git add` / `commit` / `push origin`（当前分支，一般为 `main`）
- **不会** `git push --force`、`--no-verify`、`commit --amend`，也不会改 git config
- 使用本机已有 Git 凭据（`credential.helper=store`），脚本不保存密钥
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

常用参数：

| 参数 | 默认 | 说明 |
|---|---|---|
| `--source` | `Z:\market_data\snapshots` | 源快照目录 |
| `--dest` | `D:\work\mcp\github\mcp_marketdata` | 本仓库根 |
| `--days` | `90` | 滚动自然日 |
| `--as-of` | 今天 | 窗口锚点 |
| `--dry-run` | 关 | 只报告，不写 `snapshots/` |

`prepare_sync.py` **不会** 自己 `git push`。提交与推送只走 `weekly_sync.ps1`。

源目录不可读或 `git push` 失败时，脚本会以非零退出码结束，并写入 `reports/weekly_sync.log`。

## 目录

```
snapshots/          # 窗口内 JSON + 引用到的 HIST/分类 CSV
reports/            # SYNC_REPORT_YYYYMMDD.md
scripts/
  prepare_sync.py
  verify_window.py
  weekly_sync.ps1
  README.md
README.md
.gitignore
```
