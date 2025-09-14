import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ChartBuilder:
    """Builds the Plotly candlestick and volume chart."""
    def __init__(self, price_data: pd.DataFrame):
        self.price_data = price_data

    def create_figure(self) -> go.Figure:
        """Creates and returns a configured Plotly Figure object with price and volume subplots."""
        fig = go.Figure()

        hovertext_price = [
            f"<b>{row.name.strftime('%a, %b %d')}</b><br><br>"
            f"<b>Price:</b> <br>"
            f"<b>Open:</b> {row['Open']:.2f} USD <br>"
            f"<b>High:</b> {row['High']:.2f} USD <br>"
            f"<b>Low:</b> {row['Low']:.2f} USD<br>"
            f"<b>Close:</b> {row['Close']:.2f} USD<br>"
            for index, row in self.price_data.iterrows()
        ]
        
        # Candlestick trace for price data
        fig.add_trace(
            go.Candlestick(
                x=self.price_data.index,
                open=self.price_data['Open'],
                high=self.price_data['High'],
                low=self.price_data['Low'],
                close=self.price_data['Close'],
                name='Price', hovertext=hovertext_price,
                hoverinfo='text'
            )
        )
        
        # Bar trace for volume data
        fig.add_trace(
            go.Bar(
                x=self.price_data.index,
                y=self.price_data['Volume'],
                name='Volume',
                yaxis='y2',
                marker_color='#5A5A5A',
                opacity=0.2, hovertemplate="<b>Volume:</b> %{y}<extra></extra>"
            )
        )

        fig.update_layout(
            plot_bgcolor='#111111', paper_bgcolor='#111111',
            font_color='white', margin=dict(l=20, r=20, t=40, b=20),
            
            hovermode='x unified',
            
            xaxis=dict(
                rangeslider_visible=False,
                gridcolor='#444444',
                showgrid=True,
                showspikes=True,
                spikemode='across',
                spikecolor='#999999',
                spikethickness=1,
                linecolor='#444444'
            ),
            yaxis=dict(
                side='right',
                gridcolor='#444444',
                showgrid=True,
                showspikes=True,
                spikemode='across',
                spikecolor='#999999',
                spikethickness=1,
                linecolor='#444444'
            ),
            
            yaxis2=dict(
                title='Volume',
                side='left',
                overlaying='y',
                showgrid=False,
                showspikes=True,
                spikemode='across',
                spikecolor='#999999',
                spikethickness=1,
                linecolor='#444444',
                visible=False
            )
        )
        
        return fig
