from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
from tableGenerator import generateTable
from IPython.display import display
import numpy as np
import plotly.graph_objects as go

path = 'C:\\Users\\guilh\\Documents\\bb3DPoseVisualizer\\joints3D'
app = Dash(__name__)
df = generateTable(path, '01')

#@app.callback(
#    Output(component_id='my-output', component_property='children'),
#    Input(component_id='my-input', component_property='value')
#)
#def update_output_div(input_value):
#    return f'Output: {input_value}'




tdf = df.loc[:100]
n_of_frames = int(len(tdf)/3)
z_offset=.05
#df = px.data.iris()

x,y,z = [], [], []
for i in range(n_of_frames):
    x.extend(tdf.xs((i, 'x'), level=[0,1]).values)
    y.extend(tdf.xs((i, 'y'), level=[0,1]).values)
    z.extend(tdf.xs((i, 'z'), level=[0,1]).values)

display(tdf)
xrange = [np.min(x), np.max(x)]
yrange = [np.min(y)-z_offset, np.max(y)+z_offset]
zrange = [np.min(z), np.max(z)+z_offset]
print(xrange)
print(yrange)
print(zrange)
# Read data from a csv
fig = go.Figure()
fig.add_trace(go.Scatter3d(x=x[0],
                           y=y[0],
                           z=z[0],
                           mode='markers',
))
frames = [go.Frame(data=[go.Scatter3d(x=x[k], 
                                      y=y[k],
                                      z=z[k])],
                   traces= [0],
                   name=f'frame{k}'      
                  ) for k  in  range(n_of_frames-1)]
fig.update(frames=frames)

def frame_args(duration):
    return {
            "frame": {"duration": duration},
            "mode": "immediate",
            "fromcurrent": True,
            "transition": {"duration": duration, "easing": "linear"},
        }

# Create and add slider
steps = []
for i in range(len(fig.data)):
    step = dict(
        method="update",
        args=[{"visible": [False] * len(fig.data)},
              {"title": "Slider switched to step: " + str(i)}],  # layout attribute
    )
    step["args"][0]["visible"][i] = False  # Toggle i'th trace to "visible"
    steps.append(step)


sliders = [dict(
    active=10,
    currentvalue={"prefix": "Frequency: "},
    pad={"t": 50},
    steps=steps
)]

sliders = [
            {
                "pad": {"b": 10, "t": 60},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [[f.name], frame_args(50)],
                        "label": str(k),
                        "method": "animate",
                    }
                    for k, f in enumerate(fig.frames)
                ],
            }
        ]


fig.update_layout(
         title='bbPoseVisualizer',
         width=600,
         height=600,
         scene=dict(
                    xaxis=dict(range=xrange, autorange=False),
                    yaxis=dict(range=yrange, autorange=False),
                    zaxis=dict(range=zrange, autorange=False),
                    aspectratio=dict(x=1, y=1, z=1),
                    ),
         updatemenus = [
            {
                "buttons": [
                    {
                        "args": [None, frame_args(1)],
                        "label": "&#9654;", # play symbol
                        "method": "animate",
                    },
                    {
                        "args": [[None], frame_args(0)],
                        "label": "&#9724;", # pause symbol
                        "method": "animate",
                    },
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 70},
                "type": "buttons",
                "x": 0.1,
                "y": 0,
            }
         ],
         sliders=sliders
         
)

#fig.show()



#for contestant, group in df.groupby("Contestant"):
#    fig.add_trace(go.Bar(x=group["Fruit"], y=group["Number Eaten"], name=contestant,
#      hovertemplate="Contestant=%s<br>Fruit=%%{x}<br>Number Eaten=%%{y}<extra></extra>"% contestant))
#fig.update_layout(legend_title_text = "Contestant")
#fig.update_xaxes(title_text="Fruit")
#fig.update_yaxes(title_text="Number Eaten")
#fig.show()
#fig.update_layout(title='Mt Bruno Elevation', autosize=False,
#                  width=500, height=500,
#                  margin=dict(l=65, r=50, b=65, t=90))
#
#fig.show()


app.layout = html.Div([
    dcc.Graph(figure=fig)
])
if __name__ == '__main__':
    app.run_server(debug=True)