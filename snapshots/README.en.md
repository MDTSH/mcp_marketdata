[中文](README.md) | [English](README.en.md)

# snapshots/

This folder is the **market-data root** published by [MDTSH/mcp_marketdata](https://github.com/MDTSH/mcp_marketdata).

Use it with [**Mathema MCP Excel**](https://github.com/MDTSH/mcp_excel). For MCP Python and Excel RawMD, **root** = **this folder**. Master-index file name: `MCP_MARKET_DATA_YYYYMMDD.json`. Relative paths inside the JSON (`hist_file`, `current_file`, `file`, and convention sidecar names) resolve against this folder.

The pack covers a rolling **~90 calendar days** of end-of-day snapshots. Loaders read raw quotes (rates, forward points, volatility, HIST prices), then bootstrap / interpolate MCP objects.

## What market data is included

Based on the latest master index in the window. Top-level keys match MCP object types.

### Daily master index (curves / surfaces, inline in JSON)

One file per valuation date: `MCP_MARKET_DATA_YYYYMMDD.json`. Curves and vol surfaces are inline; price history and static tables are referenced by file name in this folder.

- **Yield curves (YieldCurve / YieldCurve2)**  
  Multi-currency deposit / zero curves (tenors + zero rates). Examples: `CNHDEPO`, `USDDEPO`, `EURDEPO`. The second set (`CNHDEPO_2`, …) pairs with FX forwards and FX vol.

- **Swap curves (SwapCurve)**  
  Swap / OIS curves (CalibrationSet + bootstrap). Examples: `CNY_SWAP_FR007_BGN`, `USD_OIS_SWAP_BGN`, `GBP_OIS_BGN`.

- **Bond curves and credit spreads (BondCurve / BondSpreadCurve)**  
  ChinaBond-style treasury, policy-bank, local-government, and rated credit curves (e.g. `CNY_BOND_TREASURY`, `CNY_BOND_CORP_AAA`), plus spreads versus treasury (e.g. `CNY_BOND_CORP_AAA_SPREAD`).

- **FX forward points (FXForwardPointsCurve / FXForwardPointsCurve2)**  
  Forward points for major pairs. Examples: `USDCNH_FXFP_BGN`, `EURUSD_FXFP`. The second set includes bid / ask.

- **FX volatility surfaces (FXVolSurface / FXVolSurface2)**  
  FX implied vol (tenor × delta). Examples: `USDCNH_RVOL_BGN`, `EURUSD_RVOL`. The second set includes bid / ask vol.

- **Equity / commodity vol and local vol (VolSurface / LocalVol)**  
  Implied vol for equity indexes, commodities, and precious metals (e.g. `CSI300_VOL`, `SCM_VOL`, `AUM_VOL`), plus local vol (e.g. `CSI300_LOCALVOL`, `USDCNY_LOCALVOL`).

- **Commodity / precious-metal forwards (ForwardCurve)**  
  Examples: `SCM_FORWARD`, `AUM_FORWARD`, `CUM_FORWARD`.

- **Credit curves (CreditCurve)**  
  CDS credit-curve section. The current snapshot may be an empty array.

- **Historical-vol nodes (HistVol)**  
  Can be built dynamically from HIST prices; the current snapshot may be empty. A few extra nodes: `bond_clean_prices` (occasional clean prices) and `ir_vol_curves` (may be empty).

### Historical prices (HIST CSV)

The master index does not inline price series. It points at sibling CSVs via `price_data_index`. `getPrice` / `rawmdHistVolFromPriceData` read them by product type + code. The date column is usually `valuation_date`.

| Product | File | Contents |
|---|---|---|
| Bonds | `BOND_PRICES_HIST.csv` | Clean price, volume, yield |
| FX spot | `FX_SPOT_PRICES_HIST.csv` | Mid, bid / ask, OHLC |
| Equity spot | `EQUITY_SPOT_PRICES_HIST.csv` | Price, volume |
| Funds | `FUND_PRICES_HIST.csv` | Price, volume |
| Equity futures | `EQUITYFUTURE_PRICES_HIST.csv` | Contract marks |
| Bond futures | `BONDFUTURE_PRICES_HIST.csv` | Contract marks |
| Commodity futures | `COMMODITYFUTURE_PRICES_HIST.csv` | Contract marks |
| Precious-metal spot | `PRECIOUSMETALS_SPOT_PRICES_HIST.csv` | Spot prices |
| Precious-metal pricing | `PRECIOUSMETALS_PRICING_PRICES_HIST.csv` | Pricing series |
| Wealth-management products | `WM_PRODUCT_PRICES_HIST.csv` | NAV (the window may still have no rows) |

This folder also has **rate-index fixings** `IR_INDEX_FIXINGS_HIST.csv` (e.g. EFFR) and an as-of auxiliary vol series `INSTRUMENT_VOLATILITY.csv`.

### Static / reference tables

| File | Role |
|---|---|
| `BOND_INFO.csv` / `BOND_INFO.json` / `BOND_INFO_SPEC.csv` | Bond terms (code, maturity, coupon, issuer, rating, …) |
| `dividends.csv` | Fund / equity ex-dates (`fund_code,ex_date,dividend_per_share`) |
| `INSTRUMENT_CLASSIFICATION.csv` | Classification (`instrument_classification_index.file`) for scenario shocks |
| `EQUITY_INFO.csv`, `FUND_INFO.csv`, `FUTURE_INFO.csv` | Underlying static fields |
| `future_multipliers.csv`, `instrument_fees.csv`, `bond_tax_rates.csv` | Multipliers / fees / tax rates |
| `code_mapping.csv`, `benchmark_mapping.csv`, `BENCHMARK_EQUITY.json` | Code and benchmark maps |
| `FUND_HOLDINGS_BREAKDOWN_*.json` | Selected fund holdings breakdowns |
| `bond_future_deliverables.csv`, `funding_rates.csv`, `CALLABLEBOND_IR_VOLS.csv` | Deliverables, funding rates, callable-bond rate vols |
| `brinson_sector_benchmark.csv`, `brinson_stock_holdings.csv` | Brinson attribution reference holdings / sector weights |

## Point loaders at this folder

| Entry | Usage | When |
|---|---|---|
| **RawMD** `MRawMarketManager` / Excel `McpRawMarketManager` | `setRoot(<this folder>)`, then fetch by `curve_id` + `valuation_date` | Directory mode: open the master index for a date |
| **JsonReader** `MMarketDataJsonReader` / Excel `McpMarketDataJsonReader` | `loadFromFile(.../MCP_MARKET_DATA_YYYYMMDD.json)` | Single-file, read-only |
| **LiveStore** `MLiveMarketDataStore` / Excel `McpLiveMarketDataStore` | `loadSnapshot(same JSON)`, then `applyUpdate` | Full snapshot + incremental patch |

### MCP Python

```python
import mcp

root = r".../mcp_marketdata/snapshots"  # your clone path

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

A valuation engine can set `raw_market_data_root` / `MCP_MARKET_DATA_ROOT` to this folder.

### Excel RawMD / LiveStore

```excel
=McpRawMarketManager(".../mcp_marketdata/snapshots")
=rawmdGetYieldCurve2(A1, "CNHDEPO_2", "20260826")
=rawmdGetFXVolSurface2(A1, "USDCNH_RVOL_BGN_2", "20260826")
=rawmdAvailableDates(A1)

=McpLiveMarketDataStore(".../mcp_marketdata/snapshots/MCP_MARKET_DATA_20260826.json")
=mdlsGetFXVolSurface2(B1, "USDCNH_RVOL_BGN_2")
=mdlsGetSwapCurve(B1, "CNY_SWAP_FR007_BGN")
```

`McpResolvePath("snapshots")` can turn a workbook-relative path into an absolute path. After you have a curve / surface object, use existing UDFs such as `YieldCurve2ZeroRate` and `FXVolSurface2GetVolatility`. Function notes: [Raw Market Data](https://help.mathema.com.cn/zh/latest/api/rawmarketdata.html).

### Object chain

Master-index JSON (inline curves / surfaces + `price_data_index` pointing at sibling HIST / aux CSVs) → `MRawMarketManager` / `MMarketDataJsonReader` / `MLiveMarketDataStore` → `MYieldCurve` / `MYieldCurve2` / `MSwapCurve` / `MBondCurve` / `MFXForwardPointsCurve(2)` / `MFXVolSurface(2)` / `MVolSurface` / `MLocalVol`, and so on. `MLiveMarketDataStore` `get*` pointers stay stable across `applyUpdate` (in-place core swap).

## `MCP_MARKET_DATA_YYYYMMDD.json`

One file per valuation date. Top-level shape:

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

Unused types may be `[]` or `{}`. `curve_id` is what `get*` / `rawmdGet*` / `mdlsGet*` use.

## Relative-path convention

```text
<repo>/snapshots/MCP_MARKET_DATA_20260826.json
<repo>/snapshots/BOND_PRICES_HIST.csv          ← price_data_index.BOND.hist_file
<repo>/snapshots/INSTRUMENT_CLASSIFICATION.csv ← instrument_classification_index.file
<repo>/snapshots/BOND_INFO.csv                 ← convention file name
<repo>/snapshots/dividends.csv                 ← convention file name
```

Do not split data to the repo root or `hist/`. Manager / Store must point at this folder (`snapshots/`), not the parent repository root.
