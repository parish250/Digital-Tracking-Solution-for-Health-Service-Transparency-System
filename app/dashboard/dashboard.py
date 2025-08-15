import dash
from dash import dcc, html
import plotly.express as px
import requests
import pandas as pd

app = dash.Dash(__name__)

def fetch_shipments():
    url = "http://localhost:8000/shipments/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching shipments: {e}")
        return []

# Fetch shipment data
shipments = fetch_shipments()
df_shipments = pd.DataFrame(shipments)

# Ensure latitude and longitude columns exist and fill missing values
if 'latitude' not in df_shipments.columns:
    df_shipments['latitude'] = -1.9441  # Kigali latitude
else:
    df_shipments['latitude'] = df_shipments['latitude'].fillna(-1.9441)

if 'longitude' not in df_shipments.columns:
    df_shipments['longitude'] = 30.0619  # Kigali longitude
else:
    df_shipments['longitude'] = df_shipments['longitude'].fillna(30.0619)

# KPI calculations
total_shipments = len(df_shipments)
delivered_shipments = df_shipments[df_shipments.get('status', '') == 'delivered'].shape[0] if 'status' in df_shipments.columns else 0
dispatched_shipments = df_shipments[df_shipments.get('status', '') == 'dispatched'].shape[0] if 'status' in df_shipments.columns else 0
delayed_shipments = df_shipments[df_shipments.get('status', '') == 'delayed'].shape[0] if 'status' in df_shipments.columns else 0

# Map figure (using scatter_map)
fig = px.scatter_map(
    df_shipments,
    lat="latitude",
    lon="longitude",
    hover_name="id" if "id" in df_shipments.columns else None,
    hover_data=["status"] if "status" in df_shipments.columns else None,
    zoom=6,
    title="Shipment Locations"
)

# Trend chart: Daily shipments over time (if 'created_at' exists)
trend_fig = None
if 'created_at' in df_shipments.columns:
    df_shipments['created_at'] = pd.to_datetime(df_shipments['created_at'])
    daily_counts = df_shipments.groupby(df_shipments['created_at'].dt.date).size().reset_index(name='shipments')
    trend_fig = px.line(daily_counts, x='created_at', y='shipments', title='Daily Shipments Over Time')

app.layout = html.Div([
    html.H1("Digital Aid Tracker - Shipment Dashboard"),
    html.Div([
        html.Div([
            html.H3("Total Shipments"),
            html.P(f"{total_shipments}")
        ], style={"padding": "10px", "border": "1px solid #ccc", "borderRadius": "5px", "width": "20%", "display": "inline-block", "marginRight": "2%"}),
        html.Div([
            html.H3("Delivered"),
            html.P(f"{delivered_shipments}")
        ], style={"padding": "10px", "border": "1px solid #ccc", "borderRadius": "5px", "width": "20%", "display": "inline-block", "marginRight": "2%"}),
        html.Div([
            html.H3("Dispatched"),
            html.P(f"{dispatched_shipments}")
        ], style={"padding": "10px", "border": "1px solid #ccc", "borderRadius": "5px", "width": "20%", "display": "inline-block", "marginRight": "2%"}),
        html.Div([
            html.H3("Delayed"),
            html.P(f"{delayed_shipments}")
        ], style={"padding": "10px", "border": "1px solid #ccc", "borderRadius": "5px", "width": "20%", "display": "inline-block"}),
    ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "30px"}),
    dcc.Graph(figure=fig),
    html.Br(),
    dcc.Graph(figure=trend_fig) if trend_fig else html.Div("No trend data available."),
])

if __name__ == "__main__":
    app.run(debug=True)