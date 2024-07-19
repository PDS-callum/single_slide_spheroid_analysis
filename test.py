import dash
from dash import dcc, html, Input, Output, State
import cv2  # OpenCV for image processing (needs to be installed)

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Upload(
        id='upload-image',
        children=html.Div('Drag and drop or click to select an image')
    ),
    html.Div(id='output-container'),
    html.Div(id='image-container', style={'width': '50%', 'display': 'inline-block'}),
])

@app.callback(
    [Output('image-container', 'children'), Output('original-image', 'data')],
    [Input('upload-image', 'contents')],
    [State('upload-image', 'filename')]
)
def update_image(content, filename):
    if content is not None:
        img_data = content.split(',')[1]
        decoded_data = base64.b64decode(img_data)
        image = cv2.imdecode(np.fromstring(decoded_data, np.uint8), cv2.IMREAD_COLOR)
        return dcc.Img(src=img_data), image
    else:
        return None, None

@app.callback(
    Output('output-container', 'children'),
    [Input('image-container', 'n_clicks')],
    [State('original-image', 'data'), State('output-container', 'children')]
)
def measure_distance(n_clicks, image, output):
    if image is None:
        return

    if n_clicks == 0:
        return output

    # Code for click and drag functionality
    if n_clicks == 1:
        # Store starting point on first click
        x_start, y_start = dash.callback_context.triggered[0]['prop_id'].split('.')[0].split('-')[-2:]
        return f"Click at ({x_start}, {y_start})"
    elif n_clicks == 2:
        # Calculate distance on second click
        x_end, y_end = dash.callback_context.triggered[0]['prop_id'].split('.')[0].split('-')[-2:]
        x_start, y_start = output.split()[1][1:-1].split(',')  # Extract starting point from previous output
        start_point = (int(x_start), int(y_start))
        end_point = (int(x_end), int(y_end))

        # Calculate distance using a chosen metric (e.g., Euclidean distance)
        distance = np.linalg.norm(np.array(start_point) - np.array(end_point))

        # Optional: Draw line on the image (requires further implementation)
        # image_copy = image.copy()
        # cv2.line(image_copy, start_point, end_point, (0, 255, 0), 2)

        return f"Distance: {distance:.2f}"

    return output  # Maintain previous output for multi-click scenarios

if __name__ == "__main__":
    app.run(debug=True)