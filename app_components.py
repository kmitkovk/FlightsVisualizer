"""A module for dash layout components."""

import dash
import dash_bootstrap_components as dbc
from dash import html, Input, Output, State


#%% Layout components
def header_element():
    """Returns the header for the whole page."""
    return dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Img(
                                    src=dash.get_asset_url("logo.png"), height="35px"
                                ),
                            ),
                            dbc.Col(
                                dbc.Col(dbc.NavbarBrand("Outtahere", className="ms-2")),
                            ),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                # PAGE SELECTION TABS
                # dbc.Col(width=1),
                dbc.Collapse(
                    [
                        dbc.Col(
                            dbc.Nav(
                                [
                                    dbc.NavItem(
                                        dbc.NavLink(
                                            "Map",
                                            href="/",
                                            id="map-nav",
                                            active=False,
                                        )
                                    ),
                                    dbc.NavItem(
                                        dbc.NavLink(
                                            "Grid",
                                            href="/grid",
                                            id="grid-nav",
                                            active=False,
                                        )
                                    ),
                                ],
                                id="header-links",
                                horizontal="start",
                                # className="header-links",
                            ),
                        ),
                        # login_modal(), # This is commented out because of dbc incompatibility
                        user_buttons(),
                        help_button(),
                        help_modal(),
                        # creator_info(),
                    ],
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                ),
            ],
            # align="center",
            # className="title-row",
        ),
        style={
            "paddingTop": "0.5rem",
            "paddingBottom": "0.5rem",
            "z-index": "1",
            "position": "fixed",
            "width": "-webkit-fill-available",
        },
        color="dark",
        dark=True,
    )


# add callback for toggling the collapse on small screens
@dash.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


def header_break():
    return html.Div(
        children=[
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
        ]
    )


def user_buttons():
    return dbc.Col(
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
    )


def creator_info():
    return dbc.Col(
        html.H5("KMK", className="team-name"),
        className="team-info",
        width="auto",
        align="right",
    )


def help_button():
    return dbc.Col(
        html.I(id="help-button", className="fas fa-info-circle"),
        width="auto",
        align="center",
        className="info-col",
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
