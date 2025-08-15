import dash
from dash import dcc, html, Input, Output, dash_table, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import json

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

# Configuration
API_BASE_URL = "http://localhost:8000"  # Update with your API URL

# Fetch data from API
def fetch_shipments():
    """Fetch shipments from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/shipments/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching shipments: {e}")
        return []

def fetch_feedbacks():
    """Fetch feedbacks from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/feedbacks/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching feedbacks: {e}")
        return []

# Generate mock data as fallback
def generate_mock_data():
    """Generate mock data for demonstration purposes"""
    np.random.seed(42)
    
    # Mock shipment data
    shipments = []
    statuses = ['In Transit', 'At Warehouse', 'At Distribution Center', 'Delivered', 'Delayed']
    locations = ['Kigali Warehouse', 'Nyagatare DC', 'Musanze DC', 'Huye DC', 'Rusizi DC']
    
    for i in range(50):
        shipment = {
            'id': f'SHP-{1000 + i}',
            'status': np.random.choice(statuses, p=[0.3, 0.2, 0.2, 0.2, 0.1]),
            'current_location': np.random.choice(locations),
            'origin': 'Central Warehouse Kigali',
            'destination': f'District {np.random.randint(1, 8)} DC',
            'items_count': np.random.randint(50, 500),
            'created_date': datetime.now() - timedelta(days=np.random.randint(0, 30)),
            'expected_delivery': datetime.now() + timedelta(days=np.random.randint(1, 10)),
            'transit_time': np.random.normal(48, 12),  # hours
            'lat': -1.9441 + np.random.normal(0, 0.5),
            'lon': 29.8739 + np.random.normal(0, 0.5),
            'responsible_person': f'Officer {np.random.randint(1, 10)}'
        }
        shipments.append(shipment)
    
    # Mock feedback data
    feedbacks = []
    feedback_types = ['Received', 'Not Received', 'Delayed', 'Damaged', 'Insufficient Quantity']
    
    for i in range(30):
        feedback = {
            'id': f'FB-{2000 + i}',
            'shipment_id': f'SHP-{1000 + np.random.randint(0, 50)}',
            'type': np.random.choice(feedback_types),
            'message': 'Sample feedback message',
            'created_date': datetime.now() - timedelta(days=np.random.randint(0, 30)),
            'district': f'District {np.random.randint(1, 8)}'
        }
        feedbacks.append(feedback)
    
    return shipments, feedbacks

# Calculate KPIs
def calculate_kpis(shipments, feedbacks):
    """Calculate key performance indicators"""
    df_shipments = pd.DataFrame(shipments)
    df_feedbacks = pd.DataFrame(feedbacks)
    
    total_dispatched = len(df_shipments)
    total_delivered = len(df_shipments[df_shipments['status'] == 'Delivered'])
    delayed_shipments = len(df_shipments[df_shipments['status'] == 'Delayed'])
    avg_transit_time = df_shipments['transit_time'].mean()
    issues_reported = len(df_feedbacks[df_feedbacks['type'].isin(['Not Received', 'Delayed', 'Damaged'])])
    
    return {
        'total_dispatched': total_dispatched,
        'total_delivered': total_delivered,
        'delivery_rate': (total_delivered / total_dispatched * 100) if total_dispatched > 0 else 0,
        'delayed_shipments': delayed_shipments,
        'avg_transit_time': avg_transit_time,
        'issues_reported': issues_reported
    }

# App Layout
app.layout = html.Div([
    html.Div([
        html.H1("Food Aid Tracking Dashboard", 
                style={'textAlign': 'center', 'color': '#2E86AB', 'marginBottom': 30}),
        html.P("Real-time monitoring of food aid distribution for transparency and accountability",
               style={'textAlign': 'center', 'color': '#666', 'fontSize': 16})
    ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'marginBottom': '20px'}),
    
    # Auto-refresh component
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # Update every 30 seconds
        n_intervals=0
    ),
    
    # KPI Cards Row
    html.Div(id='kpi-cards', style={'marginBottom': '30px'}),
    
    # Main dashboard content
    html.Div([
        # Left column - Map and Shipment List
        html.Div([
            html.H3("Live Tracking Map", style={'color': '#2E86AB'}),
            dcc.Graph(id='tracking-map'),
            
            html.H3("Recent Shipments", style={'color': '#2E86AB', 'marginTop': '30px'}),
            html.Div(id='shipment-table')
        ], className='six columns'),
        
        # Right column - Charts and Alerts
        html.Div([
            html.H3("Supply Chain Analytics", style={'color': '#2E86AB'}),
            dcc.Graph(id='trend-charts'),
            
            html.H3("Alerts & Anomalies", style={'color': '#2E86AB', 'marginTop': '30px'}),
            html.Div(id='alerts-panel'),
            
            html.H3("Feedback Overview", style={'color': '#2E86AB', 'marginTop': '30px'}),
            dcc.Graph(id='feedback-chart')
        ], className='six columns')
    ], className='row')
], style={'padding': '20px'})

# Callback for KPI cards
@app.callback(
    Output('kpi-cards', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_kpi_cards(n):
    shipments = fetch_shipments()
    feedbacks = fetch_feedbacks()
    kpis = calculate_kpis(shipments, feedbacks)
    
    cards = html.Div([
        # Total Dispatched
        html.Div([
            html.H4(f"{kpis['total_dispatched']}", style={'color': '#2E86AB', 'fontSize': '2.5em', 'margin': '0'}),
            html.P("Total Dispatched", style={'color': '#666', 'fontSize': '1.1em'})
        ], className='three columns', style={
            'backgroundColor': 'white', 'padding': '20px', 'textAlign': 'center',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'borderRadius': '8px', 'margin': '5px'
        }),
        
        # Delivery Rate
        html.Div([
            html.H4(f"{kpis['delivery_rate']:.1f}%", style={'color': '#A23B72', 'fontSize': '2.5em', 'margin': '0'}),
            html.P("Delivery Rate", style={'color': '#666', 'fontSize': '1.1em'})
        ], className='three columns', style={
            'backgroundColor': 'white', 'padding': '20px', 'textAlign': 'center',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'borderRadius': '8px', 'margin': '5px'
        }),
        
        # Average Transit Time
        html.Div([
            html.H4(f"{kpis['avg_transit_time']:.1f}h", style={'color': '#F18F01', 'fontSize': '2.5em', 'margin': '0'}),
            html.P("Avg Transit Time", style={'color': '#666', 'fontSize': '1.1em'})
        ], className='three columns', style={
            'backgroundColor': 'white', 'padding': '20px', 'textAlign': 'center',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'borderRadius': '8px', 'margin': '5px'
        }),
        
        # Issues Reported
        html.Div([
            html.H4(f"{kpis['issues_reported']}", style={'color': '#C73E1D', 'fontSize': '2.5em', 'margin': '0'}),
            html.P("Issues Reported", style={'color': '#666', 'fontSize': '1.1em'})
        ], className='three columns', style={
            'backgroundColor': 'white', 'padding': '20px', 'textAlign': 'center',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'borderRadius': '8px', 'margin': '5px'
        })
    ], className='row')
    
    return cards

# Callback for tracking map
@app.callback(
    Output('tracking-map', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_map(n):
    shipments = fetch_shipments()
    df = pd.DataFrame(shipments)
    
    # Color mapping for status
    color_map = {
        'Delivered': '#28a745',
        'In Transit': '#007bff',
        'At Warehouse': '#ffc107',
        'At Distribution Center': '#17a2b8',
        'Delayed': '#dc3545'
    }
    
    df['color'] = df['status'].map(color_map)
    
    fig = px.scatter_mapbox(
        df, lat='lat', lon='lon',
        color='status',
        hover_name='id',
        hover_data={'current_location': True, 'items_count': True, 'status': True},
        color_discrete_map=color_map,
        zoom=7,
        height=400
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(center=dict(lat=-1.9441, lon=29.8739)),
        showlegend=True,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    
    return fig

# Callback for shipment table
@app.callback(
    Output('shipment-table', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_shipment_table(n):
    shipments = fetch_shipments()
    df = pd.DataFrame(shipments)
    
    # Get recent shipments
    df_recent = df.head(10)
    df_recent['created_date'] = pd.to_datetime(df_recent['created_date']).dt.strftime('%Y-%m-%d %H:%M')
    
    return dash_table.DataTable(
        data=df_recent[['id', 'status', 'current_location', 'items_count', 'created_date']].to_dict('records'),
        columns=[
            {'name': 'Shipment ID', 'id': 'id'},
            {'name': 'Status', 'id': 'status'},
            {'name': 'Location', 'id': 'current_location'},
            {'name': 'Items', 'id': 'items_count'},
            {'name': 'Created', 'id': 'created_date'}
        ],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#2E86AB', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'filter_query': '{status} = Delayed'},
                'backgroundColor': '#f8d7da',
                'color': 'black',
            },
            {
                'if': {'filter_query': '{status} = Delivered'},
                'backgroundColor': '#d4edda',
                'color': 'black',
            }
        ]
    )

# Callback for trend charts
@app.callback(
    Output('trend-charts', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_trend_charts(n):
    shipments = fetch_shipments()
    feedbacks = fetch_feedbacks()
    
    df_shipments = pd.DataFrame(shipments)
    df_feedbacks = pd.DataFrame(feedbacks)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Shipments Trend', 'Delay Patterns by Location'),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # Daily shipments trend
    df_shipments['date'] = pd.to_datetime(df_shipments['created_date']).dt.date
    daily_shipments = df_shipments.groupby('date').size().reset_index(name='count')
    
    fig.add_trace(
        go.Scatter(
            x=daily_shipments['date'],
            y=daily_shipments['count'],
            mode='lines+markers',
            name='Daily Shipments',
            line=dict(color='#2E86AB')
        ),
        row=1, col=1
    )
    
    # Delay patterns by location
    delayed_by_location = df_shipments[df_shipments['status'] == 'Delayed'].groupby('current_location').size()
    
    fig.add_trace(
        go.Bar(
            x=delayed_by_location.index,
            y=delayed_by_location.values,
            name='Delayed Shipments',
            marker_color='#C73E1D'
        ),
        row=2, col=1
    )
    
    fig.update_layout(height=500, showlegend=False)
    return fig

# Callback for alerts panel
@app.callback(
    Output('alerts-panel', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_alerts_panel(n):
    shipments = fetch_shipments()
    df = pd.DataFrame(shipments)
    
    # Simple fraud detection rules
    alerts = []
    
    # Check for shipments delayed more than 3 days
    delayed_shipments = df[df['status'] == 'Delayed']
    if len(delayed_shipments) > 0:
        alerts.append({
            'type': 'warning',
            'message': f"{len(delayed_shipments)} shipments are currently delayed",
            'icon': '⚠️'
        })
    
    # Check for unusual transit times
    unusual_transit = df[df['transit_time'] > df['transit_time'].quantile(0.9)]
    if len(unusual_transit) > 0:
        alerts.append({
            'type': 'danger',
            'message': f"{len(unusual_transit)} shipments have unusually long transit times",
            'icon': '🚨'
        })
    
    if not alerts:
        alerts.append({
            'type': 'success',
            'message': "All systems operating normally",
            'icon': '✅'
        })
    
    alert_cards = []
    for alert in alerts:
        color = {'warning': '#FFC107', 'danger': '#DC3545', 'success': '#28A745'}[alert['type']]
        alert_cards.append(
            html.Div([
                html.Span(alert['icon'], style={'fontSize': '1.5em', 'marginRight': '10px'}),
                html.Span(alert['message'])
            ], style={
                'backgroundColor': color,
                'color': 'white',
                'padding': '15px',
                'marginBottom': '10px',
                'borderRadius': '5px'
            })
        )
    
    return html.Div(alert_cards)

# Callback for feedback chart
@app.callback(
    Output('feedback-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_feedback_chart(n):
    feedbacks = fetch_feedbacks()
    df_feedbacks = pd.DataFrame(feedbacks)
    
    feedback_counts = df_feedbacks['type'].value_counts()
    
    fig = px.pie(
        values=feedback_counts.values,
        names=feedback_counts.index,
        title="Feedback Distribution"
    )
    
    fig.update_layout(height=300)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)