from dash import Dash, html, callback, Input, Output, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import dash_ag_grid as dag
import pandas as pd

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.read_csv('./assets/sales_data_sample.csv')

# print(df.columns)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Product Sales Dashboard')
        ], width=12)
    ], className='mb-3'),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(df.PRODUCTLINE.unique(), id='product-dropdown', placeholder='Select A Product')
        ], width=6, className='mb-3'),
        dbc.Col([
            dcc.Dropdown(df.QTR_ID.unique(), id='quarter-dropdown', placeholder='Select A Quarter')
        ], width=6, className='mb-3'),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5('Total Revenue', className='card-title'),
                    html.H2(id='total_revenue', style={'textAlign':'center'})
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5('Number of Orders', className='card-title'),
                    html.H2(id='total_orders', style={'textAlign':'center'})
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5('Average Order Amount', className='card-title'),
                    html.H2(id='avg_order_amt', style={'textAlign':'center'})
                ])
            ])
        ], width=4)

    ], className='mb-3'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5('Product Chart', className='card-title'),
                    dcc.Graph(id='sales_by_product')
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5('Sales By Country', className='card-title'),
                    dcc.Graph(id='sales_by_country')
                ])
            ])
        ], width=6)
    ], className='mb-3'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4('Products Table', className='card-title'),
                    dag.AgGrid(
                        id='products_datatable',
                        rowData=df.to_dict('records'),
                        columnDefs=[{'field': i } for i in ['ORDERNUMBER', 'PRODUCTLINE', 'SALES', 'QTR_ID', 'QUANTITYORDERED']],
                        columnSize='sizeToFit'
                    )
                ])
            ])
        ])
    ], className='mb-5')

], className='mt-3')

@callback(
    Output('total_revenue', 'children'),
    [Input('product-dropdown', 'value'),
    Input('quarter-dropdown', 'value')]
)
def update_total_revenue(selected_product, selected_quarter):
    filtered_df = df.copy()

    if selected_product:
        filtered_df = filtered_df[filtered_df['PRODUCTLINE'] == selected_product]

    if selected_quarter:
        filtered_df = filtered_df[filtered_df['QTR_ID'] == selected_quarter]

    return f"${filtered_df['SALES'].sum():,.0f}"

@callback(
    Output('total_orders', 'children'),
    [Input('product-dropdown', 'value'),
     Input('quarter-dropdown', 'value')]
)
def update_total_orders(selected_product, selected_quarter):
    filtered_df = df.copy()

    if selected_product:
        filtered_df = filtered_df[filtered_df['PRODUCTLINE'] == selected_product]

    if selected_quarter:
        filtered_df = filtered_df[filtered_df['QTR_ID'] == selected_quarter]

    return filtered_df['ORDERNUMBER'].nunique()

@callback(
    Output('avg_order_amt', 'children'),
    [Input('product-dropdown', 'value'),
     Input('quarter-dropdown', 'value')]
)
def update_avg_order_amt(selected_product, selected_quarter):
    filtered_df = df.copy()

    if selected_product:
        filtered_df = filtered_df[filtered_df['PRODUCTLINE'] == selected_product]

    if selected_quarter:
        filtered_df = filtered_df[filtered_df['QTR_ID'] == selected_quarter]

    return f"${filtered_df['SALES'].mean():,.0f}"

@callback(
    Output('sales_by_product', 'figure'),
    Input('quarter-dropdown', 'value')
)
def update_sales_by_product(selected_quarter):
    filtered_df = df.copy()

    if selected_quarter:
        filtered_df = filtered_df[filtered_df['QTR_ID'] == selected_quarter]
    
    fig = px.bar(
        filtered_df.groupby('PRODUCTLINE')['SALES'].sum().reset_index().sort_values(by='SALES', ascending=False),
        x='PRODUCTLINE',
        y='SALES'
    )

    return fig

@callback(
    Output('sales_by_country', 'figure'),
    [Input('product-dropdown', 'value'),
     Input('quarter-dropdown', 'value')]
)
def update_sales_by_country(selected_product, selected_quarter):
    filtered_df = df.copy()

    if selected_product:
        filtered_df = filtered_df[filtered_df['PRODUCTLINE'] == selected_product]

    if selected_quarter:
        filtered_df = filtered_df[filtered_df['QTR_ID'] == selected_quarter]
    
    fig = px.pie(
        filtered_df,
        values='SALES',
        names='COUNTRY',
    )

    return fig

@callback(
    Output('products_datatable', 'rowData'),
    [Input('product-dropdown', 'value'),
     Input('quarter-dropdown', 'value')]
)
def update_products_datatable(selected_product, selected_quarter):
    columns_to_show = ['ORDERNUMBER', 'QUANTITYORDERED', 'SALES', 'QTR_ID', 'PRODUCTLINE']
    filtered_df = df[columns_to_show].copy()

    if selected_product:
        filtered_df = filtered_df[filtered_df['PRODUCTLINE'] == selected_product]

    if selected_quarter:
        filtered_df = filtered_df[filtered_df['QTR_ID'] == selected_quarter]

    final_df = filtered_df.groupby(['ORDERNUMBER','PRODUCTLINE']).agg({
        'SALES': 'sum',
        'QUANTITYORDERED':'first',
        'QTR_ID':'first'}).reset_index().round(2)

    return final_df.to_dict('records')





if __name__=='__main__':
    app.run(debug=True)
