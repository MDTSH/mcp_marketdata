# snapshots/

本目录就是 GitHub 仓库 [MDTSH/mcp_marketdata](https://github.com/MDTSH/mcp_marketdata) 对外发布的**数据树**（`snapshots/`），不是另一套根目录。

RawMD / LiveStore 的根目录 = **本文件夹**。JSON 里的相对路径（`hist_file`、`file`、`BOND_INFO.csv` 等）都相对这里解析。源端 `Z:\market_data\snapshots` 也是 JSON + HIST + 辅助表同一层，没有单独的 `hist/`。

This folder **is** the published GitHub `snapshots/` window. Relative paths resolve against this directory.

## 文件类型

| 类型 | 示例 | 说明 |
|---|---|---|
| 日主索引 | `MCP_MARKET_DATA_YYYYMMDD.json` | 窗口内每个估值日一份 |
| 价格 HIST | `BOND_PRICES_HIST.csv`、`EQUITY_SPOT_PRICES_HIST.csv` | `price_data_index.*.hist_file` |
| 债券条款 | `BOND_INFO.csv`、`BOND_INFO.json`、`BOND_INFO_SPEC.csv` | 静态参考表，整表发布 |
| 分红 | `dividends.csv` | `fund_code,ex_date,dividend_per_share`；事件表整表发布 |
| 分类 | `INSTRUMENT_CLASSIFICATION.csv` | `instrument_classification_index.file` |
| 其它辅助 | `EQUITY_INFO.csv`、`FUND_INFO.csv`、`FUTURE_INFO.csv`、`future_multipliers.csv`、`instrument_fees.csv`、`IR_INDEX_FIXINGS_HIST.csv`、`INSTRUMENT_VOLATILITY.csv` 等 | 加载器按文件名在本目录查找；JSON 通常不写路径 |

`current_file`（如 `BOND_PRICES.csv`）源端通常不存在，加载器回退到对应 `hist_file`。

## 窗口与体积

- 主索引：文件名日期 ≥ 今天 − **90** 个自然日。
- `*_HIST*.csv`：按日期列裁到窗口；`BOND_PRICES_HIST.csv` 在 90 日之后仍可能 ≥100MB，会再丢掉最旧行直到 &lt;99MB（**不用 Git LFS**）。此时债券 HIST 实际起始日可能晚于窗口起点，见 `reports/SYNC_REPORT_*.md`。
- 参考表（`BOND_INFO*`、分类、INFO/费率/乘数）整表复制。`BOND_INFO` 虽有 `maturity_date`，那是条款字段，不是行情时间序列。
- `dividends.csv` 有 `ex_date`，但是稀疏事件表；按 90 日裁会裁掉窗口外仍可能用到的除权记录（源上多为上一日历年），因此整表发布。
- 有明确 as-of 列的辅助序列（如 `INSTRUMENT_VOLATILITY.csv` 的 `asof_date`）按 90 日裁剪。

## 相对路径

```
<snapshots>/MCP_MARKET_DATA_20260826.json
<snapshots>/BOND_PRICES_HIST.csv          ← hist_file
<snapshots>/INSTRUMENT_CLASSIFICATION.csv ← instrument_classification_index.file
<snapshots>/BOND_INFO.csv                 ← 约定文件名 / scenario_config.bond_info
<snapshots>/dividends.csv                 ← 约定文件名
```

不要把数据再拆到仓库根或 `hist/`。周六任务从 `Z:\market_data\snapshots` 同步到这里，见仓库根 `README.md`。
