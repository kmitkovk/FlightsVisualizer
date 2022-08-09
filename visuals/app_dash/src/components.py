"""A module for dash layout components."""

import dash
import dash_bootstrap_components as dbc
from dash import html


#%% Layout components
def header_element():
    """Returns the header for the whole page."""
    return dbc.Row(
        [
            dbc.Col(
                html.Img(src=dash.get_asset_url("logo.png"), className="page-logo"),
                className="logo-col",
                width="auto",
            ),
            dbc.Col(
                html.H4("Flights Visualizer", className="page-title"),
                className="title-col",
                width="auto",
            ),
            # PAGE SELECTION TABS
            dbc.Col(
                dbc.Nav(
                    [
                        dbc.NavItem(
                            dbc.NavLink("Map", href="/map", id="map-nav", active=False)
                        ),
                        dbc.NavItem(
                            dbc.NavLink(
                                "Grid", href="/grid", id="grid-nav", active=False
                            )
                        ),
                    ],
                    id="header-links",
                    horizontal="start",
                    className="header-links",
                ),
                width=True,
                className="navbar-col",
            ),
            dbc.Col(
                dbc.Row(
                    [
                        dbc.Col(
                            html.P(id="username-display", className="username-display"),
                            className="tight",
                            width=True,
                        ),
                        dbc.Col(
                            html.I(id="login-button2", className="fas fa-user-circle"),
                            className="heavy-padded-left",
                            width="auto",
                        ),
                    ],
                    align="center",
                    className="tight",
                ),
                width="auto",
                className="login-col",
            ),
            # This is commented out because of dbc incompatibility
            # login_modal(),
            dbc.Col(
                html.I(id="help-button", className="fas fa-info-circle"),
                width="auto",
                align="center",
                className="info-col",
            ),
            help_modal(),
            dbc.Col(
                html.H5("KMK", className="team-name"),
                className="team-info",
                width="auto",
                align="right",
            ),
        ],
        align="center",
        className="title-row",
    )


def header_break():
    return html.Div(
        children=[
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
        ]
    )


def username_display(user=None):
    if user is None:
        return [
            dbc.Row(
                dbc.Col("Please log in to use the app.", className="tight"),
                className="tight",
            ),
            html.Div(className="vertical-line"),
        ]
    else:
        return [
            dbc.Row(
                dbc.Col(
                    html.P(f"Welcome, {user}!", className="important-text"),
                    className="tight",
                ),
                className="tight",
            ),
            html.Div(className="vertical-line"),
            dbc.Row(
                dbc.Col(
                    html.P(
                        "Do you want to log in with a different user name?",
                        className="small-text",
                    ),
                    className="tight",
                ),
                className="padded-top",
            ),
        ]


def login_modal():
    """Returns the modal that prompts the user to log in."""
    return dbc.Modal(
        [
            dbc.ModalHeader("LOGIN"),
            dbc.ModalBody(
                dbc.Form(
                    [
                        dbc.FormGroup(
                            [
                                dbc.Label("Username", width=4),
                                dbc.Col(
                                    dbc.Input(
                                        type="text",
                                        id="username",
                                        className="card-input",
                                    ),
                                    width=8,
                                ),
                            ],
                            row=True,
                            style={"margin-bottom": "0px"},
                        ),
                        dbc.FormGroup(
                            [
                                dbc.Label("Password", width=4),
                                dbc.Col(
                                    dbc.Input(
                                        type="password",
                                        id="password",
                                        className="card-input",
                                    ),
                                    width=8,
                                ),
                            ],
                            row=True,
                            style={"margin-bottom": "0px"},
                        ),
                    ],
                    className="heavy-padded-top",
                ),
                className="modal-body",
            ),
            dbc.ModalFooter(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(id="login-status", className="login-status"),
                            width=9,
                            className="tight",
                        ),
                        dbc.Col(
                            dbc.Button(
                                "LOGIN",
                                id="login-button",
                                color="danger",
                                block=True,
                                className="login-button",
                            ),
                            width=3,
                            className="tight",
                        ),
                    ],
                    align="center",
                    className="tight",
                    style={"width": "100%"},
                ),
                className="modal-footer",
            ),
        ],
        id="login-modal",
        size="sm",
        is_open=False,
    )


def help_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(id="help-modal-header", className="modal-header"),
            dbc.ModalBody(
                html.P(id="help-modal-message", className="tight"),
                className="modal-body",
            ),
            dbc.ModalFooter(
                f"Please report any bugs or suggestions to the dashboard owner.",
                className="modal-footer",
            ),
        ],
        id="help-modal",
        size="md",
    )


def page_under_construction():
    return dbc.Row(
        dbc.Col(
            dbc.Container(
                [
                    html.H1("UNDER CONSTRUCTION", className="display-3"),
                    html.P(
                        "This page is currently still under construction.",
                        className="lead",
                    ),
                    html.Hr(className="my-2"),
                    html.P("Click the button below to return to the home page."),
                    dbc.Nav(
                        dbc.NavItem(dbc.NavLink("HOME", active=True, href="/")),
                        pills=True,
                    ),
                ]
            ),
            width=4,
            className="tight",
            align="center",
        ),
        className="very-heavy-padded-top",
        justify="center",
    )
