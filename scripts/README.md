# scripts（运维）

本目录只给发布方使用。最终客户只需克隆仓库并指向 `../market_data/`，见仓库根与 `market_data/README.md`。

| 文件 | 作用 |
|---|---|
| `prepare_sync.py` | 从 `Z:\market_data\snapshots` 复制 90 自然日窗口到 `../market_data`（JSON + HIST + BOND_INFO/dividends 等 sidecar），裁剪 HIST 行，写 `../reports/SYNC_REPORT_YYYYMMDD.md`。拒绝父目录 `Z:\market_data`。不执行 git push。 |
| `verify_window.py` | 断言目标 `market_data/` 无窗口外 JSON；`hist_file` 与非 `current_file` 的引用、以及源上存在的约定 sidecar 都必须在目标里。 |
| `weekly_sync.ps1` | prepare → verify → `git add market_data reports scripts …` / commit / `git push origin <当前分支>`。无变更则跳过提交。若仍存在 `snapshots/` 则拒绝，避免发布两棵树。 |

**仅同步** 本机 `Z:\market_data\snapshots`（JSON + HIST + 辅助表），**不会**拷贝父目录 `Z:\market_data` 下的 live / qh / 其它 dump。本机克隆：`D:\work\mcp\github\mcp_marketdata`。

## 源 → 发布

`Z:\market_data\snapshots` 里 JSON、HIST、辅助 CSV 在同一层。同步后写入本仓库的 `market_data/`，保持相对路径不变。源端没有单独的 `hist/`，本仓库也不拆分 `hist/`，也不再使用 `snapshots/` 作为发布目录。

## 窗口与体积

- 保留主索引：文件名日期 `YYYYMMDD >= 今天 - 90` 个自然日
- 解析窗口内 JSON 的路径字段，并额外复制源上存在的约定 sidecar
- HIST / 带 as-of 的辅助序列按行裁剪
- `BOND_INFO`、分类、INFO/费率/乘数整表复制；`dividends.csv` 整表复制（稀疏事件表，按 90 日裁会丢掉窗口外仍可能用到的除权记录）
- GitHub.com 单文件上限 100MB。`BOND_PRICES_HIST.csv` 在 90 日之后仍可能超限，会再丢掉最旧行直到 &lt;99MB（见 `reports/SYNC_REPORT_*.md`）
- 窗口外的目标 JSON / 未再被引用的数据文件会被删除；**不会删除** `.git` 或 `market_data/README.md`
- 源上的 `current_file` 通常不存在，加载器回退到 `hist_file`

## 参数

在仓库根目录：

```bat
python scripts\prepare_sync.py --dry-run
python scripts\prepare_sync.py
python scripts\verify_window.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\weekly_sync.ps1
```

`weekly_sync.ps1` 会 push。若只要改本地、暂不上传，只跑 `prepare_sync.py` / `verify_window.py`。`prepare_sync.py` **不会** 自己 `git push`。

| 参数 | 默认 | 说明 |
|---|---|---|
| `--source` | `Z:\market_data\snapshots` | 源快照目录（禁止传父目录 `Z:\market_data`） |
| `--dest` | `D:\work\mcp\github\mcp_marketdata` | 本仓库根；发布数据写入 `<dest>/market_data` |
| `--days` | `90` | 滚动自然日 |
| `--as-of` | 今天 | 窗口锚点 |
| `--dry-run` | 关 | 只报告，不写 `market_data/` |

```bat
python scripts\prepare_sync.py --dry-run --source Z:\market_data\snapshots --dest D:\work\mcp\github\mcp_marketdata --days 90
```

## 周六自动同步

计划任务名：`MCP_MarketData_WeeklySync`

- 每周六本地时间 **06:00**，以当前用户运行（任务为 **Interactive only**：开机且已登录才会跑）
- 自动执行：`prepare_sync.py` → `verify_window.py` → `git add` / `commit` / `push origin`
- **不会** `git push --force`、`--no-verify`、`commit --amend`，也不会改 git config
- 日志：`reports/weekly_sync.log`（已加入 `.gitignore`）
- 每次运行另写 `reports/SYNC_REPORT_YYYYMMDD.md`

若没有变更，跳过 commit / push。

停用：

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
