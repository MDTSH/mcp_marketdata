# market_data/

本目录是 [MDTSH/mcp_marketdata](https://github.com/MDTSH/mcp_marketdata) 发布的 **市场数据根目录**。

MCP Python 与 Excel RawMD 的 **root** = **本文件夹**。主索引文件名：`MCP_MARKET_DATA_YYYYMMDD.json`（例如 `MCP_MARKET_DATA_20260826.json`）。JSON 内的相对路径（`hist_file`、`current_file`、`file`、约定 sidecar 文件名）都相对这里解析。

数据包覆盖滚动约 **90 个自然日** 的日终快照。加载器读原始报价（利率、远期点、波动率、HIST 价格），再 Bootstrap / 插值成 MCP 对象。

## 指向本目录

| 入口 | 用法 | 何时用 |
|---|---|---|
| **RawMD** `MRawMarketManager` / Excel `McpRawMarketManager` | `setRoot(<本目录>)`，再按 `curve_id` + `valuation_date` 取对象 | 目录模式：按估值日打开对应主索引 |
| **JsonReader** `MMarketDataJsonReader` / Excel `McpMarketDataJsonReader` | `loadFromFile(.../MCP_MARKET_DATA_YYYYMMDD.json)` | 单文件只读 |
| **LiveStore** `MLiveMarketDataStore` / Excel `McpLiveMarketDataStore` | `loadSnapshot(同一 JSON)`，之后可 `applyUpdate` | 全量快照 + 增量 patch |

### MCP Python

```python
import mcp

root = r".../mcp_marketdata/market_data"  # 改成你的克隆路径

mgr = mcp.MRawMarketManager(root)
yc = mgr.getYieldCurve("CNHDEPO", "20260826")
fxvol = mgr.getFXVolSurface("USDCNH_RVOL_BGN", "20260826")
px = mgr.getPrice("000300", "EQUITYSPOT", "20260826")

reader = mcp.MMarketDataJsonReader()
reader.loadFromFile(root + r"/MCP_MARKET_DATA_20260826.json")
swap = reader.getSwapCurve("CNY_SWAP_FR007_BGN")

store = mcp.MLiveMarketDataStore()
store.loadSnapshot(root + r"/MCP_MARKET_DATA_20260826.json")
fxvol2 = store.getFXVolSurface2("USDCNH_RVOL_BGN_2")
```

估值引擎可将 `raw_market_data_root` / `MCP_MARKET_DATA_ROOT` 指到本目录。

### Excel RawMD / LiveStore

```excel
=McpRawMarketManager(".../mcp_marketdata/market_data")
=rawmdGetYieldCurve2(A1, "CNHDEPO_2", "20260826")
=rawmdGetFXVolSurface2(A1, "USDCNH_RVOL_BGN_2", "20260826")
=rawmdAvailableDates(A1)

=McpLiveMarketDataStore(".../mcp_marketdata/market_data/MCP_MARKET_DATA_20260826.json")
=mdlsGetFXVolSurface2(B1, "USDCNH_RVOL_BGN_2")
=mdlsGetSwapCurve(B1, "CNY_SWAP_FR007_BGN")
```

也可用 `McpResolvePath("market_data")` 把相对工作簿的路径解析成绝对路径。取到曲线 / 曲面对象后，再用 `YieldCurve2ZeroRate`、`FXVolSurface2GetVolatility` 等已有 UDF 读数。函数说明见 [Raw Market Data](https://help.mathema.com.cn/zh/latest/api/rawmarketdata.html)。

### 对象链

主索引 JSON（内联曲线/曲面 + `price_data_index` 指向同目录 HIST / 辅助 CSV）→ `MRawMarketManager` / `MMarketDataJsonReader` / `MLiveMarketDataStore` → `MYieldCurve` / `MYieldCurve2` / `MSwapCurve` / `MBondCurve` / `MFXForwardPointsCurve(2)` / `MFXVolSurface(2)` / `MVolSurface` / `MLocalVol` 等。`MLiveMarketDataStore` 的 `get*` 指针在 `applyUpdate` 后保持不变（原地换芯）。

## `MCP_MARKET_DATA_YYYYMMDD.json`

每个估值日一个文件。顶层结构：

```json
{
  "valuation_date": "20260826",
  "_metadata": {
    "data_update_time": "2026-08-27T08:31:04+08:00",
    "market_data_version": "20260311.001",
    "data_source": "Sample"
  },
  "SwapCurve": [ { "curve_id": "...", "CalibrationSet": { } } ],
  "YieldCurve": [ ],
  "YieldCurve2": [ ],
  "BondCurve": [ ],
  "BondSpreadCurve": [ ],
  "CreditCurve": [ ],
  "FXForwardPointsCurve": [ ],
  "FXForwardPointsCurve2": [ ],
  "ForwardCurve": [ ],
  "VolSurface": [ ],
  "FXVolSurface": [ ],
  "FXVolSurface2": [ ],
  "LocalVol": [ ],
  "HistVol": [ ],
  "price_data_index": {
    "BOND": {
      "hist_file": "BOND_PRICES_HIST.csv",
      "current_file": "BOND_PRICES.csv",
      "date_column": "valuation_date"
    }
  },
  "instrument_classification_index": { "file": "INSTRUMENT_CLASSIFICATION.csv" },
  "bond_clean_prices": { },
  "ir_vol_curves": { }
}
```

未使用的类型可以是空数组 `[]` 或空对象 `{}`。`curve_id` 用于 `get*` / `rawmdGet*` / `mdlsGet*`。

## 包含哪些数据

以窗口内最新主索引为准。顶层键与 MCP 对象类型对应。

### 曲线 / 曲面（JSON 内联）

| Section | 含义 | 示例 `curve_id` |
|---|---|---|
| **SwapCurve** | 互换 / OIS，CalibrationSet + Bootstrap | `CNY_SWAP_FR007_BGN`、`USD_OIS_SWAP_BGN`、`GBP_OIS_BGN` |
| **YieldCurve** | 存款 / 零息（Tenors + ZeroRates，小数） | `CNHDEPO`、`USDDEPO`、`EURDEPO` |
| **YieldCurve2** | 第二套存款曲线（与 FXFP2 / FXVol2 配套） | `CNHDEPO_2`、`USDDEPO_2` |
| **BondCurve** | 中债等债券曲线 | `CNY_BOND_TREASURY`、`CNY_BOND_CORP_AAA` |
| **BondSpreadCurve** | 相对国债的利差曲线 | `CNY_BOND_CORP_AAA_SPREAD` |
| **CreditCurve** | CDS 信用曲线 | 当前快照可为空数组 |
| **FXForwardPointsCurve** | FX 远期点 | `USDCNH_FXFP_BGN`、`EURUSD_FXFP` |
| **FXForwardPointsCurve2** | 第二套远期点（Bid / Ask 等） | `USDCNH_FXFP_BGN_2` |
| **FXVolSurface** | FX 波动率曲面（Delta × Tenor） | `USDCNH_RVOL_BGN`、`EURUSD_RVOL` |
| **FXVolSurface2** | 第二套 FX vol（Bid / Ask vol） | `USDCNH_RVOL_BGN_2` |
| **VolSurface** | 权益 / 商品 / 贵金属隐含 vol | `CSI300_VOL`、`SCM_VOL`、`AUM_VOL` |
| **LocalVol** | 局部波动率 | `CSI300_LOCALVOL`、`USDCNY_LOCALVOL` |
| **ForwardCurve** | 商品 / 贵金属远期 | `SCM_FORWARD`、`AUM_FORWARD` |
| **HistVol** | 由 HIST 价格动态构建的历史波动率节点 | 当前快照可为空；可用 `getHistVolFromPriceData` |

另有少量附属节点：`bond_clean_prices`（个别债净价）、`ir_vol_curves`（可为空）。

### 价格 HIST（`price_data_index`）

主索引不内联行情序列，而是引用同目录 CSV。

| product_type | hist_file（本目录） |
|---|---|
| BOND | `BOND_PRICES_HIST.csv` |
| EQUITYSPOT | `EQUITY_SPOT_PRICES_HIST.csv` |
| FXSPOT | `FX_SPOT_PRICES_HIST.csv` |
| FUND | `FUND_PRICES_HIST.csv` |
| EQUITYFUTURE | `EQUITYFUTURE_PRICES_HIST.csv` |
| BONDFUTURE | `BONDFUTURE_PRICES_HIST.csv` |
| COMMODITYFUTURE | `COMMODITYFUTURE_PRICES_HIST.csv` |
| PRECIOUSMETALSSPOT | `PRECIOUSMETALS_SPOT_PRICES_HIST.csv` |
| PRECIOUSMETALSPRICING | `PRECIOUSMETALS_PRICING_PRICES_HIST.csv` |
| WM_PRODUCT | `WM_PRODUCT_PRICES_HIST.csv` |

日期列多为 `valuation_date`。`getPrice` / `rawmdHistVolFromPriceData` / `mdlsHistVolFromPriceData` 按 `product_type` + 代码读这些文件。

### 参考 / 辅助表（同目录）

| 文件 | 作用 |
|---|---|
| `BOND_INFO.csv` / `BOND_INFO.json` / `BOND_INFO_SPEC.csv` | 债券条款（代码、到期、票息、发行人等） |
| `dividends.csv` | 基金 / 股票除权（`fund_code,ex_date,dividend_per_share`） |
| `INSTRUMENT_CLASSIFICATION.csv` | `instrument_classification_index.file`；情景按分类冲击 |
| `EQUITY_INFO.csv`、`FUND_INFO.csv`、`FUTURE_INFO.csv` | 标的静态信息 |
| `future_multipliers.csv`、`instrument_fees.csv`、`bond_tax_rates.csv` | 乘数 / 费率 / 税率 |
| `IR_INDEX_FIXINGS_HIST.csv` | 利率指标历史定盘 |
| `INSTRUMENT_VOLATILITY.csv` | 带 as-of 的辅助波动率序列 |
| `code_mapping.csv`、`benchmark_mapping.csv`、`BENCHMARK_EQUITY.json` | 代码与基准映射 |
| `FUND_HOLDINGS_BREAKDOWN_*.json` | 部分基金持仓分解 |
| `bond_future_deliverables.csv`、`funding_rates.csv`、`CALLABLEBOND_IR_VOLS.csv` | 可交割券、融资利率等 |

## 相对路径约定

```text
<repo>/market_data/MCP_MARKET_DATA_20260826.json
<repo>/market_data/BOND_PRICES_HIST.csv          ← price_data_index.BOND.hist_file
<repo>/market_data/INSTRUMENT_CLASSIFICATION.csv ← instrument_classification_index.file
<repo>/market_data/BOND_INFO.csv                 ← 约定文件名
<repo>/market_data/dividends.csv                 ← 约定文件名
```

不要把数据再拆到仓库根、`hist/` 或 `snapshots/`。Manager / Store 必须指向本文件夹，而不是上一级仓库根。
