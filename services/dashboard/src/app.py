import random
from datetime import datetime

import dash
import pandas
from dash import dcc, html
from dash.dependencies import Input, Output
from plotly import graph_objects

from database import engine
from settings import settings

GRAPH_INTERVAL = settings.graph_interval * 1000
PRICES_TABLE_NAME = settings.timescaledb_prices_table
TICKERS_TABLE_NAME = settings.timescaledb_tickers_table

COLORS = [
    "#e51e1e"
]


def get_stock_data(start: datetime, end: datetime, ticker=None):
    def format_date(dt: datetime) -> str:
        return dt.isoformat(timespec="seconds")

    query = f"SELECT * FROM {PRICES_TABLE_NAME} WHERE ts BETWEEN '{format_date(start)}' AND '{format_date(end)}'"

    if ticker:
        query += f" AND ticker = '{ticker}' "

    with engine.connect() as conn:
        return pandas.read_sql_query(query, conn)


def get_tickers():
    query = f"SELECT ticker FROM {TICKERS_TABLE_NAME}"
    with engine.connect() as conn:
        return pandas.read_sql_query(query, conn)


app = dash.Dash(
    __name__,
    title="Real-time stock changes",
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }],
)
app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H4(
                            "Stock changes",
                            className="app__header__title"
                        ),
                    ],
                    className="app__header__desc",
                ),
            ],
            className="app__header",
        ),
        html.Div(
            [
                html.P("Select a stock ticker"),
                dcc.Dropdown(
                    id="stock-ticker",
                    searchable=True,
                    options=[
                        {"label": ticker, "value": ticker}
                        for ticker in get_tickers()['ticker']
                    ],
                    value=get_tickers()['ticker'][0]
                ),
            ],
            className="app__selector",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H6(
                                    "Current price changes",
                                    className="graph__title"
                                )
                            ]
                        ),
                        dcc.Graph(id="stock-graph"),
                    ],
                    className="one-half column",
                )
            ],
            className="app__content",
        ),
        dcc.Interval(
            id="stock-graph-update",
            interval=int(GRAPH_INTERVAL),
            n_intervals=0
        ),
    ],
    className="app__container",
)


@app.callback(
    Output("stock-graph", "figure"),
    [
        Input("stock-ticker", "value"),
        Input("stock-graph-update", "n_intervals")
    ],
)
def generate_stock_graph(selected_ticker, _):
    data = []
    filtered_df = get_stock_data(
        datetime(1, 1, 1),
        datetime.now(),
        selected_ticker
    )
    groups = filtered_df.groupby(by="ticker")

    for group, data_frame in groups:
        data_frame = data_frame.sort_values(by=["ts"])
        trace = graph_objects.Scatter(
            x=data_frame.ts.tolist(),
            y=data_frame.price.tolist(),
            marker=dict(color=random.choice(COLORS)),
            name=group,
        )
        data.append(trace)

    layout = graph_objects.Layout(
        xaxis={"title": "Time"},
        yaxis={"title": "Price"},
        margin={"l": 70, "b": 70, "t": 70, "r": 70},
        hovermode="closest"
    )

    figure = graph_objects.Figure(data=data, layout=layout)
    return figure
