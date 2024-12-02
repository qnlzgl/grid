from dash import Dash, html, dash_table
import pandas as pd

# Sample data for each table
overview_data = {
    "Category": ["Stats Office", "Stats Office", "Energy", "Food", "Food", "Hotels"],
    "Market": ["UK", "UK", "Germany", "Spain", "UK", "UK"],
    "Name": ["RPI", "Price Quotes", "Strom Report", "Soysuper", "Tesco", "Trivago"],
}
df_overview = pd.DataFrame(overview_data)

as_of_data = {
    "As-Of": ["Lookback -30d", "Incl Stale"],
    "Latest": ["", ""],
}
df_as_of = pd.DataFrame(as_of_data)

table_of_contents_data = {
    "Section": [
        "Current Status",
        "Current Failures",
        "Pending Today",
        "Updated Today",
        "% Success History",
        "Datasets Status History",
    ]
}
df_table_of_contents = pd.DataFrame(table_of_contents_data)

current_status_data = {
    "Status": ["Success", "Failure", "Pending", "Total"],
    "Count": [5, 2, 1, 8],
}
df_current_status = pd.DataFrame(current_status_data)

current_failures_data = {
    "Category": ["Food", "Hotels"],
    "Market": ["UK", "UK"],
    "Name": ["Tesco", "Trivago"],
    "Reason": [
        "Dag(s)/Task(s) Failed",
        "Significantly less data ingested",
    ],
}
df_current_failures = pd.DataFrame(current_failures_data)

pending_today_data = {
    "Category": ["Food", "Stats Office"],
    "Market": ["Spain", "UK"],
    "Name": ["Soysuper", "RPI"],
    "Start Time": ["08:00", "08:15"],
    "End Time": ["08:30", "08:45"],
}
df_pending_today = pd.DataFrame(pending_today_data)

updated_today_data = {
    "Category": ["Energy", "Food"],
    "Market": ["Germany", "UK"],
    "Name": ["Strom Report", "Tesco"],
    "Notes": ["Daily data updated", "No significant changes"],
}
df_updated_today = pd.DataFrame(updated_today_data)

success_history_data = {
    "Dataset": ["dt2", "dt3", "dt4", "dt5", "dt6"],
    "Success %": [70, 85, 91, 98, 70],
}
df_success_history = pd.DataFrame(success_history_data)

datasets_status_history_data = {
    "Category": ["Energy", "Stats Office"],
    "Market": ["Germany", "UK"],
    "Name": ["Strom Report", "RPI"],
    "Status": ["Success", "Pending"],
}
df_datasets_status_history = pd.DataFrame(datasets_status_history_data)

# Initialize the Dash app
app = Dash(__name__)

app.layout = html.Div(
    style={"display": "flex", "flexDirection": "row", "gap": "20px", "padding": "20px"},
    children=[
        # Left Column: Overview
        html.Div(
            style={"flex": "1"},
            children=[
                html.H2("Overview"),
                dash_table.DataTable(
                    id="overview-table",
                    columns=[{"name": col, "id": col} for col in df_overview.columns],
                    data=df_overview.to_dict("records"),
                ),
            ],
        ),
        # Middle Column: As-Of and Table of Contents
        html.Div(
            style={"flex": "1"},
            children=[
                html.H2("As Of"),
                dash_table.DataTable(
                    id="as-of-table",
                    columns=[{"name": col, "id": col} for col in df_as_of.columns],
                    data=df_as_of.to_dict("records"),
                ),
                html.H2("Table of Contents"),
                dash_table.DataTable(
                    id="table-of-contents",
                    columns=[{"name": col, "id": col} for col in df_table_of_contents.columns],
                    data=df_table_of_contents.to_dict("records"),
                ),
            ],
        ),
        # Right Column: Other Tables
        html.Div(
            style={"flex": "2"},
            children=[
                html.H2("Current Status"),
                dash_table.DataTable(
                    id="current-status-table",
                    columns=[{"name": col, "id": col} for col in df_current_status.columns],
                    data=df_current_status.to_dict("records"),
                ),
                html.H2("Current Failures"),
                dash_table.DataTable(
                    id="current-failures-table",
                    columns=[{"name": col, "id": col} for col in df_current_failures.columns],
                    data=df_current_failures.to_dict("records"),
                ),
                html.H2("Pending Today"),
                dash_table.DataTable(
                    id="pending-today-table",
                    columns=[{"name": col, "id": col} for col in df_pending_today.columns],
                    data=df_pending_today.to_dict("records"),
                ),
                html.H2("Updated Today"),
                dash_table.DataTable(
                    id="updated-today-table",
                    columns=[{"name": col, "id": col} for col in df_updated_today.columns],
                    data=df_updated_today.to_dict("records"),
                ),
                html.H2("% Success History"),
                dash_table.DataTable(
                    id="success-history-table",
                    columns=[{"name": col, "id": col} for col in df_success_history.columns],
                    data=df_success_history.to_dict("records"),
                ),
                html.H2("Datasets Status History"),
                dash_table.DataTable(
                    id="datasets-status-history-table",
                    columns=[
                        {"name": col, "id": col} for col in df_datasets_status_history.columns
                    ],
                    data=df_datasets_status_history.to_dict("records"),
                ),
            ],
        ),
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)