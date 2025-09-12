import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from concurrent.futures import ThreadPoolExecutor, as_completed

from stockcharts.utils import date_utils
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
            dcc.Store(id='event-data-store'),
            
            dbc.Row([
                dbc.Col([
                    html.H3(id='app-name', children=f"{self.ticker} Stock Chart"),
                    dcc.Loading(
                        type="circle",
                        children=dcc.Graph(id='stock-chart', style={'height': '90vh'})
                    )
                ], width=9),
                dbc.Col([
                    dbc.Button(
                        "X", id='close-info-button', color="secondary", size="sm",
                        className="position-absolute top-0 end-0 m-2",
                        style={'display': 'none'}
                    ),
                    html.H3(id='info-date'),
                    html.Hr(),
                    html.P(id='info-content', style={'whiteSpace': 'pre-wrap'})
                ], width=3, className="position-relative"),
            ])
        ], fluid=True, className="p-4")

    def _setup_callbacks(self):
        @self.app.callback(
            [
                Output('stock-chart', 'figure'), 
                Output('event-data-store', 'data')
            ],
            [Input('app-name', 'n_clicks')]
        )
        def start_loading_and_fetch_data(n_clicks):
            """
            This callback is triggered on initial page load to fetch the raw data.
            It is a one-time, blocking operation.
            """
            price, events = self.data_manager.fetch_raw_data()
            processed_events = list(self.data_manager.process_events(events=events))
            chart_builder = ChartBuilder(price)
            fig = chart_builder.create_figure()

            return fig, processed_events


        @self.app.callback(
            [
                Output('info-date', 'children'),
                Output('info-content', 'children'), 
                Output('close-info-button', 'style')
            ],
            [Input('event-data-store', 'data')]
        )
        def process_and_display_todays_events(event_data):
            """ This callback is triggered when event-data-store is updated."""
            if not event_data:
                return "Today", "Waiting for data...", {'display': 'block'}
            todays_events = self.data_manager.day_events(events=event_data)            
            output_string = ""
            for event in todays_events:
                output_string += f"Time: {event['time']}\nContent: {event['content']}\n" + "-"*20 + "\n"

            return "Today", output_string or "No news for today.", {'display': 'none'}
        
        @self.app.callback(
            Output('info-date', 'children', allow_duplicate=True),
            Output('info-content', 'children', allow_duplicate=True),
            Output('close-info-button', 'style', allow_duplicate=True),
            Input('stock-chart', 'clickData'),
            Input('close-info-button', 'n_clicks'),
            State('event-data-store', 'data'),
            prevent_initial_call=True
        )
        def update_info_panel(clickData, close_clicks, all_events):
            """
            This callback is triggered by a chart click OR a close button click.
            """
            triggered_id = ctx.triggered_id

            # View for a specific day: when the chart is clicked
            if triggered_id == 'stock-chart' and clickData:
                clicked_date = clickData['points'][0]['x']
                clicked_date = date_utils.get_date(clicked_date)
                
                if all_events is None:
                    return f"{clicked_date}", "Loading...", {'display': 'block'}
                
                events_on_date = self.data_manager.day_events(events=all_events, date=clicked_date)                
                output_string = ""
                for event in events_on_date:
                    output_string += f"Time: {event['time']}\nContent: {event['content']}\n" + "-"*20 + "\n"
                
                return f"{clicked_date}", output_string or "No news for this day.", {'display': 'block'}
            
            # View for when the close button is clicked
            if triggered_id == 'close-info-button':
                todays_events = self.data_manager.day_events(all_events)                
                output_string = ""
                for event in todays_events:
                    output_string += f"Time: {event['time']}\nContent: {event['content']}\n" + "-"*20 + "\n"
                
                return "Today", output_string or "No news for today.", {'display': 'none'}



    def run(self, debug=True):
        self.app.run(debug=debug)