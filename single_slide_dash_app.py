from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import cv2
import base64
import numpy as np
import datetime
from utils.general_utils import *
from dash_canvas.utils import array_to_data_url
import plotly.graph_objects as go
import json
import pandas as pd

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Upload(
        id="upload-image",
        children=html.Div([
            "Drag and Drop or ",
            html.A("Select Files")
        ]),
        style={
            "width": "100%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px"
        }),
    dcc.Input(
        id="threshold_input",
        type="number",
        min=0,
        placeholder="threshhold",
        debounce=True,
        value=26,
        style={
            "width": "80%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px"
        }),
    html.Button(
        "Find circles...", 
        id="submit_threshold", 
        n_clicks=0,
        style={
            "width": "18%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderRadius": "5px",
            "textAlign": "right",
            # "margin": "10px"
        }),
    dcc.Tabs([
        dcc.Tab(label="Original image", children=[
            html.Div(id="output-image-upload",children=[
                html.Img(id="image",src="", style={"height": "1000px"})
            ], style={"display": "flex", "justify-content": "center", "align-items": "center"})
        ]),
        dcc.Tab(label="Thresholded image", children=[
            html.Div(id="thresholded-output-image-upload",children=[
                html.Img(id="thresholded_annotated_image",src="", style={"height": "1000px"})
            ], style={"display": "flex", "justify-content": "center", "align-items": "center"})
        ]),
        dcc.Tab(label="Unthresholded image", children=[
            html.Div(id="unthresholded-output-image-upload",children=[
                html.Img(id="unthresholded_annotated_image",src="", style={"height": "1000px"})
            ], style={"display": "flex", "justify-content": "center", "align-items": "center"})
        ]),
        dcc.Tab(label="Histogram", children=[
            dcc.Graph(id="histo", figure=go.Figure()),
            dcc.Graph(id="box", figure=go.Figure())
        ])
    ]),
    dcc.Store(id="data_store",data=json.dumps({"filename":"","threshold":26})),
    dcc.Store(id="image_data_store",data=json.dumps({"filename":[]})),
    dcc.Store(id="current_image_data",data=None)
])

@callback(
        Output("data_store","data"),
        Input("threshold_input","value"),
        State("data_store","data"),
        prevent_initial_call=True
)
def update_threshold(
    threshold,
    data_store
):
    data_store = json_to_dict(data_store)
    data_store["threshold"] = threshold
    print(data_store)
    return json.dumps(data_store)

@callback([Output("image","src"), Output("data_store","data"), Output("image_data_store","data")],
          [Input("upload-image", "contents")],
          [State("upload-image", "filename"), State("data_store","data"), State("image_data_store","data")],
          prevent_initial_call=True)
def push_image(
    contents,
    filename,
    data_store,
    image_data_store
):
    data_store = json_to_dict(data_store)
    data_store["filename"] = filename
    image_data_store = pd.DataFrame(json_to_dict(image_data_store))
    if filename not in image_data_store.filename:
        circles_df = proc_image(contents,data_store["threshold"])
        circles_df["filename"] = filename
        print(image_data_store)
        image_data_store = pd.concat([image_data_store,circles_df]).reset_index(drop=True)
        print(image_data_store)
    print(data_store)
    return contents, json.dumps(data_store), image_data_store.to_json()

@callback([Output("thresholded_annotated_image","src"),Output("unthresholded_annotated_image","src"),Output("histo","figure"),Output("box","figure")],
          [Input("submit_threshold","n_clicks")],
          [State("image","src"), State("data_store","data"), State("image_data_store","data")])
def push_circles(
    n_clicks,
    contents,
    data_store,
    image_data_store
):
    data_store = json_to_dict(data_store)
    filename = data_store["filename"]
    image_data_store = pd.DataFrame(json_to_dict(image_data_store))
    current_df = image_data_store.query("filename == @filename").copy()
    thresholded_image = draw_circles(contents,current_df,data_store["threshold"])
    unthresholded_image = draw_circles(contents,current_df,99999999999999)
    
    fig_hist = go.Figure()
    fig_box = go.Figure()

    for filename in set(image_data_store.filename.values):
        fig_hist.add_trace(go.Histogram(x=image_data_store.query("filename == @filename").radius, name=filename,nbinsx=20))
        fig_box.add_trace(go.Box(x=image_data_store.query("filename == @filename").radius, name=filename))

    fig_hist.update_layout(
        title="Spheroid sizes",
        xaxis_title="Radius (pixels)",
        yaxis_title="Count",
        barmode="overlay"
    )
    fig_box.update_layout(
        title="Spheroid sizes",
        xaxis_title="Radius (pixels)"
    )

    fig_hist.update_traces(opacity=0.75)
    fig_box.update_traces(opacity=0.75)
    return array_to_data_url(thresholded_image),array_to_data_url(unthresholded_image),fig_hist,fig_box

# @callback(
#     [Output("thresholded_annotated_image","src",allow_duplicate=True),Output("unthresholded_annotated_image", "src"),Output("histo", "figure"),Output("box", "figure"),Output("current_image_data", "data")],
#     [Input("submit_threshold", "n_clicks"),Input("intermediate-value", "data")],
#     [State("image", "src"),State("submit_threshold", "value")]
# )
# def push_circles(
#     n_clicks,
#     data,
#     image_data_url,
#     threshold
# ):
#     data = pd.read_json(data)
#     image = data_url_to_array(image_data_url)
#     print(image)
#     _, thresholded_image_data, threshold_df = proc_image(image,threshold=threshold)
#     _, unthresholded_image_data, _ = proc_image(image,threshold=1000000000)
    
#     fig_hist = go.Figure()
#     fig_box = go.Figure()

#     for filename in set(data.filename.values):
#         fig_hist.add_trace(go.Histogram(x=data.query("filename == @filename").radius, name=filename,nbinsx=20))
#         fig_box.add_trace(go.Box(x=data.query("filename == @filename").radius, name=filename))

#     fig_hist.update_layout(
#         title="Spheroid sizes",
#         xaxis_title="Radius (pixels)",
#         yaxis_title="Count",
#         barmode="overlay"
#     )
#     fig_box.update_layout(
#         title="Spheroid sizes",
#         xaxis_title="Radius (pixels)"
#     )

#     fig_hist.update_traces(opacity=0.75)
#     fig_box.update_traces(opacity=0.75)
#     return thresholded_image_data[-1],unthresholded_image_data[-1],fig_hist,fig_box,threshold_df.to_json()

# @callback([Output("thresholded_annotated_image","src",allow_duplicate=True),Output("unthresholded_annotated_image", "src"),Output("histo", "figure"),Output("box", "figure"),Output("current_image_data", "data")],
#           Input("upload-image", "contents"),
#           Input("intermediate-value", "data"),
#           State("upload-image", "filename"),
#           State("threshold_input", "value"),
#           prevent_initial_call=True)
# def update_output(list_of_contents, data, list_of_names, threshold):
#     data = pd.read_json(data)
#     _, thresholded_image_data, threshold_df = proc_image(list_of_contents,threshold=threshold)
#     _, unthresholded_image_data, _ = proc_image(list_of_contents,threshold=1000000000)
    
#     fig_hist = go.Figure()
#     fig_box = go.Figure()

#     for filename in set(data.filename.values):
#         fig_hist.add_trace(go.Histogram(x=data.query("filename == @filename").radius, name=filename,nbinsx=20))
#         fig_box.add_trace(go.Box(x=data.query("filename == @filename").radius, name=filename))

#     fig_hist.update_layout(
#         title="Spheroid sizes",
#         xaxis_title="Radius (pixels)",
#         yaxis_title="Count",
#         barmode="overlay"
#     )
#     fig_box.update_layout(
#         title="Spheroid sizes",
#         xaxis_title="Radius (pixels)"
#     )

#     fig_hist.update_traces(opacity=0.75)
#     fig_box.update_traces(opacity=0.75)
#     return thresholded_image_data[-1],unthresholded_image_data[-1],fig_hist,fig_box,threshold_df.to_json()

# @callback(Output("thresholded_annotated_image","src",allow_duplicate=True),
#           Input("current_image_data", "data"),
#           Input("threshold_input", "value"),
#           prevent_initial_call=True)
# def redraw(data,threshold):
#     try:
#         uploaded_df = pd.read_json(data)
#     except:
#         return ""
#     print(uploaded_df)
#     return ""

if __name__ == "__main__":
    app.run(debug=True)