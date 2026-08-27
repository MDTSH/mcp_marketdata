# scripts

| 文件 | 作用 |
|---|---|
| `prepare_sync.py` | 从 `Z:\market_data\snapshots` 复制 90 自然日窗口到 `../snapshots`（JSON + HIST + BOND_INFO/dividends 等 sidecar），裁剪 HIST 行，写 `../reports/SYNC_REPORT_YYYYMMDD.md`。不执行 git push。 |
| `verify_window.py` | 断言目标 `snapshots/` 无窗口外 JSON；`hist_file` 与非 `current_file` 的引用、以及源上存在的约定 sidecar 都必须在目标里。 |
| `weekly_sync.ps1` | prepare → verify → `git add` / commit / `git push origin <当前分支>`。无变更则跳过提交。 |

## dry-run

```bat
python prepare_sync.py --dry-run
```

在仓库根目录则：

```bat
python scripts\prepare_sync.py --dry-run --source Z:\market_data\snapshots --dest D:\work\mcp\github\mcp_marketdata --days 90
```

## 周六任务

由计划任务 `MCP_MarketData_WeeklySync` 调用本目录下的 `weekly_sync.ps1`。停用方法见上级 `README.md`。
