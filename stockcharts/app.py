import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from stockcharts.components.chart import ChartBuilder
from stockcharts.api.data_fetcher import DataFetcher

class StockChartApp:
    """The main application class."""
    def __init__(self, ticker="NVDA"):
        self.ticker = ticker
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
        
        chart = ChartBuilder(price_data=DataFetcher(ticker=ticker).get_price_history())
        self.figure = chart.create_figure()
        self._setup_layout()

    def _setup_layout(self):
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H3(id='app-name', children="Stock Chart", style={'height': '10vh'}),
                    dcc.Graph(id='stock-chart', figure=self.figure, style={'height': '90vh'})
                ], width=9),
                dbc.Col([
                    html.H3(id='info-date', children="Information"),
                    html.Hr(),
                    html.P(id='info-content', children="Content will appear here.", style={'whiteSpace': 'pre-wrap'})
                ], width=3),
            ])
        ], fluid=True)

    def run(self, debug=True):
        self.app.run(debug=debug)