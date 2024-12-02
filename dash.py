import dash
from dash import dcc, html, dash_table
import pandas as pd
import plotly.express as px

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

app.layout = html.Div([
    html.H1("Infrastructure Dashboard"),
    
    html.Div([
        html.H2("Overview"),
        dash_table.DataTable(
            id='overview-table',
            columns=[{"name": i, "id": i} for i in df_overview.columns],
            data=df_overview.to_dict('records'),
            style_table={'overflowX': 'auto'},
        ),
    ], style={'margin-bottom': '20px'}),
    
    html.Div([
        html.H2("Current Failures"),
        dash_table.DataTable(
            id='failures-table',
            columns=[{"name": i, "id": i} for i in df_failures.columns],
            data=df_failures.to_dict('records'),
            style_table={'overflowX': 'auto'},
        ),
    ], style={'margin-bottom': '20px'}),
    
    html.Div([
        html.H2("Pending Today"),
        dash_table.DataTable(
            id='pending-table',
            columns=[{"name": i, "id": i} for i in df_pending.columns],
            data=df_pending.to_dict('records'),
            style_table={'overflowX': 'auto'},
        ),
    ], style={'margin-bottom': '20px'}),
    
    html.Div([
        html.H2("Updated Today"),
        dash_table.DataTable(
            id='updated-table',
            columns=[{"name": i, "id": i} for i in df_updated.columns],
            data=df_updated.to_dict('records'),
            style_table={'overflowX': 'auto'},
        ),
    ], style={'margin-bottom': '20px'}),
    
    html.Div([
        html.H2("% Success Aggregate"),
        dcc.Graph(
            id='success-aggregate-bar',
            figure=px.bar(df_success_agg, x="Dataset", y="Success Rate", title="% Success Aggregate")
        ),
    ], style={'margin-bottom': '20px'}),
])

if __name__ == '__main__':
    app.run_server(debug=True)