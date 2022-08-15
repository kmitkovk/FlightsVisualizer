"""The main entry point of the Dash app"""

import logging
import os
import warnings

import dash
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, dcc, html

# from pythonjsonlogger import jsonlogger

import app_components

# This is how to suppress workings
warnings.filterwarnings("ignore", message=" only support")
# Suppress flask message that .env files are present
os.environ["FLASK_SKIP_DOTENV"] = "true"


dash_app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.LUX,
        dbc.icons.FONT_AWESOME,
    ],
    use_pages=True,
)

dash_app.title = "my app title"

dash_app.layout = html.Div(
    [
        app_components.header_element(),
        app_components.header_break(),
        dash.page_container,
    ]
)

# logHandler = logging.StreamHandler()
# formatter = jsonlogger.JsonFormatter(
#     fmt=(f"%(asctime)s" "%(levelname)s %(module)s %(funcName)s %(message)s %(name)s")
# )
# logHandler.setFormatter(formatter)

# app.logger.handlers = [logHandler]
# app.logger.setLevel(logging.INFO)
# app.logger.info("This is a info message.")

app = dash_app.server

if __name__ == "__main__":
    # app.logger.setLevel(logging.DEBUG)
    dash_app.run_server(debug=True)
