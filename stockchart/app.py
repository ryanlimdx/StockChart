import dash
from dash import dcc, html, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc
import os
import plotly.graph_objects as go

from concurrent.futures import ThreadPoolExecutor, as_completed

from stockchart.utils import date_utils
from stockchart.components.chart import ChartBuilder
from stockchart.components.data_manager import DataManager

class StockChartApp:
    """The main application class."""
    def __init__(self, ticker="NVDA"):
        self.ticker = ticker
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
        self.data_manager = DataManager(ticker=ticker)
        self._setup_layout()
        self._setup_callbacks()

    def _setup_layout(self):
        """Set up the layout of the"""
        self.app.layout = dbc.Container([
            dcc.Store(id='event-data-store'),
            # Chart
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(
                            [   
                                dbc.Row([
                                    dbc.Col(
                                        html.Div(id='logo-image', style={
                                            'width': '24px',
                                            'height': '24px',
                                            'border-radius': '50%',
                                            'background-color': '#555555', # Placeholder
                                            'background-size': 'cover',
                                            'background-position': 'center',
                                            'background-repeat': 'no-repeat',
                                            'vertical-align': 'middle',
                                        }),
                                        width="auto",
                                    ),
                                    dbc.Col(
                                        html.P(f"{self.ticker} - 3 Month", className="mb-0 ms-2", style={'vertical-align': 'middle'}),
                                        width="auto"
                                    )
                                ], className="d-flex align-items-center mb-2"),
                                dcc.Loading(
                                    type="circle",
                                    children=dcc.Graph(id='stock-chart', style={'height': '90vh'})
                                )
                            ]
                        ), 
                        className="rounded-4 d-flex flex-column", 
                        style={
                            'background-color': '#111111', 
                            'height': '100%',
                            }
                    ),
                ], width=9,  style={'height': '100%', 'display': 'flex', 'flex-direction': 'column'}),
                # Information panel and App card
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(html.H3(id='info-date', children=html.B("Today"))),
                                        dbc.Col(
                                            dbc.Button("X", id='close-info-button', size="sm", className="ms-auto", style={'display': 'none'}),
                                            width="auto"
                                        )
                                    ],
                                    align="center",
                                    className="mb-3 flex-shrink-0"
                                ),
                                html.Div(
                                    id='info-content',
                                    style={'overflowY': 'auto'},
                                    children=[
                                        dbc.Card(
                                            dbc.CardBody(
                                                html.P("Loading events...", className="card-text text-center m-0")
                                            ),
                                            className="rounded-4 bg-secondary"
                                        )
                                    ]
                                )
                            ],
                            className="d-flex flex-column h-100"
                        ),
                        className="rounded-4 flex-grow-1",
                        style={'min-height': '0', 'height': '95%'}
                    ),
                    dbc.Button(
                        [
                            dcc.Loading(
                                id="loading-title",
                                type="circle",
                                children=html.H5(id='loading-title-text', children=html.B("StockChart"), className="text-center")
                            )
                        ],
                        id="loading-card", 
                        n_clicks=0,
                        className="mt-4 rounded-4", 
                        style={'height': '5%', 'cursor': 'pointer', 'background-color': '#303030', 'border': 'none', 'color': 'white'}
                    ),

                ], width=3,  style={'height': '100%', 'display': 'flex', 'flex-direction': 'column'}
                ),
            ], style={'height': '100%'})
        ], fluid=True, className="p-4 vh-100")

    def _create_event_cards(self, events):
        """Creates a list of styled Card components for events."""
        if not events:
            return [
                dbc.Card(
                    dbc.CardBody(
                        html.P("All caught up!", className="card-text text-center m-0")
                    ),
                    className="mb-3 rounded-4 bg-secondary"
                )
            ]

        event_cards = []
        for event in events:
            event_type_color = {
                "Macro News": "primary",
                "News": "success",
                "SEC Filing": "warning",
                "Insider Transaction": "info"
            }.get(event.get('type'), "#222529")

            content_lines = event.get('content', '').split('\n')
            content_with_breaks = []
            for i, line in enumerate(content_lines):
                if i > 0:
                    content_with_breaks.append(html.Br())
                content_with_breaks.append(line)

            card = dbc.Card(
                dbc.CardBody([
                    # Header
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Badge(event.get('type', 'Event'), color=event_type_color, className="me-1"),
                                width="auto"
                            ),
                            dbc.Col(
                                html.Small(event.get('time', ''), className="text-muted"),
                                className="text-end"
                            )
                        ],
                        align="center",
                        className="mb-2"
                    ),

                    # Title
                    html.H6(
                        event.get('title', 'No Title'),
                        className="mt-3 card-title fw-bold",
                        style={
                            'whiteSpace': 'nowrap',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis'
                        }
                    ),

                    # Content
                    html.P(
                        content_with_breaks,
                        className="card-text small text-muted mb-2"
                    ),

                    # Footer
                    html.A(
                        event.get('source', 'Read more'),
                        href=event.get('url', '#'),
                        target="_blank",
                        rel="noopener noreferrer",
                        className="card-link small"
                    )
                ]),
                className="mb-3 rounded-4 bg-secondary"
            )
            event_cards.append(card)
        return event_cards

    def _setup_callbacks(self):
        """Set up necessary callbacks for interactivity."""
        @self.app.callback(
            Output('logo-image', 'style'),
            Input('loading-card', 'n_clicks'),
        )
        def load_logo_url(n_clicks):
            """Loads the ticker logo URL."""
            logo_url = self.data_manager.load_logo()
            if logo_url:
                return {
                    'width': '24px',
                    'height': '24px',
                    'border-radius': '50%',
                    'background-image': f'url({logo_url})',
                    'background-size': 'cover',
                    'background-position': 'center',
                    'background-repeat': 'no-repeat',
                    'vertical-align': 'middle',
                }
            return no_update
        
        @self.app.callback(
            Output('stock-chart', 'figure'),
            Input('loading-card', 'n_clicks')
        )
        def load_price_chart(n_clicks):
            """This callback is triggered on page load for loading the price chart"""
            price = self.data_manager.load_price_data()
            chart_builder = ChartBuilder(price)
            fig = chart_builder.create_figure()
            return fig

        @self.app.callback(
            Output('event-data-store', 'data'),
            Output('loading-title-text', 'children'),
            Input('loading-card', 'n_clicks'),
        )
        def load_event_data(n_clicks):
            """This callback is triggered on page load for loading the events"""
            force_refresh = n_clicks is not None
            return self.data_manager.load_event_data(force_refresh=force_refresh), "StockChart"

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
            """This callback is triggered on refresh or pressing the close button"""
            triggered_id = ctx.triggered_id

            if event_data_input is None:
                return html.B("Today"), no_update, {'display': 'none'}
            
            if triggered_id == 'stock-chart' and clickData:
                clicked_date = clickData['points'][0]['x']
                clicked_date = date_utils.get_date(clicked_date)
                
                _, display_date, _ = date_utils.string_to_display(date_string=clicked_date)
                events_on_date = self.data_manager.day_events(events=all_events, date=clicked_date)
                event_cards = self._create_event_cards(events_on_date)
                
                return html.B(f"{display_date}"), event_cards, {'display': 'block'}
            
            todays_events = self.data_manager.day_events(events=event_data_input)
            event_cards = self._create_event_cards(todays_events)
            return html.B("Today"), event_cards, {'display': 'none'}

    def run(self, debug=True):
        """Entry point to run the app"""
        self.app.run(debug=debug)