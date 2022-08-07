import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, dash_table, html

dash.register_page(__name__)

df = pd.read_csv("data/sample.csv").round(2)

layout = dbc.Container(
    [
        html.H1(children="Subpage 2"),
        dbc.Label("Click cell table:"),
        dash_table.DataTable(
            df.to_dict("records"),
            [{"name": i, "id": i} for i in df.columns],
            id="tbl",
            style_data_conditional=[
                {
                    "if": {
                        "filter_query": "{{{}}} >= {}".format(col, value),
                        "column_id": col,
                    },
                    "backgroundColor": "#B10DC9",
                    "color": "white",
                }
                for (col, value) in df.quantile(0.9).iteritems()
            ],
        ),
        dbc.Alert(id="tbl_out"),
    ]
)


@dash.callback(Output("tbl_out", "children"), Input("tbl", "active_cell"))
def update_graphs(active_cell):
    return str(active_cell) if active_cell else "Click the table"
