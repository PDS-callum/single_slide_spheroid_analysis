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
import base64
import io
import math

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
    html.P("No scale set. Click start and stop of scale bar.", id="scale_text"),
    dcc.Tabs(
        id="main_tabs", 
        value="original_image", 
        children=[
            dcc.Tab(
                label="Original image", 
                value="original_image", 
                children=[
                    dcc.Graph(
                        id="output-image-upload",
                        figure=go.Figure()
                    ),
                    html.Div(id='output-container')
        ]),
            dcc.Tab(
                label="Annotations", 
                value="annotations", 
                children=[
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
                        id="annotations_tabs", 
                        value="threshold_image", 
                        children=[
                            dcc.Tab(
                                label="Thresholded image", 
                                value="threshold_image", 
                                children=[
                                    html.Div(
                                        id="threshold_img_div",
                                        style={
                                            "display": "flex", 
                                            "justify-content": "center", 
                                            "align-items": "center"
                                        },
                                        children=[
                                            html.Img(
                                                id="threshold_img",
                                                src="", 
                                                style={
                                                    "height": "1000px"
                                                }
                                            )
                                        ]
                                    )
                                ]
                            ),
                            dcc.Tab(
                                label="Unhresholded image", 
                                value="unthreshold_image", 
                                children=[
                                    html.Div(
                                        id="unthreshold_img_div",
                                        style={
                                            "display": "flex", 
                                            "justify-content": "center", 
                                            "align-items": "center"
                                        },
                                        children=[
                                            html.Img(
                                                id="unthreshold_img",
                                                src="", 
                                                style={
                                                    "height": "1000px"
                                                }
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
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
    return json.dumps(data_store)

@callback(
    [
        Output("scale_text","children"),
        Output("data_store","data", allow_duplicate=True),
        Output("image_data_store","data")
    ],
    Input("output-image-upload","clickData"),
    [
        State("data_store","data"),
        State("image_data_store","data")
    ],prevent_initial_call = True
)
def get_coord(click_data,data_store,image_data_store):
    data_store = json_to_dict(data_store)
    image_data_store = pd.DataFrame(json_to_dict(image_data_store))
    def scale_radius(x):
        return round((x/data_store["scale"])*500,2)
    try:
        data_store["clicks"]+=1
    except:
        data_store["clicks"]=1
    if data_store["clicks"]%2 == 0:
        delta_x = abs(data_store["prev_click"]["points"][0]["x"] - click_data["points"][0]["x"])
        delta_y = abs(data_store["prev_click"]["points"][0]["y"] - click_data["points"][0]["y"])
        data_store["scale"] = delta_x
        image_data_store["microm_radius"] = image_data_store["radius"].apply(scale_radius)
        return "Scale set!",json.dumps(data_store),image_data_store.to_json()
    else:
        data_store["prev_click"] = click_data
        return "No scale set. Click start and stop of scale bar.",json.dumps(data_store),image_data_store.to_json()

@callback(
    [
        Output("output-image-upload","figure"), 
        Output("data_store","data", allow_duplicate=True),
        Output("image_data_store","data", allow_duplicate=True),
        Output("slides_data_div","children"),
        Output("threshold_img","src",allow_duplicate=True),
        Output("unthreshold_img","src",allow_duplicate=True)
    ],[
        Input("upload-image", "contents")
    ],[
        State("upload-image", "filename"), 
        State("data_store","data"), 
        State("image_data_store","data")
    ],
    prevent_initial_call=True
)
def push_image(
    contents,
    filenames,
    data_store,
    image_data_store
):
    if contents is not None:
        data_store = json_to_dict(data_store)
        image_data_store = pd.DataFrame(json_to_dict(image_data_store))
        for content, filename in zip(contents, filenames):
            if filename not in image_data_store.filename:
                circles_df = proc_image(content,data_store["threshold"])
                circles_df["filename"] = filename
                print(circles_df)
                image_data_store = pd.concat([image_data_store,circles_df]).reset_index(drop=True)
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        try:
            data_store.update({
                "filename":filename,
                "loaded_image":content})
            image_data_store["average_shade"] = [sum(x)/len(x) for x in image_data_store.colour_values]
            image_data_store["confidence_shade"] = [(255-x)/255 for x in image_data_store.average_shade]
            out_df = image_data_store.copy()
            out_df["coordinate"] = [str(f"{int(x[0])},{int(x[1])}") for x in out_df.coordinate]
            out_df = out_df.drop(columns=["colour_values"])
            table = dash_table.DataTable(
                out_df.to_dict("records"),
                [{"name": i, "id": i} for i in out_df.columns]
                )
            with io.BytesIO(decoded) as image_buffer:
                img = Image.open(image_buffer)
                fig = px.imshow(img)
                fig.update_layout(
                    height=1080
                )
                return fig, json.dumps(data_store), image_data_store.to_json(), table, content, content
        except Exception as e:
            return go.Figure(), json.dumps(data_store), image_data_store.to_json(), dash_table.DataTable(), "", ""
    else:
        return go.Figure(), json.dumps({}), pd.DataFrame().to_json(), dash_table.DataTable(), "", ""

@callback(
    [
        Output("threshold_img","src",allow_duplicate=True),
        Output("unthreshold_img","src",allow_duplicate=True),
        Output("histo","figure"),Output("box","figure")
    ],[
        Input("submit_threshold","n_clicks")
    ],[
        State("threshold_img","src"), 
        State("data_store","data"), 
        State("image_data_store","data")
    ],
    prevent_initial_call=True
)
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
    print(thresholded_image)
    unthresholded_image = draw_circles(contents,current_df,99999999999999)
    
    fig_hist = go.Figure()
    fig_box = go.Figure()

    for filename in set(image_data_store.filename.values):
        fig_hist.add_trace(go.Histogram(x=image_data_store.query("filename == @filename").microm_radius, name=filename,nbinsx=20))
        fig_box.add_trace(go.Box(x=image_data_store.query("filename == @filename").microm_radius, name=filename))

    fig_hist.update_layout(
        title="Spheroid sizes",
        xaxis_title="Radius (um)",
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

@callback(
        [
            Output("download-dataframe-csv", "data")
        ],
        [
            Input("download_proc","n_clicks")
        ],
        [
            State("image_data_store","data")
        ],
        prevent_initial_call=True
    )
def download_processed_data(
    n_clicks,
    image_data_store
):
    print(3)
    image_data_store = pd.DataFrame(json_to_dict(image_data_store))
    out_df = image_data_store.drop(columns=["colour_values"])
    return [dcc.send_data_frame(out_df.to_csv, "processed_data.csv", index=False)]

if __name__ == "__main__":
    app.run(debug=True)