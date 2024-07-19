from dash import Dash, dcc, html, Input, Output, State, callback, dash_table
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
        multiple=True,
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
        }),
    dcc.Tabs(
        id="main_tabs", 
        value="original_image", 
        children=[
            dcc.Tab(
                label="Original image", 
                value="original_image", 
                children=[
                    html.Div(
                        id="output-image-upload",
                        children=[
                            html.Img(
                                id="image",
                                src="", 
                                style={
                                    "height": "1000px"
                                })], 
                                style={
                                    "display": "flex", 
                                    "justify-content": "center", 
                                    "align-items": "center"
                                })
        ]),
        dcc.Tab(
            label="Thresholded image", 
            value="threshold_image", 
            children=[
                html.Div(
                    id="thresholded-output-image-upload",
                    children=[
                        html.Img(
                            id="thresholded_annotated_image",
                            src="", 
                            style={
                                "height": "1000px"
                            })], 
                            style={
                                "display": "flex", 
                                "justify-content": "center", 
                                "align-items": "center"
                            })
        ]),
        dcc.Tab(
            label="Unthresholded image", 
            value="unthreshold_image", 
            children=[
                html.Div(
                    id="unthresholded-output-image-upload",
                    children=[
                        html.Img(
                            id="unthresholded_annotated_image",
                            src="", 
                            style={
                                "height": "1000px"
                            })], 
                            style={
                                "display": "flex", 
                                "justify-content": "center", 
                                "align-items": "center"
                            })
        ]),
        dcc.Tab(
            label="Histogram", 
            value="graphs", 
            children=[
                dcc.Graph(
                    id="histo",
                    figure=go.Figure()
                ),
                dcc.Graph(
                    id="box", 
                    figure=go.Figure()
                )
            ]),
        dcc.Tab(
            label="Data", 
            value="tables", 
            children=[
                html.Button(
                    "...Download processed data...", 
                    id="download_proc", 
                    n_clicks=0,
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderRadius": "5px",
                        'text-align': 'center'
                    }),
                html.Div(id="slides_data_div")
            ]
        )
        ]),
    dcc.Download(
        id="download-dataframe-csv"
    ),
    dcc.Store(
        id="data_store",
        data=json.dumps({
            "filename":"",
            "threshold":26
        })
    ),
    dcc.Store(
        id="image_data_store",
        data=json.dumps({
            "filename":[],
            "colour_values":[]
        })
    ),
    dcc.Store(
        id="current_image_data",
        data=None
    )
])

@callback(
        Output("data_store","data", allow_duplicate=True),
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

@callback(
        [
            Output("image","src"), 
            Output("data_store","data", allow_duplicate=True),
            Output("image_data_store","data", allow_duplicate=True),
            Output("slides_data_div","children")
        ],[
            Input("upload-image", "contents")
        ],[
            State("upload-image", "filename"), 
            State("data_store","data"), 
            State("image_data_store","data")
        ],
        prevent_initial_call=True)
def push_image(
    contents,
    filenames,
    data_store,
    image_data_store
):
    data_store = json_to_dict(data_store)
    image_data_store = pd.DataFrame(json_to_dict(image_data_store))
    for content, filename in zip(contents, filenames):
        if filename not in image_data_store.filename:
            circles_df = proc_image(content,data_store["threshold"])
            circles_df["filename"] = filename
            image_data_store = pd.concat([image_data_store,circles_df]).reset_index(drop=True)
    data_store["filename"] = filename
    image_data_store["average_shade"] = [sum(x)/len(x) for x in image_data_store.colour_values]
    image_data_store["confidence_shade"] = [(255-x)/255 for x in image_data_store.average_shade]
    out_df = image_data_store.copy()
    out_df["coordinate"] = [str(f"{int(x[0])},{int(x[1])}") for x in out_df.coordinate]
    out_df = out_df.drop(columns=["colour_values"])
    table = dash_table.DataTable(
        out_df.to_dict("records"),
        [{"name": i, "id": i} for i in out_df.columns]
        )
    return content, json.dumps(data_store), image_data_store.to_json(), table

@callback([Output("thresholded_annotated_image","src"),Output("unthresholded_annotated_image","src"),Output("histo","figure"),Output("box","figure")],
          [Input("submit_threshold","n_clicks")],
          [State("image","src"), State("data_store","data"), State("image_data_store","data")])
def push_circles(
    n_clicks,
    contents,
    data_store,
    image_data_store
):
    if not n_clicks:
        return "", "", go.Figure(), go.Figure()
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

# @callback([Output("download-dataframe-csv", "data")],
#           [Input("download_proc","n_clicks")],
#           [State("image_data_store","data")])
# def download_processed_data(
#     n_clicks,
#     image_data_store
# ):
#     if not n_clicks:
#         return {}
#     image_data_store = pd.DataFrame(json_to_dict(image_data_store))
#     out_df = image_data_store.drop(columns=["colour_values"])
#     print(dcc.send_data_frame(out_df.to_csv, "processed_data.csv", index=False))
#     return dcc.send_data_frame(out_df.to_csv, "processed_data.csv", index=False)

if __name__ == "__main__":
    app.run(debug=True)