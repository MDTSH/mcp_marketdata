# SYNC_REPORT_20260827

- as_of: 2026-08-27
- window: 2026-05-29 .. 2026-08-27 (90 calendar days)
- source: `Z:\market_data\snapshots`
- dest: `D:\work\mcp\github\mcp_marketdata`
- published_dir: `snapshots` (source mixes JSON + HIST + aux; relative names kept)
- dry_run: false
- dest_published_size: 160.91 MB

## JSON

- source_outside_window: 651
- added (0):
  - (none)
- updated (0):
  - (none)
- unchanged (63):
  - MCP_MARKET_DATA_20260529.json
  - MCP_MARKET_DATA_20260601.json
  - MCP_MARKET_DATA_20260602.json
  - MCP_MARKET_DATA_20260603.json
  - MCP_MARKET_DATA_20260604.json
  - MCP_MARKET_DATA_20260605.json
  - MCP_MARKET_DATA_20260608.json
  - MCP_MARKET_DATA_20260609.json
  - MCP_MARKET_DATA_20260610.json
  - MCP_MARKET_DATA_20260611.json
  - MCP_MARKET_DATA_20260612.json
  - MCP_MARKET_DATA_20260615.json
  - MCP_MARKET_DATA_20260616.json
  - MCP_MARKET_DATA_20260617.json
  - MCP_MARKET_DATA_20260618.json
  - MCP_MARKET_DATA_20260622.json
  - MCP_MARKET_DATA_20260623.json
  - MCP_MARKET_DATA_20260624.json
  - MCP_MARKET_DATA_20260625.json
  - MCP_MARKET_DATA_20260626.json
  - MCP_MARKET_DATA_20260629.json
  - MCP_MARKET_DATA_20260630.json
  - MCP_MARKET_DATA_20260701.json
  - MCP_MARKET_DATA_20260702.json
  - MCP_MARKET_DATA_20260703.json
  - MCP_MARKET_DATA_20260706.json
  - MCP_MARKET_DATA_20260707.json
  - MCP_MARKET_DATA_20260708.json
  - MCP_MARKET_DATA_20260709.json
  - MCP_MARKET_DATA_20260710.json
  - MCP_MARKET_DATA_20260713.json
  - MCP_MARKET_DATA_20260714.json
  - MCP_MARKET_DATA_20260715.json
  - MCP_MARKET_DATA_20260716.json
  - MCP_MARKET_DATA_20260717.json
  - MCP_MARKET_DATA_20260720.json
  - MCP_MARKET_DATA_20260721.json
  - MCP_MARKET_DATA_20260722.json
  - MCP_MARKET_DATA_20260723.json
  - MCP_MARKET_DATA_20260724.json
  - MCP_MARKET_DATA_20260727.json
  - MCP_MARKET_DATA_20260728.json
  - MCP_MARKET_DATA_20260729.json
  - MCP_MARKET_DATA_20260730.json
  - MCP_MARKET_DATA_20260731.json
  - MCP_MARKET_DATA_20260803.json
  - MCP_MARKET_DATA_20260804.json
  - MCP_MARKET_DATA_20260805.json
  - MCP_MARKET_DATA_20260806.json
  - MCP_MARKET_DATA_20260807.json
  - MCP_MARKET_DATA_20260810.json
  - MCP_MARKET_DATA_20260811.json
  - MCP_MARKET_DATA_20260812.json
  - MCP_MARKET_DATA_20260813.json
  - MCP_MARKET_DATA_20260814.json
  - MCP_MARKET_DATA_20260817.json
  - MCP_MARKET_DATA_20260818.json
  - MCP_MARKET_DATA_20260819.json
  - MCP_MARKET_DATA_20260820.json
  - MCP_MARKET_DATA_20260821.json
  - MCP_MARKET_DATA_20260824.json
  - MCP_MARKET_DATA_20260825.json
  - MCP_MARKET_DATA_20260826.json
- deleted (0):
  - (none)

## HIST / referenced / auxiliary files

| file | action | rows_before | rows_after | unparsed | dest_size |
|---|---|---:|---:|---:|---|
| BENCHMARK_EQUITY.json | copy | 0 | 0 | 0 | 0.00 MB |
| BONDFUTURE_PRICES.csv | missing | 0 | 0 | 0 | 0.00 MB |
| BONDFUTURE_PRICES_HIST.csv | trim | 6528 | 756 | 0 | 0.03 MB |
| BOND_INFO.csv | copy | 0 | 0 | 0 | 14.92 MB |
| BOND_INFO.json | copy | 0 | 0 | 0 | 0.00 MB |
| BOND_INFO_SPEC.csv | copy | 0 | 0 | 0 | 0.02 MB |
| BOND_PRICES.csv | missing | 0 | 0 | 0 | 0.00 MB |
| BOND_PRICES_HIST.csv | trim+github_cap | 17584221 | 2527290 | 0 | 97.46 MB |
| CALLABLEBOND_IR_VOLS.csv | copy | 0 | 0 | 0 | 0.00 MB |
| COMMODITYFUTURE_PRICES.csv | missing | 0 | 0 | 0 | 0.00 MB |
| COMMODITYFUTURE_PRICES_HIST.csv | trim | 580 | 0 | 0 | 0.00 MB |
| EQUITYFUTURE_PRICES.csv | missing | 0 | 0 | 0 | 0.00 MB |
| EQUITYFUTURE_PRICES_HIST.csv | trim | 8692 | 996 | 0 | 0.03 MB |
| EQUITY_INFO.csv | copy | 0 | 0 | 0 | 0.00 MB |
| EQUITY_SPOT_PRICES.csv | missing | 0 | 0 | 0 | 0.00 MB |
| EQUITY_SPOT_PRICES_HIST.csv | trim | 5808670 | 584599 | 0 | 19.73 MB |
| FUND_HOLDINGS_BREAKDOWN_510050.SH.json | copy | 0 | 0 | 0 | 0.01 MB |
| FUND_HOLDINGS_BREAKDOWN_510300.SH.json | copy | 0 | 0 | 0 | 0.01 MB |
| FUND_HOLDINGS_BREAKDOWN_510300.json | copy | 0 | 0 | 0 | 0.00 MB |
| FUND_HOLDINGS_BREAKDOWN_510500.SH.json | copy | 0 | 0 | 0 | 0.01 MB |
| FUND_HOLDINGS_BREAKDOWN_511090.SH.json | copy | 0 | 0 | 0 | 0.00 MB |
| FUND_HOLDINGS_BREAKDOWN_511130.SH.json | copy | 0 | 0 | 0 | 0.00 MB |
| FUND_HOLDINGS_BREAKDOWN_511130.json | copy | 0 | 0 | 0 | 0.00 MB |
| FUND_HOLDINGS_BREAKDOWN_511520.SH.json | copy | 0 | 0 | 0 | 0.00 MB |
| FUND_HOLDINGS_BREAKDOWN_512100.SH.json | copy | 0 | 0 | 0 | 0.01 MB |
| FUND_INFO.csv | copy | 0 | 0 | 0 | 0.00 MB |
| FUND_PRICES.csv | missing | 0 | 0 | 0 | 0.00 MB |
| FUND_PRICES_HIST.csv | trim | 610385 | 32222 | 0 | 1.17 MB |
| FUTURE_INFO.csv | copy | 0 | 0 | 0 | 0.00 MB |
| FX_SPOT_PRICES.csv | missing | 0 | 0 | 0 | 0.00 MB |
| FX_SPOT_PRICES_HIST.csv | trim | 51001 | 6660 | 0 | 0.45 MB |
| INSTRUMENT_CLASSIFICATION.csv | copy | 0 | 0 | 0 | 0.00 MB |
| INSTRUMENT_VOLATILITY.csv | trim | 6786 | 0 | 0 | 0.00 MB |
| IR_INDEX_FIXINGS_HIST.csv | trim | 10922 | 403 | 0 | 0.01 MB |
| PRECIOUSMETALS_PRICING_PRICES.csv | missing | 0 | 0 | 0 | 0.00 MB |
| PRECIOUSMETALS_PRICING_PRICES_HIST.csv | trim | 592 | 0 | 0 | 0.00 MB |
| PRECIOUSMETALS_SPOT_PRICES.csv | missing | 0 | 0 | 0 | 0.00 MB |
| PRECIOUSMETALS_SPOT_PRICES_HIST.csv | trim | 1101 | 45 | 0 | 0.00 MB |
| WM_PRODUCT_PRICES.csv | missing | 0 | 0 | 0 | 0.00 MB |
| WM_PRODUCT_PRICES_HIST.csv | trim | 1 | 0 | 0 | 0.00 MB |
| benchmark_mapping.csv | copy | 0 | 0 | 0 | 0.00 MB |
| bond_future_deliverables.csv | copy | 0 | 0 | 0 | 0.00 MB |
| bond_tax_rates.csv | copy | 0 | 0 | 0 | 0.00 MB |
| brinson_sector_benchmark.csv | copy | 0 | 0 | 0 | 0.00 MB |
| brinson_stock_holdings.csv | copy | 0 | 0 | 0 | 0.00 MB |
| code_mapping.csv | copy | 0 | 0 | 0 | 0.00 MB |
| dividends.csv | copy | 0 | 0 | 0 | 0.00 MB |
| funding_rates.csv | copy | 0 | 0 | 0 | 0.00 MB |
| future_multipliers.csv | copy | 0 | 0 | 0 | 0.00 MB |
| instrument_fees.csv | copy | 0 | 0 | 0 | 0.01 MB |

## Dangling refs

- `BONDFUTURE_PRICES.csv`
- `BOND_PRICES.csv`
- `COMMODITYFUTURE_PRICES.csv`
- `EQUITYFUTURE_PRICES.csv`
- `EQUITY_SPOT_PRICES.csv`
- `FUND_PRICES.csv`
- `FX_SPOT_PRICES.csv`
- `PRECIOUSMETALS_PRICING_PRICES.csv`
- `PRECIOUSMETALS_SPOT_PRICES.csv`
- `WM_PRODUCT_PRICES.csv`

## Well-known sidecars missing on source

- `corporate_actions.csv`
- `fund_fees.csv`

## Warnings

- BOND_PRICES_HIST.csv: GitHub 99MB cap applied; HIST rows kept from 2026-06-10 (90-day window still used for JSON)
- BOND_PRICES_HIST.csv: dest size 97.46 MB is near GitHub 100MB limit.
- well-known sidecars missing on source (not published): corporate_actions.csv, fund_fees.csv
