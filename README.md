[中文](README.md) | [English](README.en.md)

# mcp_marketdata

市场数据标准包，不是行情下载站。

本仓库给出的是经过清洗、整理、并按类型预定义惯例的日终快照。JSON 顶层键与 MCP 对象一一对应（`SwapCurve`、`YieldCurve`、`FXVolSurface`、`CreditCurve` …）。每个节点本身就是该类数据的定义：日历、日计数、插值、单位都已写好。有这类节点，就有这类数据的定义。

中国市场滚动约 **90 个自然日** 的日终包，是这份标准的公开样本。经 MCP 转换成引擎对象后，可直接用于 Excel、Python 和估值批次——定价与风险共用同一套定义。

配合 [**Mathema MCP Excel**](https://github.com/MDTSH/mcp_excel) 使用。把 Manager / Store 指到本仓库的 [`snapshots/`](snapshots/README.md)（不要指仓库根目录）。

- 仓库：https://github.com/MDTSH/mcp_marketdata
- Excel / Python 包：[Mathema MCP Excel](https://github.com/MDTSH/mcp_excel)
- 帮助站：[Raw Market Data](https://help.mathema.com.cn/zh/latest/api/rawmarketdata.html)、[市场数据就绪](https://help.mathema.com.cn/zh/latest/docs/risk/market_data_readiness.html)
- 字段、对象类型与加载示例见 [`snapshots/README.md`](snapshots/README.md)

## 包含了哪些市场数据

数据都在 `snapshots/`。一日一份主索引 JSON，曲线和波动率写在 JSON 里；行情序列和静态表是同目录下的 CSV / JSON。

### 日主索引（曲线 / 曲面）

每个估值日一个 `MCP_MARKET_DATA_YYYYMMDD.json`。加载器读原始报价，再 Bootstrap / 插值成 MCP 对象。

- **收益率曲线（YieldCurve / YieldCurve2）**  
  多币种存款 / 零息曲线，用于折现；第二套与外汇远期、外汇波动率配套。

- **互换曲线（SwapCurve）**  
  人民币 FR007 互换及多币种隔夜指数互换（OIS），用于利率产品定盘与折现。

- **债券曲线与信用利差（BondCurve / BondSpreadCurve）**  
  中债国债、政策性金融债、地方债及各评级信用债曲线，以及相对国债的利差曲线。

- **外汇远期点（FXForwardPointsCurve / FXForwardPointsCurve2）**  
  主要货币对的远期点数；第二套提供买卖价。

- **外汇波动率曲面（FXVolSurface / FXVolSurface2）**  
  外汇隐含波动率（期限 × Delta）；第二套提供买卖价波动率。

- **权益 / 商品波动率与局部波动率（VolSurface / LocalVol）**  
  股指、商品、贵金属的隐含波动率，以及局部波动率曲面。

- **商品 / 贵金属远期（ForwardCurve）**  
  原油、铜、金银等远期曲线。

- **信用曲线（CreditCurve）**  
  CDS 信用曲线分区；当前快照可能为空，加载器仍识别该类型。

### 历史行情（HIST）

按品种一份时间序列，供取价、历史波动率等使用。

- **债券价格**：净价、成交量和到期收益率。
- **外汇即期**：中间价，以及买卖价、开高低收等。
- **股票 / 基金现货**：收盘价与成交量。
- **股指期货 / 国债期货 / 商品期货**：合约行情。
- **贵金属现货与定价**：黄金等现货及定价序列。
- **理财产品净值**：财富管理产品价格序列（窗口内可能尚无行）。
- **利率指标定盘**：如 EFFR 等历史定盘。

### 静态辅助

估值、情景和映射用的参考表，与主索引放在同一目录。

- **债券条款（BOND_INFO）**：代码、到期日、票息、发行人、评级等。
- **分红（dividends）**：基金 / 股票除权除息。
- **工具分类**：产品大类与细类，供情景按分类冲击。
- **标的信息**：股票、基金、期货的静态字段（乘数、费率、税率等）。
- **映射与持仓**：交易代码与行情代码对照、业绩基准，以及部分基金持仓分解。
- **其它约定表**：国债期货可交割券、融资利率、含权债利率波动率等。

## 怎么用

克隆后，把数据根设为 `snapshots/` 的绝对路径（或相对工作簿的路径）。一日一份主索引：`MCP_MARKET_DATA_YYYYMMDD.json`。完整示例与字段说明见 [`snapshots/README.md`](snapshots/README.md)。

```python
import mcp
mgr = mcp.MRawMarketManager(r".../mcp_marketdata/snapshots")
yc = mgr.getYieldCurve("CNHDEPO", "20260826")
```
