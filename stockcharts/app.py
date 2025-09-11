import dash
import dash.dcc as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import html

class StockChartApp:
    """The main application class."""
    def __init__(self, ticker="NVDA"):
        self.ticker = ticker
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
        self.figure = go.Figure()

        self.figure.update_layout(
            title="Chart Placeholder (No Data Loaded)",
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            plot_bgcolor='#111111', paper_bgcolor='#111111',
            font_color='white',
            annotations=[
                dict(
                    text="Interactive chart",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16)
                )
            ]
        )

        self._setup_layout()

    def _setup_layout(self):
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H3(id='app-name', children="NVDA Stock Chart", style={'height': '10vh'}),
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