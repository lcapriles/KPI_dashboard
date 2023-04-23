import csv
import os
import shutil
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

#TODO: The configuration should be read from an ini in   ../conf
data_url = "https://raw.githubusercontent.com/plotly/datasets/master/supermarket_Sales.csv"
input_dir = 'data/in'
processed_dir = 'data/proc'

data_list=[]
for filename in os.listdir(input_dir): 
    if filename.endswith('.csv'):
        with open(os.path.join(input_dir, filename), newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            data_list = [[row[i] for i in [10,0,2,5,6,7,8,13]] for row in csvreader]  #Only specific columns...

#After processing the files, move them to the processed dir...
#shutil.move(os.path.join(input_dir, filename), os.path.join(processed_dir, filename))

pd_data_list = pd.DataFrame(data_list[1:], columns=data_list[0])
pd_data_list["Date"] = pd.to_datetime(pd_data_list["Date"])
pd_data_list["Unit price"] = pd.to_numeric(pd_data_list["Unit price"])
pd_data_list["Quantity"] = pd.to_numeric(pd_data_list["Quantity"])
pd_data_list["Revenue"] = pd_data_list["Unit price"] * pd_data_list["Quantity"] 
pd_data_list = pd_data_list.sort_values(by='Date')
fecha_min = pd_data_list['Date'].min()  #This have to be done before set_index...
fecha_max = pd_data_list['Date'].max()  #This have to be done before set_index...
pd_data_list = pd_data_list.sort_values("Date").set_index("Date")
pd_data_list.rename(columns={"Gross income": "Net Income"}, inplace=True)

#The dash app...            
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

daily_sales_number = (
    pd_data_list["Invoice ID"].groupby("Date").nunique().rename("Number of sales")
)   
title_font_size = 30
 
figure_daily_sales_number = px.line(
    daily_sales_number, title="Daily number of sales"
).update_layout(title_font_size=title_font_size)

m7d_mean_revenue = (
    pd_data_list["Revenue"].groupby("Date").sum().rolling(7, min_periods=7).mean()
)
 
figure_m7d_mean_revenue = px.line(
    m7d_mean_revenue, title="7-day moving average of daily revenue"
).update_layout(title_font_size=title_font_size)

#TODO: The layout shoul be in a layout or property file in ../conf
app.layout = html.Div([
        html.H1("Sales KPIs"),
        html.H2("Sales Dataset"),
        html.Ul([
                html.Li(f"Number of cities: {pd_data_list['City'].nunique()}"),
                html.Li(
                    f"Time period: {fecha_min} - {fecha_max}"
                ),
                html.Li(["Data Source: ", html.A(data_url, href=data_url)]),
            ]),
        dcc.Graph(figure=figure_daily_sales_number),
        dcc.Graph(figure=figure_m7d_mean_revenue),
])

if __name__ == "__main__":
    app.run_server(debug=True)
    
