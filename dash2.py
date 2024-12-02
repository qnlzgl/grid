import dash
from dash import dash_table, html
import pandas as pd

# Read CSV data
data = pd.read_csv("your_file.csv")  # Replace with the extracted CSV filename

# App initialization
app = dash.Dash(__name__)

# Define styles for table cells
def style_data_conditional():
    return [
        {
            "if": {
                "filter_query": f"{{{col}}} = 0",
                "column_id": col,
            },
            "backgroundColor": "#f8d7da",  # Light red
            "color": "#842029",  # Dark red text
        }
        for col in data.columns if col.startswith("0")  # For day columns
    ]

# Define Dash layout
app.layout = html.Div([
    html.H1("Task Monitoring Dashboard", style={"textAlign": "center"}),
    dash_table.DataTable(
        id="dag-table",
        columns=[
            {"name": col, "id": col, "type": "text" if col not in data.select_dtypes("number").columns else "numeric"}
            for col in data.columns
        ],
        data=data.to_dict("records"),
        style_data={
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_cell={
            "textAlign": "center",
            "padding": "10px",
            "border": "1px solid #ddd",
        },
        style_header={
            "backgroundColor": "#007BFF",
            "color": "white",
            "fontWeight": "bold",
            "textAlign": "center",
        },
        style_table={"overflowX": "auto", "border": "thin lightgrey solid"},
        style_data_conditional=style_data_conditional(),
        page_size=10,  # Show 10 rows per page
    )
])

# Run app
if __name__ == "__main__":
    app.run_server(debug=True)