import csv
import os
import shutil
import dash
from dash import dcc
from dash import html
from dash.dash_table import DataTable
import plotly.express as px
import pandas as pd

#TODO: The configuration should be read from an ini in   ../conf
data_url = "https://raw.githubusercontent.com/plotly/datasets/master/supermarket_Sales.csv"
input_dir = 'data/in'
processed_dir = 'data/proc'
i=0
data_list=[]
for filename in os.listdir(input_dir): 
    if filename.endswith('.csv'):
        with open(os.path.join(input_dir, filename), newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            if i != 0:  
                next(csvreader) #Only the header of the first file...       
            df = [[row[i] for i in [10,0,2,5,6,7,8,13,15]] for row in csvreader]  #Only specific columns...
            data_list += df
        i=1
    #After processing the file, move it to the processed dir...
    #TODO: move files...
    #shutil.move(os.path.join(input_dir, filename), os.path.join(processed_dir, filename))

pd_data_list = pd.DataFrame(data_list[1:], columns=data_list[0])
pd_data_list["Date"] = pd.to_datetime(pd_data_list["Date"])
pd_data_list["Unit price"] = pd.to_numeric(pd_data_list["Unit price"])
pd_data_list["Quantity"] = pd.to_numeric(pd_data_list["Quantity"])
pd_data_list["Tax 5%"] = pd.to_numeric(pd_data_list["Tax 5%"])
pd_data_list["Cost of goods sold"] = pd.to_numeric(pd_data_list["Cost of goods sold"])
pd_data_list["Gross income"] = pd.to_numeric(pd_data_list["Gross income"])
pd_data_list["Revenue"] = pd_data_list["Unit price"] * pd_data_list["Quantity"] 
pd_data_list.rename(columns={"Gross income": "Net Income"}, inplace=True)
pd_data_list = pd_data_list.sort_values(by='Date')
fecha_min = (pd_data_list['Date'].min()).strftime('%d/%m/%y')  #This have to be done before set_index...
fecha_max = (pd_data_list['Date'].max()).strftime('%d/%m/%y')  #This have to be done before set_index...
pd_data_list = pd_data_list.sort_values("Date").set_index("Date")


#The dash app...            
app = dash.Dash(__name__)

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

figure_product_line = px.pie(
    pd_data_list.groupby("Product line")["Revenue"].sum().reset_index(),
    names="Product line",
    values="Revenue",
    title="Product lines ratio",
).update_layout(title_font_size=title_font_size)
 
figure_revenue_bycity = px.bar(
    pd_data_list.groupby(["City"])["Revenue"].sum(), title="Revenue by city"
).update_layout(title_font_size=title_font_size)

sums = (
    pd_data_list[
        [
            "Revenue",
            "Tax 5%",
            "Cost of goods sold",
            "Net Income",
        ]
    ]
    .sum()
    .rename("Value")
    .reset_index()
    .rename(columns={"index": "Item"})
)

#TODO: The layout shoul be in a layout or property file in ../conf
sums_datatable = html.Div([
        html.Label(
            html.P("Revenue breakdown"),
            style={"font-size": f"{title_font_size}px", "font-color": "grey"},
        ),
        html.Br(),
        DataTable(
            data=sums.to_dict("records"),
            columns=[{"name": col, "id": col} for col in ["Item", "Value"]],
        ),
])

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
        html.Div([
            html.Table([
                html.Tr([  
                    html.Td(dcc.Graph(figure=figure_product_line),style={"verticalAlign":"baseline"}),
                    html.Td(dcc.Graph(figure=figure_revenue_bycity),style={"verticalAlign":"baseline"}),
                    html.Td(sums_datatable,style={"verticalAlign":"top"}),
                ]),
            ]),
        ]),        
        dcc.Graph(figure=figure_daily_sales_number),
        dcc.Graph(figure=figure_m7d_mean_revenue),
])

if __name__ == "__main__":
    app.run_server(debug=True)
    
