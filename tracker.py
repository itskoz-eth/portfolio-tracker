#!/usr/bin/env python3
"""
Portfolio Tracker
-----------------
Fetches live prices for your crypto and stock holdings.
Configure your holdings in portfolio.yaml, then run this script.

Usage:
    python tracker.py              # Show portfolio summary
    python tracker.py --json       # Output as JSON
    python tracker.py --markdown   # Output as Markdown
    python tracker.py --watch      # Auto-refresh every 60 seconds
"""

import requests
import json
import yaml
import time
import os
import sys
from datetime import datetime
from typing import Dict, Optional, Any
import argparse

# =============================================================================
# CONFIGURATION
# =============================================================================

CONFIG_FILE = "portfolio.yaml"

# CoinGecko display name overrides (optional)
CRYPTO_DISPLAY_NAMES = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "dogecoin": "DOGE",
    "cardano": "ADA",
    "ripple": "XRP",
    "polkadot": "DOT",
    "chainlink": "LINK",
    "uniswap": "UNI",
    "aave": "AAVE",
    "avalanche-2": "AVAX",
    "polygon-ecosystem-token": "POL",
    "bittensor": "TAO",
    "hyperliquid": "HYPE",
    "sui": "SUI",
    "aptos": "APT",
    "arbitrum": "ARB",
    "optimism": "OP",
    "near": "NEAR",
    "cosmos": "ATOM",
    "litecoin": "LTC",
    "shiba-inu": "SHIB",
    "pepe": "PEPE",
}

# =============================================================================
# LOAD CONFIG
# =============================================================================

def load_config() -> Dict[str, Any]:
    """Load portfolio configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
    
    if not os.path.exists(config_path):
        print(f"Error: {CONFIG_FILE} not found!", file=sys.stderr)
        print("Create a portfolio.yaml file with your holdings.", file=sys.stderr)
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return {
        "name": config.get("portfolio_name", "My Portfolio"),
        "crypto": config.get("crypto", {}),
        "stocks": config.get("stocks", {}),
        "cash": config.get("cash", {}),
    }

# =============================================================================
# API FUNCTIONS
# =============================================================================

def fetch_crypto_prices(holdings: Dict[str, float]) -> Dict[str, Optional[float]]:
    """Fetch crypto prices from CoinGecko (free, no API key required)."""
    if not holdings:
        return {}
    
    prices = {}
    ids = ",".join(holdings.keys())
    
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        for coin_id in holdings.keys():
            if coin_id in data and "usd" in data[coin_id]:
                prices[coin_id] = data[coin_id]["usd"]
            else:
                prices[coin_id] = None
                print(f"Warning: Could not fetch price for {coin_id}", file=sys.stderr)
                
    except requests.RequestException as e:
        print(f"Error fetching crypto prices: {e}", file=sys.stderr)
        for coin_id in holdings.keys():
            prices[coin_id] = None
            
    return prices


def fetch_stock_prices(holdings: Dict[str, float]) -> Dict[str, Optional[float]]:
    """Fetch stock prices using Yahoo Finance chart API."""
    if not holdings:
        return {}
    
    prices = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    for symbol in holdings.keys():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = data.get("chart", {}).get("result", [])
            if result:
                meta = result[0].get("meta", {})
                price = meta.get("regularMarketPrice")
                if price is not None:
                    prices[symbol] = float(price)
                else:
                    prices[symbol] = None
                    print(f"Warning: No price for {symbol}", file=sys.stderr)
            else:
                prices[symbol] = None
                print(f"Warning: Empty result for {symbol}", file=sys.stderr)
                
        except requests.RequestException as e:
            prices[symbol] = None
            print(f"Warning: Error fetching {symbol}: {e}", file=sys.stderr)
        except (KeyError, IndexError, ValueError) as e:
            prices[symbol] = None
            print(f"Warning: Parse error for {symbol}: {e}", file=sys.stderr)
            
    return prices

# =============================================================================
# DISPLAY FUNCTIONS
# =============================================================================

def format_currency(value: float) -> str:
    """Format a number as currency."""
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:,.2f}M"
    elif abs(value) >= 1000:
        return f"${value:,.0f}"
    elif abs(value) >= 1:
        return f"${value:,.2f}"
    elif abs(value) >= 0.01:
        return f"${value:.4f}"
    else:
        return f"${value:.6f}"


def format_holdings(amount: float) -> str:
    """Format holdings amount."""
    if amount >= 1_000_000:
        return f"{amount/1_000_000:,.2f}M"
    elif amount >= 1000:
        return f"{amount:,.0f}"
    elif amount >= 1:
        return f"{amount:,.2f}"
    else:
        return f"{amount:.6f}"


def get_display_name(coin_id: str) -> str:
    """Get display name for a crypto asset."""
    return CRYPTO_DISPLAY_NAMES.get(coin_id, coin_id.upper().replace("-", " "))


def print_summary(config: Dict, crypto_prices: Dict, stock_prices: Dict):
    """Print a formatted summary of current prices and holdings."""
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    name = config["name"]
    
    print("\n" + "=" * 74)
    print(f"{name.upper()} - {timestamp}")
    print("=" * 74)
    
    # Crypto section
    if config["crypto"]:
        print("\n CRYPTO")
        print("-" * 74)
        print(f"{'Asset':<12} {'Price':>14} {'Holdings':>16} {'Value':>18}")
        print("-" * 74)
        
        crypto_total = 0
        for coin_id, holdings in config["crypto"].items():
            display = get_display_name(coin_id)
            price = crypto_prices.get(coin_id)
            
            if price is not None and holdings > 0:
                value = price * holdings
                crypto_total += value
                print(f"{display:<12} {format_currency(price):>14} {format_holdings(holdings):>16} {format_currency(value):>18}")
            elif holdings > 0:
                print(f"{display:<12} {'Error':>14} {format_holdings(holdings):>16} {'--':>18}")
        
        print("-" * 74)
        print(f"{'CRYPTO TOTAL':<12} {'':>14} {'':>16} {format_currency(crypto_total):>18}")
    else:
        crypto_total = 0
    
    # Stock section
    if config["stocks"]:
        print("\n STOCKS & ETFs")
        print("-" * 74)
        print(f"{'Ticker':<12} {'Price':>14} {'Shares':>16} {'Value':>18}")
        print("-" * 74)
        
        stock_total = 0
        for symbol, shares in config["stocks"].items():
            price = stock_prices.get(symbol)
            
            if price is not None and shares > 0:
                value = price * shares
                stock_total += value
                print(f"{symbol:<12} {format_currency(price):>14} {format_holdings(shares):>16} {format_currency(value):>18}")
            elif shares > 0:
                print(f"{symbol:<12} {'Error':>14} {format_holdings(shares):>16} {'--':>18}")
        
        print("-" * 74)
        print(f"{'STOCK TOTAL':<12} {'':>14} {'':>16} {format_currency(stock_total):>18}")
    else:
        stock_total = 0
    
    # Cash section
    if config["cash"]:
        print("\n CASH & STABLECOINS")
        print("-" * 74)
        print(f"{'Account':<30} {'Value':>18}")
        print("-" * 74)
        
        cash_total = 0
        for name, amount in config["cash"].items():
            if amount > 0:
                cash_total += amount
                print(f"{name:<30} {format_currency(amount):>18}")
        
        print("-" * 74)
        print(f"{'CASH TOTAL':<30} {format_currency(cash_total):>18}")
    else:
        cash_total = 0
    
    # Grand total
    print("\n" + "=" * 74)
    grand_total = crypto_total + stock_total + cash_total
    
    if crypto_total > 0:
        crypto_pct = (crypto_total / grand_total * 100) if grand_total > 0 else 0
        print(f"{'CRYPTO:':>45} {format_currency(crypto_total):>18} ({crypto_pct:.1f}%)")
    if stock_total > 0:
        stock_pct = (stock_total / grand_total * 100) if grand_total > 0 else 0
        print(f"{'STOCKS/ETFs:':>45} {format_currency(stock_total):>18} ({stock_pct:.1f}%)")
    if cash_total > 0:
        cash_pct = (cash_total / grand_total * 100) if grand_total > 0 else 0
        print(f"{'CASH/STABLECOINS:':>45} {format_currency(cash_total):>18} ({cash_pct:.1f}%)")
    
    print("-" * 74)
    print(f"{'TOTAL NET WORTH':>45} {format_currency(grand_total):>18}")
    print("=" * 74 + "\n")
    
    return grand_total


def output_json(config: Dict, crypto_prices: Dict, stock_prices: Dict):
    """Output prices as JSON for programmatic use."""
    output = {
        "timestamp": datetime.now().isoformat(),
        "portfolio_name": config["name"],
        "crypto": {},
        "stocks": {},
        "cash": {},
        "totals": {
            "crypto": 0,
            "stocks": 0,
            "cash": 0,
            "total": 0
        }
    }
    
    for coin_id, holdings in config["crypto"].items():
        display = get_display_name(coin_id)
        price = crypto_prices.get(coin_id)
        value = price * holdings if price else 0
        output["crypto"][display] = {
            "id": coin_id,
            "price": price,
            "holdings": holdings,
            "value": round(value, 2)
        }
        output["totals"]["crypto"] += value
    
    for symbol, shares in config["stocks"].items():
        price = stock_prices.get(symbol)
        value = price * shares if price else 0
        output["stocks"][symbol] = {
            "price": price,
            "shares": shares,
            "value": round(value, 2)
        }
        output["totals"]["stocks"] += value
    
    for name, amount in config["cash"].items():
        output["cash"][name] = {
            "amount": amount,
            "value": amount
        }
        output["totals"]["cash"] += amount
    
    output["totals"]["crypto"] = round(output["totals"]["crypto"], 2)
    output["totals"]["stocks"] = round(output["totals"]["stocks"], 2)
    output["totals"]["total"] = round(
        output["totals"]["crypto"] + output["totals"]["stocks"] + output["totals"]["cash"], 2
    )
    
    print(json.dumps(output, indent=2))


def output_markdown(config: Dict, crypto_prices: Dict, stock_prices: Dict):
    """Output as Markdown table."""
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    lines = [
        f"# {config['name']}",
        f"*Last updated: {timestamp}*",
        "",
    ]
    
    crypto_total = 0
    if config["crypto"]:
        lines.extend([
            "## Crypto",
            "| Asset | Price | Holdings | Value |",
            "|-------|------:|:--------:|------:|",
        ])
        
        for coin_id, holdings in config["crypto"].items():
            display = get_display_name(coin_id)
            price = crypto_prices.get(coin_id)
            if price and holdings > 0:
                value = price * holdings
                crypto_total += value
                lines.append(f"| {display} | {format_currency(price)} | {format_holdings(holdings)} | {format_currency(value)} |")
        
        lines.append(f"| **TOTAL** | | | **{format_currency(crypto_total)}** |")
        lines.append("")
    
    stock_total = 0
    if config["stocks"]:
        lines.extend([
            "## Stocks & ETFs",
            "| Ticker | Price | Shares | Value |",
            "|--------|------:|:------:|------:|",
        ])
        
        for symbol, shares in config["stocks"].items():
            price = stock_prices.get(symbol)
            if price and shares > 0:
                value = price * shares
                stock_total += value
                lines.append(f"| {symbol} | {format_currency(price)} | {format_holdings(shares)} | {format_currency(value)} |")
        
        lines.append(f"| **TOTAL** | | | **{format_currency(stock_total)}** |")
        lines.append("")
    
    cash_total = sum(config["cash"].values()) if config["cash"] else 0
    if config["cash"]:
        lines.extend([
            "## Cash & Stablecoins",
            "| Account | Value |",
            "|---------|------:|",
        ])
        
        for name, amount in config["cash"].items():
            if amount > 0:
                lines.append(f"| {name} | {format_currency(amount)} |")
        
        lines.append(f"| **TOTAL** | **{format_currency(cash_total)}** |")
        lines.append("")
    
    grand_total = crypto_total + stock_total + cash_total
    lines.extend([
        "---",
        f"## Total Net Worth: **{format_currency(grand_total)}**",
    ])
    
    print("\n".join(lines))


def watch_mode(config: Dict, interval: int = 60):
    """Continuously refresh prices."""
    print(f"Watch mode: refreshing every {interval} seconds. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            crypto_prices = fetch_crypto_prices(config["crypto"])
            stock_prices = fetch_stock_prices(config["stocks"])
            print_summary(config, crypto_prices, stock_prices)
            
            print(f"Next refresh in {interval} seconds... (Ctrl+C to stop)")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nWatch mode stopped.")

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Track your portfolio with live prices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python tracker.py              # Show portfolio summary
    python tracker.py --json       # Output as JSON
    python tracker.py --markdown   # Output as Markdown
    python tracker.py --watch      # Auto-refresh every 60 seconds
    python tracker.py --watch 30   # Auto-refresh every 30 seconds
        """
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--markdown", "-md", action="store_true", help="Output as Markdown")
    parser.add_argument("--watch", "-w", nargs="?", const=60, type=int, metavar="SECONDS",
                       help="Watch mode: auto-refresh (default: 60 seconds)")
    args = parser.parse_args()
    
    config = load_config()
    
    if args.watch:
        watch_mode(config, args.watch)
        return
    
    print("Fetching latest prices...", file=sys.stderr)
    
    crypto_prices = fetch_crypto_prices(config["crypto"])
    stock_prices = fetch_stock_prices(config["stocks"])
    
    if args.json:
        output_json(config, crypto_prices, stock_prices)
    elif args.markdown:
        output_markdown(config, crypto_prices, stock_prices)
    else:
        print_summary(config, crypto_prices, stock_prices)


if __name__ == "__main__":
    main()
