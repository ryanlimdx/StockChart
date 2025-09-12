import plotly.graph_objects as go
import pandas as pd
import json
from typing import List, Dict, Any

class ChartBuilder:
    """Builds the Plotly candlestick chart from processed data."""
    def __init__(self, price_data: pd.DataFrame):
        self.price_data = price_data

    def create_figure(self) -> go.Figure:
        """Creates and returns a configured Plotly Figure object."""
        fig = go.Figure()
        fig.add_trace(
            go.Candlestick(
                x=self.price_data.index,
                open=self.price_data['Open'], high=self.price_data['High'],
                low=self.price_data['Low'], close=self.price_data['Close'],
                name='Price'
            )
        )

        fig.update_layout(
            title=f"NVDA Stock Price (Last 3 Months)",
            xaxis_rangeslider_visible=False,
            plot_bgcolor='#111111', paper_bgcolor='#111111',
            font_color='white', margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(gridcolor='#444444', visible=False),
            yaxis=dict(gridcolor='#444444', title='Price (USD)', side='right'),

            hovermode='x',

        )

        return fig