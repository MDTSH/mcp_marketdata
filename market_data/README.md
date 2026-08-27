[中文](README.md) | [English](README.en.md)

# market_data/

本目录是 [MDTSH/mcp_marketdata](https://github.com/MDTSH/mcp_marketdata) 发布的 **市场数据根目录**。

配合 [**Mathema MCP Excel**](https://github.com/MDTSH/mcp_excel) 使用；MCP Python 与 Excel RawMD 的 **root** = **本文件夹**。主索引文件名：`MCP_MARKET_DATA_YYYYMMDD.json`。JSON 内的相对路径（`hist_file`、`current_file`、`file`、约定 sidecar 文件名）都相对这里解析。

数据包覆盖滚动约 **90 个自然日** 的日终快照。加载器读原始报价（利率、远期点、波动率、HIST 价格），再 Bootstrap / 插值成 MCP 对象。

## 包含了哪些市场数据

以窗口内最新主索引为准。顶层键与 MCP 对象类型对应。

### 日主索引（曲线 / 曲面，写在 JSON 内）

每个估值日一个 `MCP_MARKET_DATA_YYYYMMDD.json`。曲线和波动率曲面内联；行情与静态表由同目录文件名引用。

- **收益率曲线（YieldCurve / YieldCurve2）**  
  多币种存款 / 零息曲线（Tenors + ZeroRates）。例如 `CNHDEPO`、`USDDEPO`、`EURDEPO`；第二套如 `CNHDEPO_2`，与外汇远期、外汇波动率配套。

- **互换曲线（SwapCurve）**  
  互换 / OIS（CalibrationSet + Bootstrap）。例如 `CNY_SWAP_FR007_BGN`、`USD_OIS_SWAP_BGN`、`GBP_OIS_BGN`。

- **债券曲线与信用利差（BondCurve / BondSpreadCurve）**  
  中债国债、政策性金融债、地方债及各评级信用债曲线（如 `CNY_BOND_TREASURY`、`CNY_BOND_CORP_AAA`），以及相对国债的利差（如 `CNY_BOND_CORP_AAA_SPREAD`）。

- **外汇远期点（FXForwardPointsCurve / FXForwardPointsCurve2）**  
  主要货币对远期点数。例如 `USDCNH_FXFP_BGN`、`EURUSD_FXFP`；第二套含买卖价。

- **外汇波动率曲面（FXVolSurface / FXVolSurface2）**  
  外汇隐含波动率（期限 × Delta）。例如 `USDCNH_RVOL_BGN`、`EURUSD_RVOL`；第二套含买卖价波动率。

- **权益 / 商品波动率与局部波动率（VolSurface / LocalVol）**  
  股指、商品、贵金属隐含波动率（如 `CSI300_VOL`、`SCM_VOL`、`AUM_VOL`），以及局部波动率（如 `CSI300_LOCALVOL`、`USDCNY_LOCALVOL`）。

- **商品 / 贵金属远期（ForwardCurve）**  
  例如 `SCM_FORWARD`、`AUM_FORWARD`、`CUM_FORWARD`。

- **信用曲线（CreditCurve）**  
  CDS 信用曲线分区；当前快照可为空数组。

- **历史波动率节点（HistVol）**  
  可由 HIST 价格动态构建；当前快照可为空。另有少量附属节点：`bond_clean_prices`（个别债净价）、`ir_vol_curves`（可为空）。

### 历史行情（HIST CSV）

主索引不内联行情序列，而是通过 `price_data_index` 引用同目录 CSV。`getPrice` / `rawmdHistVolFromPriceData` 按品种 + 代码读取。日期列多为 `valuation_date`。

| 品种 | 文件 | 内容 |
|---|---|---|
| 债券 | `BOND_PRICES_HIST.csv` | 净价、成交量、收益率 |
| 外汇即期 | `FX_SPOT_PRICES_HIST.csv` | 中间价及买卖价、开高低收 |
| 股票现货 | `EQUITY_SPOT_PRICES_HIST.csv` | 价格、成交量 |
| 基金 | `FUND_PRICES_HIST.csv` | 价格、成交量 |
| 股指期货 | `EQUITYFUTURE_PRICES_HIST.csv` | 合约行情 |
| 国债期货 | `BONDFUTURE_PRICES_HIST.csv` | 合约行情 |
| 商品期货 | `COMMODITYFUTURE_PRICES_HIST.csv` | 合约行情 |
| 贵金属现货 | `PRECIOUSMETALS_SPOT_PRICES_HIST.csv` | 现货价格 |
| 贵金属定价 | `PRECIOUSMETALS_PRICING_PRICES_HIST.csv` | 定价序列 |
| 理财产品 | `WM_PRODUCT_PRICES_HIST.csv` | 净值（窗口内可能尚无行） |

同目录还有 **利率指标定盘** `IR_INDEX_FIXINGS_HIST.csv`（如 EFFR），以及带 as-of 的辅助波动率序列 `INSTRUMENT_VOLATILITY.csv`。

### 静态辅助

| 文件 | 作用 |
|---|---|
| `BOND_INFO.csv` / `BOND_INFO.json` / `BOND_INFO_SPEC.csv` | 债券条款（代码、到期、票息、发行人、评级等） |
| `dividends.csv` | 基金 / 股票除权（`fund_code,ex_date,dividend_per_share`） |
| `INSTRUMENT_CLASSIFICATION.csv` | 工具分类（`instrument_classification_index.file`）；情景按分类冲击 |
| `EQUITY_INFO.csv`、`FUND_INFO.csv`、`FUTURE_INFO.csv` | 标的静态信息 |
| `future_multipliers.csv`、`instrument_fees.csv`、`bond_tax_rates.csv` | 乘数 / 费率 / 税率 |
| `code_mapping.csv`、`benchmark_mapping.csv`、`BENCHMARK_EQUITY.json` | 代码与基准映射 |
| `FUND_HOLDINGS_BREAKDOWN_*.json` | 部分基金持仓分解 |
| `bond_future_deliverables.csv`、`funding_rates.csv`、`CALLABLEBOND_IR_VOLS.csv` | 可交割券、融资利率、含权债利率波动率 |
| `brinson_sector_benchmark.csv`、`brinson_stock_holdings.csv` | Brinson 归因参考持仓 / 行业权重 |

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

## 相对路径约定

```text
<repo>/market_data/MCP_MARKET_DATA_20260826.json
<repo>/market_data/BOND_PRICES_HIST.csv          ← price_data_index.BOND.hist_file
<repo>/market_data/INSTRUMENT_CLASSIFICATION.csv ← instrument_classification_index.file
<repo>/market_data/BOND_INFO.csv                 ← 约定文件名
<repo>/market_data/dividends.csv                 ← 约定文件名
```

不要把数据再拆到仓库根、`hist/` 或 `snapshots/`。Manager / Store 必须指向本文件夹，而不是上一级仓库根。
