import argparse
from stockcharts.app import StockChartApp

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the StockChart Dash application.")
    parser.add_argument(
        '--ticker',
        type=str,
        default='NVDA',
        help='The stock ticker symbol to display (e.g., AAPL, GOOG). Defaults to NVDA.'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help='Enable debug mode. Defaults to True.'
    )
    args = parser.parse_args()

    app = StockChartApp(ticker=args.ticker)
    app.run(debug=args.debug)