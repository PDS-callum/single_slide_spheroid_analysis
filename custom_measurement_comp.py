from dash import Dash, html, Output, Input, State, dcc

class MeasurementMarker(html.Div):
  def __init__(self, x, y, label=""):
    super().__init__()
    self.style = {
        "position": "absolute",
        "left": f"{x}px",
        "top": f"{y}px",
        "background-color": "lightblue",
        "border-radius": "50%",
        "width": "15px",
        "height": "15px",
        "text-align": "center",
        "line-height": "15px",
        "color": "black"
    }
    self.children = label

class MeasurementTool(html.Div):
  def __init__(self, id, image_src):
    super().__init__()
    self.id = id
    self.image_src = image_src
    self.starting_x = None
    self.starting_y = None
    self.distance_div = html.Div(id=f"{id}-distance", children="", style={"position": "absolute", "top": "10px", "left": "10px"})
    self.marker1 = None
    self.marker2 = None
    self.style = {"position": "relative", "background-image": f"url('{image_src}')", "background-size": "contain", "background-repeat": "no-repeat", "width": "500px", "height": "300px"}  # Adjust width and height as needed
    self.events = [
        ("mousedown", self.on_mousedown),
        ("mouseup", self.on_mouseup),
        ("mousemove", self.on_mousemove),
    ]
    for event_name, event_handler in self.events:
      self.n_clicks_out(event_name)(event_handler)

  def on_mousedown(self, event):
    self.starting_x = event.x - self.offsetLeft
    self.starting_y = event.y - self.offsetTop

  def on_mouseup(self, event):
    if self.starting_x and self.starting_y:
      self.marker2 = MeasurementMarker(event.x - self.offsetLeft, event.y - self.offsetTop, "M2")
      self.calculate_distance()

  def on_mousemove(self, event):
    if self.starting_x and self.starting_y:
      self.marker1 = MeasurementMarker(event.x - self.offsetLeft, event.y - self.offsetTop, "M1")

  def calculate_distance(self):
    if self.marker1 and self.marker2:
      x1, y1 = self.marker1.style["left"].replace("px", ""), self.marker1.style["top"].replace("px", "")
      x2, y2 = self.marker2.style["left"].replace("px", ""), self.marker2.style["top"].replace("px", "")
      distance = ((float(x2) - float(x1))**2 + (float(y2) - float(y1))**2)**0.5
      self.distance_div.children = f"Distance: {distance:.2f} px"

  def n_clicks_out(self, event_name):
    def decorator(event_handler):
      @CallBack(
          Output(component_id=self.id, component_property="children"),
          [Input(component_id=self.id, component_property=event_name)],
      )
      def set_n_clicks(n_clicks):
        event_handler(n_clicks)
        return self
      return decorator
    return decorator

app = Dash(__name__)

# ... rest of your app layout and callbacks

# Example usage in your layout
image_src = "path/to/your/image.jpg"
measurement_tool = MeasurementTool(id="measurement-tool", image_src=image_src)
app.layout = html.Div(
