# market_data/

本目录是 GitHub 仓库 [MDTSH/mcp_marketdata](https://github.com/MDTSH/mcp_marketdata) 对外发布的 **market_data 主目录**（不是再套一层 `snapshots/`）。

本地源只同步 **`Z:\market_data\snapshots`** 里属于该目录的 JSON + HIST + 辅助表；**不会**拷贝父目录 `Z:\market_data` 下的 `live`、`qh` 或其他 dump。

MCP Python 的 **root** = **本文件夹**。主索引文件名：`MCP_MARKET_DATA_YYYYMMDD.json`（例如 `MCP_MARKET_DATA_20260826.json`）。JSON 内的相对路径（`hist_file`、`current_file`、`file`、约定 sidecar 文件名）都相对这里解析。

## 给 MCP Python 用

这套数据面向 **MCP Python** 的 Raw 市场数据接口，核心是一日一份的 JSON 快照，而不是已序列化的曲线对象。加载器读原始报价（利率、远期点、波动率、HIST 价格），再 Bootstrap / 插值成 MCP 对象。

| 入口 | 用法 | 何时用 |
|---|---|---|
| `MRawMarketManager` | `setRoot(<本目录>)`，再按 `curve_id` + `valuation_date` 取对象 | 目录模式：按估值日打开对应主索引 |
| `MMarketDataJsonReader` | `loadFromFile(.../MCP_MARKET_DATA_YYYYMMDD.json)` | 单文件入口，与目录模式对等 |
| `MLiveMarketDataStore` | `loadSnapshot(同一 JSON)`，之后可 `applyUpdate` | 全量快照 + 增量 patch |

```python
import mcp

root = r"D:\work\mcp\github\mcp_marketdata\market_data"

mgr = mcp.MRawMarketManager(root)
yc = mgr.getYieldCurve("CNHDEPO", "20260826")
fxvol = mgr.getFXVolSurface("USDCNH_RVOL_BGN", "20260826")
px = mgr.getPrice("000300", "EQUITYSPOT", "20260826")

reader = mcp.MMarketDataJsonReader()
reader.loadFromFile(root + r"\MCP_MARKET_DATA_20260826.json")
swap = reader.getSwapCurve("CNY_SWAP_FR007_BGN")

store = mcp.MLiveMarketDataStore()
store.loadSnapshot(root + r"\MCP_MARKET_DATA_20260826.json")
fxvol2 = store.getFXVolSurface2("USDCNH_RVOL_BGN_2")
```

估值引擎侧也可把 `raw_market_data_root` / `MCP_MARKET_DATA_ROOT` 指到本目录。

### 对象链（一句话）

主索引 JSON（内联曲线/曲面 + `price_data_index` 指向同目录 HIST/辅助 CSV）→ `MRawMarketManager` / `MMarketDataJsonReader` / `MLiveMarketDataStore` → `MYieldCurve` / `MYieldCurve2` / `MSwapCurve` / `MBondCurve` / `MFXForwardPointsCurve(2)` / `MFXVolSurface(2)` / `MVolSurface` / `MLocalVol` 等 MCP 对象。`MLiveMarketDataStore` 的 `get*` 指针在 `applyUpdate` 后保持不变（原地换芯）。

## 包含哪些数据（按主索引 section 分类）

以窗口内最新主索引 `MCP_MARKET_DATA_20260826.json` 为准。顶层键与 MCP 对象类型对应；未用类型可为空数组。

### 曲线 / 曲面（JSON 内联）

| Section | 含义 | 本仓库示例 `curve_id` |
|---|---|---|
| **SwapCurve** | 互换/OIS，CalibrationSet + Bootstrap | `CNY_SWAP_FR007_BGN`、`USD_OIS_SWAP_BGN`、`GBP_OIS_BGN` |
| **YieldCurve** | 存款/零息（Tenors + ZeroRates，小数） | `CNHDEPO`、`USDDEPO`、`EURDEPO` |
| **YieldCurve2** | 第二套存款曲线（与 FXFP2 / FXVol2 配套） | `CNHDEPO_2`、`USDDEPO_2` |
| **BondCurve** | 中债等债券曲线 | `CNY_BOND_TREASURY`、`CNY_BOND_CORP_AAA` |
| **BondSpread**（`BondSpreadCurve`） | 相对国债的利差曲线 | `CNY_BOND_CORP_AAA_SPREAD` |
| **CreditCurve** | CDS 信用曲线 | 当前快照为空数组 |
| **FXForwardPointsCurve** | FX 远期点 | `USDCNH_FXFP_BGN`、`EURUSD_FXFP` |
| **FXForwardPointsCurve2** | 第二套远期点（Bid/Ask 等） | `USDCNH_FXFP_BGN_2` |
| **FXVolSurface** | FX 波动率曲面（Delta × Tenor） | `USDCNH_RVOL_BGN`、`EURUSD_RVOL` |
| **FXVolSurface2** | 第二套 FX vol（Bid/Ask vol） | `USDCNH_RVOL_BGN_2` |
| **VolSurface** | 权益/商品/贵金属隐含 vol | `CSI300_VOL`、`SCM_VOL`、`AUM_VOL` |
| **LocalVol** | 局部波动率 | `CSI300_LOCALVOL`、`USDCNY_LOCALVOL` |
| **ForwardCurve** | 商品/贵金属远期 | `SCM_FORWARD`、`AUM_FORWARD` |
| **HistVol** | 由 HIST 价格动态构建的历史波动率节点 | 当前快照为空；可用 `getHistVolFromPriceData` |

另有少量附属节点：`bond_clean_prices`（个别债净价）、`ir_vol_curves`（当前为空）。

### 价格 HIST（`price_data_index`）

主索引不内联行情序列，而是引用同目录 CSV。本仓库 `price_data_index` 产品类型：

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

`current_file`（如 `BOND_PRICES.csv`）源端通常不存在，加载器回退到对应 `hist_file`。日期列多为 `valuation_date`。

### 参考 / 辅助表（同目录，JSON 往往不写路径）

| 文件 | 作用 |
|---|---|
| `BOND_INFO.csv` / `BOND_INFO.json` / `BOND_INFO_SPEC.csv` | 债券条款（代码、到期、票息、发行人等），整表发布 |
| `dividends.csv` | 基金/股票除权（`fund_code,ex_date,dividend_per_share`），事件表整表发布 |
| `INSTRUMENT_CLASSIFICATION.csv` | `instrument_classification_index.file`；情景按分类冲击 |
| `EQUITY_INFO.csv`、`FUND_INFO.csv`、`FUTURE_INFO.csv` | 标的静态信息 |
| `future_multipliers.csv`、`instrument_fees.csv`、`bond_tax_rates.csv` | 乘数 / 费率 / 税率 |
| `IR_INDEX_FIXINGS_HIST.csv` | 利率指标历史定盘 |
| `INSTRUMENT_VOLATILITY.csv` | 带 as-of 的辅助波动率序列（按窗口裁剪） |
| `code_mapping.csv`、`benchmark_mapping.csv`、`BENCHMARK_EQUITY.json` | 代码与基准映射 |
| `FUND_HOLDINGS_BREAKDOWN_*.json` | 部分基金持仓分解 |
| `bond_future_deliverables.csv`、`funding_rates.csv`、`CALLABLEBOND_IR_VOLS.csv` 等 | 可交割券、融资利率等 |

源上若没有 `corporate_actions.csv`、`fund_fees.csv`，本仓库也不发布。

## 90 日窗口与体积

- 主索引：文件名日期 ≥ 今天 − **90** 个自然日。
- `*_HIST*.csv`：按日期列裁到窗口。
- **`BOND_PRICES_HIST.csv`**：跨度大，90 日裁完仍可能 ≥100MB。GitHub.com 单文件上限 100MB，且本仓库 **不用 Git LFS**，同步脚本会再丢掉最旧行直到 **&lt;99MB**。此时债券 HIST 实际起始日可能晚于窗口起点（见 `reports/SYNC_REPORT_*.md`，例如曾从 2026-06-10 起保留）。
- `BOND_INFO*`、分类、INFO/费率/乘数整表复制（`maturity_date` 是条款字段，不是行情时间）。
- `dividends.csv` 有 `ex_date`，但是稀疏事件表；按 90 日裁会丢掉窗口外仍可能用到的除权记录，因此整表发布。

## 相对路径约定

```
<repo>/market_data/MCP_MARKET_DATA_20260826.json
<repo>/market_data/BOND_PRICES_HIST.csv          ← price_data_index.BOND.hist_file
<repo>/market_data/INSTRUMENT_CLASSIFICATION.csv ← instrument_classification_index.file
<repo>/market_data/BOND_INFO.csv                 ← 约定文件名
<repo>/market_data/dividends.csv                 ← 约定文件名
```

不要把数据再拆到仓库根、`hist/` 或 `snapshots/`。`scripts/`、`reports/` 在仓库根，不在本目录。周六任务从 `Z:\market_data\snapshots` 同步到这里，见仓库根 `README.md`。
