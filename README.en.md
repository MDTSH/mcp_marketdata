[中文](README.md) | [English](README.en.md)

# mcp_marketdata

A publishable market-data pack for **MCP Python** and **Excel (RawMD / LiveStore)**. The public window is a rolling **~90 calendar days** of end-of-day snapshots.

Use it with [**Mathema MCP Excel**](https://github.com/MDTSH/mcp_excel). Point Manager / Store at this repo’s [`market_data/`](market_data/README.en.md) folder (not the repository root).

- Repository: https://github.com/MDTSH/mcp_marketdata
- Excel / Python package: [Mathema MCP Excel](https://github.com/MDTSH/mcp_excel)
- Field names, object types, and load examples: [`market_data/README.en.md`](market_data/README.en.md)

## What market data is included

Everything lives under `market_data/`. There is one master-index JSON per valuation date. Curves and volatility surfaces are inline in that JSON; price history and static tables are sidecar files in the same folder.

### Daily master index (curves / surfaces)

One file per valuation date: `MCP_MARKET_DATA_YYYYMMDD.json`. Loaders read raw quotes, then bootstrap / interpolate MCP objects.

- **Yield curves (YieldCurve / YieldCurve2)**  
  Multi-currency deposit / zero curves for discounting. The second set pairs with FX forwards and FX vol.

- **Swap curves (SwapCurve)**  
  CNY FR007 swaps and multi-currency overnight index swaps (OIS) for fixing and discounting rates products.

- **Bond curves and credit spreads (BondCurve / BondSpreadCurve)**  
  ChinaBond-style treasury, policy-bank, local-government, and rated credit curves, plus spreads versus treasury.

- **FX forward points (FXForwardPointsCurve / FXForwardPointsCurve2)**  
  Forward points for major pairs. The second set includes bid / ask.

- **FX volatility surfaces (FXVolSurface / FXVolSurface2)**  
  FX implied vol (tenor × delta). The second set includes bid / ask vol.

- **Equity / commodity vol and local vol (VolSurface / LocalVol)**  
  Implied vol for equity indexes, commodities, and precious metals, plus local-vol surfaces.

- **Commodity / precious-metal forwards (ForwardCurve)**  
  Forward curves such as crude, copper, gold, and silver.

- **Credit curves (CreditCurve)**  
  CDS credit-curve section. The current snapshot may be empty; loaders still recognize the type.

### Historical prices (HIST)

One time series per product type, used for marks and historical volatility.

- **Bond prices**: clean price, volume, and yield.
- **FX spot**: mid, plus bid / ask and OHLC where available.
- **Equity / fund spots**: close and volume.
- **Equity / bond / commodity futures**: listed contract marks.
- **Precious-metal spot and pricing**: gold and related series.
- **Wealth-management NAVs**: WM product prices (the window may still have no rows).
- **Rate-index fixings**: historical fixings such as EFFR.

### Static / reference tables

Reference files used for valuation, scenarios, and code mapping, in the same folder as the master index.

- **Bond terms (BOND_INFO)**: code, maturity, coupon, issuer, rating, and related fields.
- **Dividends**: fund / equity ex-dates and amounts.
- **Instrument classification**: product class and subclass for scenario shocks.
- **Underlying info**: equity, fund, and future static fields (multipliers, fees, tax rates, and similar).
- **Mappings and holdings**: trade-code to price-code maps, benchmarks, and selected fund holdings breakdowns.
- **Other convention tables**: bond-future deliverables, funding rates, callable-bond rate vols, and similar.

## How to use

After cloning, set the data root to the `market_data/` folder (absolute path, or a path relative to the workbook). One master index per day: `MCP_MARKET_DATA_YYYYMMDD.json`. Full examples and field notes: [`market_data/README.en.md`](market_data/README.en.md).

```python
import mcp
mgr = mcp.MRawMarketManager(r".../mcp_marketdata/market_data")
yc = mgr.getYieldCurve("CNHDEPO", "20260826")
```
