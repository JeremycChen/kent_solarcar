from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

# Assuming static values for demonstration
metrics = {
    'Speed': 120,  # km/h
    'Distance': 350,  # km
    'Temperature': 25,  # Celsius
    'Time': '2:15:30',  # hh:mm:ss
    'Battery': 85,  # Percentage
    'Lap Count': 5
}

app = Dash(__name__)

# Creating a simple line chart for demonstration
fig = px.line(x=[1, 2, 3], y=[1, 3, 2], title="Sample Graph")

app.layout = html.Div([
    html.H1('Dashboard', style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.H3(f"Speed: {metrics['Speed']} km/h", style={'fontSize': 24}),
            dcc.Graph(figure=fig, config={'displayModeBar': False})
        ], className="four columns"),
        html.Div([
            html.H3(f"Distance: {metrics['Distance']} km"),
            dcc.Graph(figure=fig, config={'displayModeBar': False})
        ], className="four columns"),
        html.Div([
            html.H3(f"Temperature: {metrics['Temperature']}°C"),
            dcc.Graph(figure=fig, config={'displayModeBar': False})
        ], className="four columns"),
    ], className="row"),
    html.Div([
        html.Div([
            html.H3(f"Time: {metrics['Time']}"),
            dcc.Graph(figure=fig, config={'displayModeBar': False})
        ], className="four columns"),
        html.Div([
            html.H3(f"Battery: {metrics['Battery']}%"),
            dcc.Graph(figure=fig, config={'displayModeBar': False})
        ], className="four columns"),
        html.Div([
            html.H3(f"Lap Count: {metrics['Lap Count']}"),
            dcc.Graph(figure=fig, config={'displayModeBar': False})
        ], className="four columns"),
    ], className="row")
], style={'columnCount': 2, 'width': '100%', 'height': '50vh'})

if __name__ == '__main__':
    app.run_server(debug=True)