import dash
from dash import dcc, html
import plotly.express as px
import requests
import pandas as pd  # don't forget to import pandas!

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

shipments = fetch_shipments()
print("Raw shipments data:", shipments)  # Debug output

df_shipments = pd.DataFrame(shipments)
print("DataFrame columns:", df_shipments.columns)
print("DataFrame head:\n", df_shipments.head())

# Add default lat/lon if missing
for idx, shipment in df_shipments.iterrows():
    if 'latitude' not in shipment or pd.isna(shipment['latitude']):
        df_shipments.at[idx, 'latitude'] = -1.9441  # Kigali latitude example
    if 'longitude' not in shipment or pd.isna(shipment['longitude']):
        df_shipments.at[idx, 'longitude'] = 30.0619  # Kigali longitude example

fig = px.scatter_mapbox(
    df_shipments,
    lat="latitude",
    lon="longitude",
    hover_name="id",
    zoom=6,
    mapbox_style="open-street-map",
)

app.layout = html.Div([
    html.H1("Digital Aid Tracker - Shipment Dashboard"),
    dcc.Graph(figure=fig),
])

if __name__ == "__main__":
    app.run_server(debug=True)
