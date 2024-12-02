import dash
from dash import dcc, html, dash_table
import pandas as pd

# Sample Data
data_overview = {
    "Category": ["Stats Office", "Stats Office", "Energy", "Food", "Food", "Hotels"],
    "Market": ["UK", "UK", "Germany", "Spain", "UK", "UK"],
    "Name": ["RPI", "Price Quotes", "Strom Report", "Soysuper", "Tesco", "Trivago"],
    "Status": ["success", "success", "success", "failure", "success", "pending"]
}

failures = {
    "Category": ["Food", "Hotels"],
    "Market": ["Spain", "UK"],
    "Name": ["Soysuper", "Trivago"],
    "Reason": ["Dags/Tasks Failed", "Significantly less data parsed"],
}

pending_today = {
    "Category": ["Food"],
    "Market": ["UK"],
    "Name": ["Tesco"],
    "Start Time": ["08:00"],
    "End Time": ["10:00"]
}

updated_today = {
    "Category": ["Stats Office"],
    "Market": ["UK"],
    "Name": ["Price Quotes"],
    "Notes": ["Data updated successfully"]
}

success_aggregate = {"dt2": 70, "dt3": 85, "dt4": 91, "dt5": 98, "dt6": 70}

# Convert to DataFrames
df_overview = pd.DataFrame(data_overview)
df_failures = pd.DataFrame(failures)
df_pending = pd.DataFrame(pending_today)
df_updated = pd.DataFrame(updated_today)
df_success_agg = pd.DataFrame(list(success_aggregate.items()), columns=["Dataset", "Success Rate"])

# Dash App
app = dash.Dash(__name__)

# Style mappings for conditional formatting
def cell_color(status):
    if status == "success":
        return "green"
    elif status == "failure":
        return "red"
    elif status == "pending":
        return "purple"
    return "white"

# Apply styles to Overview table
overview_table_data = [
    {
        **row,
        "StatusColor": cell_color(row["Status"])
    }
    for row in df_overview.to_dict("records")
]

app.layout = html.Div([
    # Main Layout
    html.Div([
        # Left Section
        html.Div([
            html.H2("Overview"),
            dash_table.DataTable(
                id='overview-table',
                columns=[
                    {"name": i, "id": i} for i in ["Category", "Market", "Name"]
                ] + [{"name": "", "id": "StatusColor", "presentation": "markdown"}],
                data=[
                    {**row, "StatusColor": f"### ⬤ {row['Status']}"}
                    for row in overview_table_data
                ],
                style_data_conditional=[
                    {
                        "if": {"filter_query": f"{{Status}} = '{status}'", "column_id": "StatusColor"},
                        "backgroundColor": color,
                        "color": "white"
                     },{
}
}