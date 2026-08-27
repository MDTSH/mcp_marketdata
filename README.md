# mcp_marketdata

面向 **MCP Python** 与 **Excel（RawMD / LiveStore）** 的可发布市场数据包。仓库公开滚动约 **90 个自然日** 的日终快照。

配合 [**Mathema MCP Excel**](https://github.com/MDTSH/mcp_excel) 使用；Manager / Store 指向本仓库 [`market_data/`](market_data/README.md)（不要指仓库根目录）。一日一份主索引：`MCP_MARKET_DATA_YYYYMMDD.json`。JSON 里的相对路径（`hist_file`、`current_file`、`file` 以及约定 sidecar 文件名）都相对 `market_data/` 解析。

- 仓库：https://github.com/MDTSH/mcp_marketdata
- Excel / Python 包：[Mathema MCP Excel](https://github.com/MDTSH/mcp_excel)
- 分类、字段与用法详见 [`market_data/README.md`](market_data/README.md)

## 快速开始

克隆后，用本机上的 `market_data` 绝对路径（或工作簿相对路径）作为数据根：

**MCP Python**

```python
import mcp

root = r".../mcp_marketdata/market_data"  # 改成你的克隆路径

mgr = mcp.MRawMarketManager(root)
yc = mgr.getYieldCurve("CNHDEPO", "20260826")
fxvol = mgr.getFXVolSurface("USDCNH_RVOL_BGN", "20260826")

store = mcp.MLiveMarketDataStore()
store.loadSnapshot(root + r"/MCP_MARKET_DATA_20260826.json")
```

**Excel RawMD / LiveStore**

```excel
=McpRawMarketManager(".../mcp_marketdata/market_data")
=rawmdGetYieldCurve2(A1, "CNHDEPO_2", "20260826")

=McpLiveMarketDataStore(".../mcp_marketdata/market_data/MCP_MARKET_DATA_20260826.json")
=mdlsGetFXVolSurface2(A1, "USDCNH_RVOL_BGN_2")
```

估值引擎可将 `raw_market_data_root` / `MCP_MARKET_DATA_ROOT` 指到同一 `market_data/` 目录。

## 主索引格式

每个交易日一个 JSON：

```text
MCP_MARKET_DATA_YYYYMMDD.json
```

顶层包含估值日、元数据，以及按 MCP 对象类型分组的数组 / 索引，例如：

| 顶层键 | 内容 |
|---|---|
| `valuation_date` | 估值日 `YYYYMMDD` |
| `_metadata` | 更新时间、版本、数据源 |
| `SwapCurve` / `YieldCurve` / `YieldCurve2` / `BondCurve` / `BondSpreadCurve` | 利率与债券曲线（内联） |
| `FXForwardPointsCurve` / `FXForwardPointsCurve2` | FX 远期点 |
| `FXVolSurface` / `FXVolSurface2` / `VolSurface` / `LocalVol` | FX / 权益 / 商品波动率 |
| `ForwardCurve` | 商品、贵金属远期 |
| `CreditCurve` / `HistVol` | 信用曲线、历史波动率节点（可为空数组） |
| `price_data_index` | 产品类型 → 同目录 HIST CSV |
| `instrument_classification_index` | 分类表路径 |
| `bond_clean_prices` / `ir_vol_curves` | 附属净价 / 利率波动率 |

曲线与曲面写在 JSON 内；行情序列、债券条款、分红等在同目录 sidecar CSV / JSON 中，由主索引或约定文件名引用。

## 数据包里有什么

| 类别 | 典型文件 / section |
|---|---|
| 日主索引 | `MCP_MARKET_DATA_YYYYMMDD.json` |
| FX vol / 远期点 | `FXVolSurface`、`FXVolSurface2`、`FXForwardPointsCurve(2)` |
| 收益率 / 互换 / 债券曲线 | `YieldCurve`、`YieldCurve2`、`SwapCurve`、`BondCurve`、`BondSpreadCurve` |
| 价格 HIST | `BOND_PRICES_HIST.csv`、`FX_SPOT_PRICES_HIST.csv`、`EQUITY_SPOT_PRICES_HIST.csv` 等 |
| 债券条款 | `BOND_INFO.csv`、`BOND_INFO.json`、`BOND_INFO_SPEC.csv` |
| 分红 / 分类 / 静态信息 | `dividends.csv`、`INSTRUMENT_CLASSIFICATION.csv`、`EQUITY_INFO.csv`、`FUND_INFO.csv`、`FUTURE_INFO.csv` |

完整 section 与 sidecar 列表见 [`market_data/README.md`](market_data/README.md)。

## 相对路径

```text
<repo>/market_data/MCP_MARKET_DATA_20260826.json
<repo>/market_data/BOND_PRICES_HIST.csv          ← price_data_index.BOND.hist_file
<repo>/market_data/INSTRUMENT_CLASSIFICATION.csv ← instrument_classification_index.file
<repo>/market_data/BOND_INFO.csv
<repo>/market_data/dividends.csv
```

JSON 与 HIST、辅助表在同一层。不要把数据拆到仓库根、`hist/` 或再套一层 `snapshots/`。

## 目录

```text
market_data/          # 数据根：指到这里
  README.md
  MCP_MARKET_DATA_YYYYMMDD.json
  *_HIST.csv
  BOND_INFO.csv / dividends.csv / …
README.md
```
