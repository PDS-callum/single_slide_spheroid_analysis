from dash import Dash, dcc, html, Input, Output, State, callback
import cv2
import base64
import numpy as np
import datetime
from utils.general_utils import *
from dash_canvas.utils import array_to_data_url
import plotly.graph_objects as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },),
    dcc.Input(
        id="threshold_input",
        type="number",
        min=0,
        placeholder="threshhold",
        value=26,
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        }),
    dcc.Tabs([
        dcc.Tab(label='Thresholded image', children=[
            html.Div(id='thresholded-output-image-upload',children=[
                html.Img(id="thresholded_annotated_image",src="", style={"height": "1000px"})
            ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
        ]),
        dcc.Tab(label='Unthresholded image', children=[
            html.Div(id='unthresholded-output-image-upload',children=[
                html.Img(id="unthresholded_annotated_image",src="", style={"height": "1000px"})
            ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
        ]),
        dcc.Tab(label='Histogram', children=[
            dcc.Graph(id="histo", figure=go.Figure()),
            dcc.Graph(id="box", figure=go.Figure())
        ]),
    ]),
    dcc.Store(id='intermediate-value',data=None)
])

def proc_image(contents,threshold):
    in_img = data_uri_to_cv2_img(contents)
    in_img_string = array_to_data_url(in_img)
    gray_img = gray(in_img)
    gray_img_string = array_to_data_url(gray_img)
    blurred_img = blur(gray_img,11,type="median")
    blurred_img_string = array_to_data_url(blurred_img)
    circles_df = find_circles(
        image=blurred_img,
        method=cv2.HOUGH_GRADIENT, 
        dp=1, 
        minDist=100,
        param1=20, 
        param2=30, 
        minRadius=25, 
        maxRadius=100
    )
    annotated_img = plot_circles(
        in_img,
        circles_df,
        threshold=threshold
    )
    annotated_img_string = array_to_data_url(annotated_img)
    return [in_img,gray_img,blurred_img,annotated_img],[in_img_string,gray_img_string,blurred_img_string,annotated_img_string],circles_df

@callback(Output('intermediate-value', 'data'), 
          Input('upload-image', 'contents'),
          Input('intermediate-value', 'data'),
          State('upload-image', 'filename'),
          State('threshold_input', 'value'))
def clean_data(list_of_contents, data, list_of_names, threshold):
    # some expensive data processing step
    _, _, circles_df = proc_image(list_of_contents,threshold)
    circles_df["filename"] = list_of_names
    try:
        uploaded_df = pd.read_json(data)
        uploaded_df = pd.concat([uploaded_df,circles_df])
    except:
        uploaded_df = circles_df.copy()
    uploaded_df = uploaded_df.reset_index()
    return uploaded_df[["coordinate","radius","filename"]].to_json()

@callback([Output('thresholded_annotated_image', 'src'),Output('unthresholded_annotated_image', 'src'),Output('histo', 'figure'),Output('box', 'figure')],
          Input('upload-image', 'contents'),
          Input('intermediate-value', 'data'),
          State('upload-image', 'filename'),
          State('threshold_input', 'value'))
def update_output(list_of_contents, data, list_of_names, threshold):
    data = pd.read_json(data)
    _, thresholded_image_data, _ = proc_image(list_of_contents,threshold=threshold)
    _, unthresholded_image_data, _ = proc_image(list_of_contents,threshold=1000000000)
    
    fig_hist = go.Figure()
    fig_box = go.Figure()

    for filename in set(data.filename.values):
        fig_hist.add_trace(go.Histogram(x=data.query("filename == @filename").radius, name=filename,nbinsx=20))
        fig_box.add_trace(go.Box(x=data.query("filename == @filename").radius, name=filename))

    fig_hist.update_layout(
        title="Spheroid sizes",
        xaxis_title="Radius (pixels)",
        yaxis_title="Count",
        barmode='overlay'
    )
    fig_box.update_layout(
        title="Spheroid sizes",
        xaxis_title="Radius (pixels)"
    )

    fig_hist.update_traces(opacity=0.75)
    fig_box.update_traces(opacity=0.75)
    return thresholded_image_data[-1],unthresholded_image_data[-1],fig_hist,fig_box

if __name__ == '__main__':
    app.run(debug=True)