# Portfolio Tracker

A simple, powerful net worth tracker that fetches live prices for your crypto and stock holdings. Works with any AI assistant to help you configure your portfolio.

## Quick Start

### 1. Install Dependencies

```bash
pip install requests pyyaml
```

### 2. Configure Your Portfolio

Open `portfolio.yaml` and add your holdings:

```yaml
portfolio_name: "My Portfolio"

crypto:
  bitcoin: 0.5
  ethereum: 2.0
  solana: 10

stocks:
  AAPL: 10
  TSLA: 5
  VOO: 20

cash:
  Bank Account: 5000
  USDC: 1000
```

**Or ask your AI assistant:** Just tell it what you own and it will update the config for you.

### 3. Run the Tracker

```bash
python tracker.py
```

## Usage

```bash
# Show portfolio summary (default)
python tracker.py

# Output as JSON (for apps/integrations)
python tracker.py --json

# Output as Markdown (for notes/docs)
python tracker.py --markdown

# Watch mode - auto-refresh every 60 seconds
python tracker.py --watch

# Watch mode - custom interval (30 seconds)
python tracker.py --watch 30
```

## Configuring Your Portfolio

### Using AI Assistant

Just tell your AI assistant what you own:

> "I have 0.5 Bitcoin, 100 shares of Tesla, and $5000 in my bank account"

The assistant will update `portfolio.yaml` for you.

### Manual Configuration

Edit `portfolio.yaml` directly:

**Crypto** - Use CoinGecko IDs (lowercase, hyphens for spaces):
- `bitcoin`, `ethereum`, `solana`, `dogecoin`, `cardano`, `ripple`
- `aave`, `uniswap`, `chainlink`, `avalanche-2`, `polygon-ecosystem-token`
- Find more at [coingecko.com](https://www.coingecko.com)

**Stocks** - Use standard ticker symbols (uppercase):
- `AAPL`, `TSLA`, `AMZN`, `GOOGL`, `MSFT`, `VOO`, `SPY`, etc.

**Cash** - Name your accounts, values are in USD:
- Bank accounts, stablecoins (USDC, USDT), money market, etc.

## Example Output

```
==========================================================================
MY PORTFOLIO - January 17, 2026 at 12:00 PM
==========================================================================

 CRYPTO
--------------------------------------------------------------------------
Asset               Price         Holdings              Value
--------------------------------------------------------------------------
BTC              $95,000             0.50           $47,500
ETH               $3,300             2.00            $6,600
SOL                 $180            10.00            $1,800
--------------------------------------------------------------------------
CRYPTO TOTAL                                        $55,900

 STOCKS & ETFs
--------------------------------------------------------------------------
Ticker              Price           Shares              Value
--------------------------------------------------------------------------
AAPL              $198.50            10.00            $1,985
TSLA              $437.50             5.00            $2,188
VOO               $636.00            20.00           $12,720
--------------------------------------------------------------------------
STOCK TOTAL                                         $16,893

 CASH & STABLECOINS
--------------------------------------------------------------------------
Account                                               Value
--------------------------------------------------------------------------
Bank Account                                         $5,000
USDC                                                 $1,000
--------------------------------------------------------------------------
CASH TOTAL                                           $6,000

==========================================================================
                                     CRYPTO:        $55,900 (71.7%)
                                STOCKS/ETFs:        $16,893 (21.7%)
                           CASH/STABLECOINS:         $6,000 (7.7%)
--------------------------------------------------------------------------
                             TOTAL NET WORTH        $78,793
==========================================================================
```

## Data Sources

- **Crypto prices**: [CoinGecko API](https://www.coingecko.com/api) (free, no API key required)
- **Stock prices**: Yahoo Finance (free, no API key required)

## Requirements

- Python 3.7+
- `requests` - HTTP requests
- `pyyaml` - YAML config parsing

## License

MIT License - Use freely, modify as needed.
