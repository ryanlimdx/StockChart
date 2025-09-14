# 📈 StockChart

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An interactive web application for visualizing stock price data and relevant financial events.

## 📝 Overview

StockChart is an interactive stock price chart for a given ticker symbol, built with Python and Dash. Its key feature is the event timeline, which provides a curated list of key events—news, SEC filings, and insider transactions—for any date you select on the chart.

The application is designed to be run from the command line and viewed in a web browser, offering a fast and responsive user experience thanks to its asynchronous data fetching and smart caching mechanism.

## ✨ Key Features

* **Interactive Candlestick Chart:** Visualize historical price and volume data with an interactive chart powered by Plotly. Zoom, pan, and hover to inspect data points.
* **Dynamic Event Timeline:** Click on any day on the chart to see a list of significant events related to the stock for that date.
* **Smart Event Processing:** Automatically fetches and processes events from multiple sources to provide a clean, clutter-free timeline.
* **Data Caching:** Event data is cached locally to ensure a fast and efficient experience on subsequent loads or refreshes.
* **Customizable Ticker:** Easily specify any stock ticker via command-line arguments.
* **Debug Mode:** Run the application in either production or debug mode for development.

## 🛠️ Technology Stack

* **Backend:** Python
* **Web Framework:** Dash
* **Charting:** Plotly
* **Data Manipulation:** Pandas
* **Styling:** Dash Bootstrap Components
* **APIs:** [Finnhub](https://finnhub.io/docs/api/introduction), [AlphaVantage](https://www.alphavantage.co/documentation/)

## 🚀 Getting Started

### Installation

1.  Clone the repository to your local machine:
    ```bash
    git clone https://github.com/ryanlimdx/StockCharts.git
    ```
2.  Navigate to the project directory:
    ```bash
    cd StockChart
    ```
3.  Install the required dependencies from the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```
4.  Clone`.env.template` and rename it as `.env`. In the `.env` file, place the appropriate API keys
    ```bash
    FINNHUB_API_KEY = "YOUR_FINNHUB_API_KEY_HERE"
    ALPHA_VANTAGE_API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY_HERE"
    ```

### Usage

You can run the application directly from the command line using the `run.py` script. Once started, it will launch a local web server. Open your web browser and navigate to the address shown in the terminal (usually `http://127.0.0.1:8050`).

The script accepts two optional arguments: `--ticker` and `--debug`.

**Basic Usage**

To run the application with the default ticker (`NVDA`) and in production mode:
```bash
python run.py
```

**Specifying a Ticker**
To view a different stock chart, use the `--ticker` argument:
```bash
python run.py --ticker=GOOG
```
This will launch the application for Google's stock.

**Enabling Debug Mode**
By default, the application runs in production mode (`debug=False`). To enable Dash's debug mode for development, use the `--debug` flag:
```bash
python run.py --debug
```

**Combining Arguments**
You can combine both arguments to customize the application's behavior::
```bash
python run.py --ticker=TSLA --debug
```
This command will run the app for the ticker, `TSLA`, with debug mode enabled.

### 📂 Project Structure
```
StockChart/
├── stockcharts/
│   ├── api/          # Handles data fetching from external APIs.
│   ├── components/   # Contains core application logic like the ChartBuilder and DataManager.
│   ├── utils/        # Utility functions (e.g., date formatting).
│   └── app.py        # Main Dash application class, layout, and callbacks.
├── cache/            # Directory for storing cached event data.
├── requirements.txt  # Project dependencies.
├── .env.template     # Duplicate this, rename it to .env and include your API keys here
└── run.py            # The entry point script to run the application.
```

### 📄 License
This project is licensed under the MIT License. See the `LICENSE` file for details.
