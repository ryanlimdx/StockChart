import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import os
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
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H3(id='app-name', children="StockChart")
                            ]
                        ), className="mb-4 rounded-4"
                    ),
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dcc.Loading(
                                    type="circle",
                                    children=dcc.Graph(id='stock-chart', style={'height': '90vh'})
                                )
                            ],
                        ), className="rounded-4", style={'background-color': '#111111'}
                    ),
                    
                ], width=9),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.H3(id='info-date', children="Today", className="mb-5")
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "X", id='close-info-button', color="secondary", size="sm",
                                            className="ms-auto", style={'display': 'none'}
                                        ),
                                    ),
                                ],
                                className="d-flex align-items-center justify-content-between"
                            ),
                            dcc.Loading(
                                type="circle",
                                children=html.Div(id='info-content')
                            )
                        ]),
                        className="rounded-4", style={'height': '100vh'}
                    ),
                    width=3,  className="position-relative"
                ),
            ])
        ], fluid=True, className="p-4")

    def _create_event_cards(self, events):
        """Creates a list of Card components for events."""
        event_cards = []
        if not events:
            card =dbc.Card(
                dbc.CardBody([
                    html.P("All caught up!", className="card-text")
                ]),
                className="mb-3 rounded-4 bg-secondary"
            )
            event_cards.append(card)
            return event_cards
        
        for event in events:
            card = dbc.Card(
                dbc.CardBody([
                    html.H5(f"Time: {event['time']}", className="card-title"),
                    html.P(f"Content: {event['content']}", className="card-text")
                ]),
                className="mb-3 rounded-4 bg-secondary"
            )
            event_cards.append(card)
        return event_cards

    def _setup_callbacks(self):
        @self.app.callback(
            Output('stock-chart', 'figure'),
            Input('app-name', 'n_clicks')
        )
        def load_price_chart(n_clicks):
            """This callback is triggered on page load for loading the price chart"""
            price = self.data_manager.fetch_price_data()
            chart_builder = ChartBuilder(price)
            fig = chart_builder.create_figure()
            return fig

        @self.app.callback(
            Output('event-data-store', 'data'),
            Input('app-name', 'n_clicks')
        )
        def load_event_data(n_clicks):
            """This callback is triggered on page load for loading the events"""
            events = self.data_manager.fetch_event_data()
            processed_events = list(self.data_manager.process_events(events=events))
            return processed_events

        @self.app.callback(
            [
                Output('info-date', 'children'),
                Output('info-content', 'children'), 
                Output('close-info-button', 'style')
            ],
            [
                Input('event-data-store', 'data'),
                Input('stock-chart', 'clickData'),
                Input('close-info-button', 'n_clicks')
            ],
            State('event-data-store', 'data')
        )
        def update_info_panel(event_data_input, clickData, close_clicks, all_events):
            triggered_id = ctx.triggered_id
            
            if triggered_id == 'stock-chart' and clickData:
                clicked_date = clickData['points'][0]['x']
                clicked_date = date_utils.get_date(clicked_date)
                
                events_on_date = self.data_manager.day_events(events=all_events, date=clicked_date)
                event_cards = self._create_event_cards(events_on_date)
                
                return f"{clicked_date}", event_cards, {'display': 'block'}
            
            todays_events = self.data_manager.day_events(events=event_data_input)
            event_cards = self._create_event_cards(todays_events)
            return "Today", event_cards, {'display': 'none'}

    def run(self, debug=True):
        self.app.run(debug=debug)