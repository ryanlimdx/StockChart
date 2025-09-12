import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from concurrent.futures import ThreadPoolExecutor, as_completed

from stockcharts.components.chart import ChartBuilder
from stockcharts.components.data_manager import DataManager

class StockChartApp:
    """The main application class."""
    def __init__(self, ticker="NVDA"):
        self.ticker = ticker
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
        self.data_manager = DataManager(ticker=ticker)
        self._setup_layout()
        self._setup_callbacks()

    def _setup_layout(self):
        self.app.layout = dbc.Container([
            dcc.Store(id='raw-data-store'),
            dcc.Store(id='generator-store'),
            
            dbc.Row([
                dbc.Col([
                    html.H3(id='app-name', children=f"{self.ticker} Stock Chart", style={'height': '10vh'}),
                    html.Div(id='chart-container', children=[
                        # Loading spinner and placeholder
                        html.Div(
                            id='loading-div',
                            children=[
                                dcc.Loading(
                                    type="circle",
                                    children=html.Div(id="loading-output", children=html.P("Loading data..."))
                                )
                            ],
                            style={'display': 'block'}
                        ),
                        # Chart component
                        dcc.Graph(id='stock-chart', figure=go.Figure(), style={'display': 'none', 'height': '90vh'})
                    ]),
                ], width=9),
                dbc.Col([
                    html.H3(children="Information", style={'height': '10vh'}),
                    html.Hr(),
                    html.P(id='info-content', children="Content will appear here.", style={'whiteSpace': 'pre-wrap'}),
                    html.Div(id='processing-spinner', style={'display': 'none'}, children=[
                        dcc.Loading(type="circle", children=html.Div(html.P("Processing events...")))
                    ])
                ], width=3),
            ])
        ], fluid=True, className="p-4")

    def _setup_callbacks(self):
        @self.app.callback(
            [
                Output('loading-div', 'style'), 
                Output('stock-chart', 'style'), 
                Output('stock-chart', 'figure'), 
                Output('raw-data-store', 'data')
            ],
            [Input('app-name', 'n_clicks')]
        )
        def start_loading_and_fetch_data(n_clicks):
            """
            This callback is triggered on initial page load to fetch the raw data.
            It is a one-time, blocking operation.
            """
            price, events = self.data_manager.fetch_raw_data()
            chart_builder = ChartBuilder(price)
            fig = chart_builder.create_figure()

            return {'display': 'none'}, {'display': 'block', 'height': '90vh'}, fig, events

        @self.app.callback(
            [
                Output('info-content', 'children'), 
                Output('processing-spinner', 'style')
            ],
            [Input('raw-data-store', 'data')]
        )
        def process_and_display_todays_events(raw_data):
            """ This callback is triggered when raw-data-store's data property is updated."""
            if not raw_data:
                return "Waiting for data...", {'display': 'block'}

            event_gen = self.data_manager.todays_events(raw_data)
            todays_events = list(event_gen)
            
            if len(todays_events) > 5:
                sorted_events = sorted(todays_events, key=lambda x: int(x['importance_rank']), reverse=True)
                todays_events = sorted_events[:5]

            output_string = ""
            for event in todays_events:
                output_string += f"Date: {event['date']}\n"
                output_string += f"Type: {event['type']}\n"
                output_string += f"Content: {event['content']}\n"
                output_string += "-" * 20 + "\n"

            # Return the final string and stop the spinner
            return output_string, {'display': 'none'}


    def run(self, debug=True):
        self.app.run(debug=debug)