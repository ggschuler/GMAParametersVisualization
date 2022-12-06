from dash import Dash, html, dcc, Input, Output
from tableGenerator import generateTable, getBones, setup_columns
from dataLoader import giveDataEntries
from features_math import cross_correlate, skewness_of_velocity, velocity
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

PATH = 'C:\\Users\\guilh\\Documents\\bb3DPoseVisualizer\\joints3D'
COLORSCALES = ['sunset','blackbody', 'solar', 'ice', 'twilight']
DATA_OPTIONS = giveDataEntries()
BONES_LIST, BONE_COLORS, BONE_NAMES_LIST = getBones()
external_style = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
APP = Dash(__name__, external_stylesheets=external_style)
DEFAULT_DATA = generateTable(PATH, '01')
Z_OFFSET=.05
PAIRS_OF_JOINTS = [4, 5, 6, 7, #left leg pairs
                       0, 1, 2, 3, #righ leg pairs
                       13, 14, 15, 16, 17, #left arm pairs
                       8, 9, 10, 11, 12,   #right arm pairs
                       18, 19, 20, 21, 22, 23]   


styles = {
    'pre':{
        'border':'thin lighgrey solid',
        'overflow':'scroll'
    }
}

def frame_args(duration):
    return {
            "frame": {"duration": duration},
            "mode": "immediate",
            "fromcurrent": True,
            "transition": {"duration": duration, "easing": "linear"},
        }

def give_selected(index):
    return columns.index(index)

def getPosition(selected_data, init_frame, last_frame):
    # GET VALUES FOR X, Y AND Z AXIS FOR ALL FRAMES ON CHOOSEN DATA:
    selected_data = selected_data.iloc[init_frame*3:(last_frame+1)*3]
    x,y,z = [], [], []
    n_of_frames = int(len(selected_data)/3)
    for i in list(range(init_frame, last_frame+1)):
        x.extend(selected_data.xs((i, 'x'), level=[0,1]).values)
        y.extend(selected_data.xs((i, 'y'), level=[0,1]).values)
        z.extend(-selected_data.xs((i, 'z'), level=[0,1]).values)
    #SET RANGES:
    #TODO: normalize it
    xrange = [np.min(x), np.max(x)]
    yrange = [np.min(y)-Z_OFFSET, np.max(y)+Z_OFFSET]
    zrange = [np.min(z), np.max(z)+Z_OFFSET]
    return x, y, z, xrange, yrange, zrange, n_of_frames

#CREATE EMPTY FIGURE:
fig = go.Figure()
fig.update_layout(clickmode='event+select')
dummy0, dummy1, columns = setup_columns()


skewfig = go.Figure()
crosscorrgraph = go.Figure()

import plotly.io as pio
#CALLBACKS:

@APP.callback(
    Output("skewgraph", "figure"),
    Output("crosscorrgraph", "figure"),
    Input("velocities", "data"),
    Input("velocities_pair", "data"),
    Input("skewness", "data"),
    Input("crosscorr", "data"),
    )

def update_skewgraph(velocities, pairvelocities, skewness, crosscorr):
    skewfig = go.Figure()
    BINSIZE = 0.3

    skewfig = ff.create_distplot([velocities], ['kde(probability)'], show_hist=False, show_rug=False, histnorm='probability', bin_size=BINSIZE)
    skewfig.data[0]['hovertemplate'] = 'x:%{x}<br>y:%{y}<extra></extra>'
    skewfig.data[0]['visible'] = 'legendonly'

    skewfig.add_histogram(x=velocities,
                          marker=dict(color='#7209b7'),
                          xbins=dict(
                            start=np.min(velocities),
                            end=np.max(velocities),
                            size=BINSIZE
                          ), histnorm='probability', name='velocity_histogram')
    skewfig.data[1]['hovertemplate'] = 'bin: [%{x}]<br>value: %{y:.3f}<extra></extra>'

    skewfig.add_vline(x=np.median(velocities), line_color='#FC817E',annotation_text=f"md={np.median(velocities):.2f}", annotation_position="top", annotation_textangle=-30, annotation_xshift=-5, line_dash='dot')
    skewfig.add_vline(x=np.mean(velocities), line_color='#fcd94c', annotation_text=f"x={np.mean(velocities):.2f}", annotation_position="top", annotation_textangle=-30, annotation_xshift=5, line_dash='dot')
    skewfig.update_layout(plot_bgcolor='#edede9',
                      title=dict(text=f'2. <b>Velocity distribution</b> (skew(V) = {skewness:.4f}):'),
                      font=dict(color="#191A1A", family='Helvetica'),
                      titlefont=dict(color='#191A1A', size=18),
                      title_y=0.91,
                      title_x=0.1,
                      autosize=True, xaxis_title='linear velocity per frame (x1000)', yaxis_title='probability'
    )
    skewfig.update_yaxes(showline=True, linewidth=2, linecolor='black', rangemode='nonnegative', scaleratio=1)
    skewfig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=False)
    #----------------------------------------------------------------------------------------------------------------
    crosscorrgraph = make_subplots(rows=2, cols=1, shared_xaxes=True, x_title='frame')
    window_corr = pd.Series(velocities).rolling(window=6, center=True).corr(pd.Series(pairvelocities))

    crosscorrgraph.append_trace(go.Scatter(
                                x=[i for i in range(len(velocities))],
                                y=velocities,
                                mode='lines',
                                name='velocity for selected joint (j<sub>s</sub>)'
    ), row=1, col=1)
    crosscorrgraph.append_trace(go.Scatter(
                                x=[i for i in range(len(pairvelocities))],
                                y=pairvelocities,
                                mode='lines',
                                name='velocity for pair joint (j<sub>p</sub>)'
    ), row=1, col=1)
    crosscorrgraph.append_trace(go.Scatter(
                                x=[i for i in range(len(pairvelocities))],
                                y=window_corr,
                                mode='lines',
                                name='rolling_correlation'
    ), row=2, col=1)

    crosscorrgraph.update_traces(selector=dict(name='rolling_correlation'))['layout']['yaxis2']['range'] = [-1.5, 1.5]
    crosscorrgraph.update_yaxes(showline=True, linewidth=2, linecolor='black', scaleratio=1)
    crosscorrgraph.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=False)
    crosscorrgraph.update_layout(plot_bgcolor='#edede9',
                      title=dict(text=f'3. <b>Global and local Pearson correlation</b> (r(j<sub>s</sub>, j<sub>p</sub>) = {crosscorr:.4f})<br><b>for joint velocity</b>:'),
                      font=dict(color="#191A1A", family='Helvetica'),
                      titlefont=dict(color='#191A1A', size=18),
                      title_y=0.91,
                      title_x=0.1,
                      autosize=True, yaxis_title='velocity (x1000)'
    )
    crosscorrgraph['layout']['yaxis2']['title']='Pearson r (w=6)'
    return skewfig, crosscorrgraph


@APP.callback(
    Output("graph", "figure"),
    Output("velocities", "data"),
    Output("velocities_pair", "data"),
    Output("skewness", "data"),
    Output("crosscorr", "data"),
    Input("color_dropdown", "value"),
    Input("data_dropdown", "value"),
    Input("init_value", "value"),
    Input("last_value", "value"),
    Input('graph', 'clickData'),
    )

def update_graph(colorscale, data, init_value, last_value, clickData):
    #UPDATE WHOLE BODY MARKERS DATAPOINTS:
    new_data = generateTable(PATH, data)
    x, y, z, xrange, yrange, zrange, n_of_frames = getPosition(new_data, int(init_value), int(last_value-1))
    index = 18
    corrected_index = columns.index(new_data.iloc[:,index].name[1])
    fig = go.Figure(go.Scatter3d(x=x[0],
                                 y=y[0],
                                 z=z[0],
                                 mode='markers',
                                 marker=dict(size=12,
                                             opacity=0.8,
                                             colorscale=colorscale,
                                             color=BONE_COLORS
                                            ),
                                 name='full_body_markers',
                                 customdata=columns,
                                 hovertemplate='<b>%{customdata}</b><br><extra></extra>'
                                               #'x:%{x:.4f}<br>'+
                                               #'y:%{y:.4f}<br>'+
                                               #'z:%{z:.4f}<br><extra></extra>'
                                 
                                 )
                    )
    #UPDATE BONES LINES DATAPOINTS:
    for bone in range(len(BONES_LIST)):
        fig.add_scatter3d(x=x[0][BONES_LIST[bone]],
                          y=y[0][BONES_LIST[bone]],
                          z=z[0][BONES_LIST[bone]],
                          name=BONE_NAMES_LIST[bone],
                          mode='lines',
                          line=dict(color="black", width=6),
                          connectgaps=False,
                          hoverinfo='skip'
                         )


    
    fig.add_scatter3d(x=[fig['data'][0]['x'][index]],
                          y=[fig['data'][0]['y'][index]],
                          z=[fig['data'][0]['z'][index]],
                          marker=dict(size=12,
                                      color="green",
                                      opacity=1,
                                      ),
                          name='selected_joint',
                          mode='markers',
                          customdata=[columns[index]],
                          hovertemplate='<b>%{customdata}</b> (selected)<br><extra></extra>'
                                               #'x:%{x:.4f}<br>'+
                                               #'y:%{y:.4f}<br>'+
                                               #'z:%{z:.4f}<br><extra></extra>'
                         )

    
    

    if clickData is not None:
        index = give_selected((clickData['points'][0]['customdata']))
        corrected_index = columns.index(new_data.iloc[:,index].name[1])
        fig.update_traces(x=[fig['data'][0]['x'][index]],
                          y=[fig['data'][0]['y'][index]],
                          z=[fig['data'][0]['z'][index]],
                          marker=dict(size=12,
                                      color="green",
                                      opacity=1,
                                      ),
                          name='selected joint',
                          mode='markers',
                          hoverinfo='all',
                          customdata=[columns[index]],
                                 hovertemplate='<b>%{customdata}</b> (selected)<br><extra></extra>',
                                               #'x:%{x:.4f}<br>'+
                                               #'y:%{y:.4f}<br>'+
                                               #'z:%{z:.4f}<br><extra></extra>',
            selector=dict(name='selected_joint'))
    

    
    #FRAME STUFF:
    frames = []
    xs_of_selected_joint = ((new_data.iloc[:,corrected_index].loc[:,'x']).array)[init_value:last_value]
    ys_of_selected_joint = ((new_data.iloc[:,corrected_index].loc[:,'y']).array)[init_value:last_value]
    zs_of_selected_joint = ((new_data.iloc[:,corrected_index].loc[:,'z']).array)[init_value:last_value]

    xs_of_pairjoint = ((new_data.iloc[:,PAIRS_OF_JOINTS[corrected_index]].loc[:,'x']).array)[init_value:last_value]
    ys_of_pairjoint = ((new_data.iloc[:,PAIRS_OF_JOINTS[corrected_index]].loc[:,'y']).array)[init_value:last_value]
    zs_of_pairjoint = ((new_data.iloc[:,PAIRS_OF_JOINTS[corrected_index]].loc[:,'z']).array)[init_value:last_value]

    
    velocities_of_selected = velocity(xs_of_selected_joint, ys_of_selected_joint, zs_of_selected_joint)
    velocities_of_pairjoint = velocity(xs_of_pairjoint,     ys_of_pairjoint,      zs_of_pairjoint)
    skewness = skewness_of_velocity(velocities_of_selected)
    crosscorr = cross_correlate(velocities_of_selected, velocities_of_pairjoint)
    print(new_data.iloc[:6,:4].to_latex())

    for frame in range(n_of_frames):
        frames.append(go.Frame(data=[go.Scatter3d(x=x[frame],y=y[frame],z=z[frame]), 
                                     go.Scatter3d(x=x[frame][BONES_LIST[0]], y=y[frame][BONES_LIST[0]], z=z[frame][BONES_LIST[0]]),  
                                     go.Scatter3d(x=x[frame][BONES_LIST[1]], y=y[frame][BONES_LIST[1]], z=z[frame][BONES_LIST[1]]),
                                     go.Scatter3d(x=x[frame][BONES_LIST[2]], y=y[frame][BONES_LIST[2]], z=z[frame][BONES_LIST[2]]),
                                     go.Scatter3d(x=x[frame][BONES_LIST[3]], y=y[frame][BONES_LIST[3]], z=z[frame][BONES_LIST[3]]),
                                     go.Scatter3d(x=x[frame][BONES_LIST[4]], y=y[frame][BONES_LIST[4]], z=z[frame][BONES_LIST[4]]),
                                     go.Scatter3d(x=x[frame][BONES_LIST[5]], y=y[frame][BONES_LIST[5]], z=z[frame][BONES_LIST[5]]),
                                     go.Scatter3d(x=[x[frame][index]], y=[y[frame][index]], z=[z[frame][index]])
                                     ],
                                traces=[0,1,2,3,4,5,6,7],
                                name=f"fr{frame}")
                                )
    
    fig.update(frames=frames)
    #UPDATE THE LAYOUT WITH TITLES, SIZES, MENU STUFF AND SLIDERS
    #STEPS ARE THE LITTLE MARKS ON THE SLIDER
    steps = [{"args":[[f.name], frame_args(0)],
              "label": f"{k+init_value}",
              "method":"animate",
              "visible":True,
             } for k, f, in enumerate(fig.frames)
            ]
    #SLIDERS ARE SLIDERS
    sliders = [{"pad": {"b": 0, "t": 10},
                "currentvalue":{"prefix":"frame Nº: "},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": steps
               }
              ]
    fig.update_layout(
                      title=f'1. <b>Joint data</b> (frames {init_value}-{last_value}) <b>for infant nº {data}</b>:',
                      autosize=True,
                      width=900,
                      height=900,
                      font=dict(color="#191A1A", family='Helvetica'),
                      titlefont=dict(color='#191A1A', size=18),
                      title_y=0.91,
                      title_x=0.1,
                      scene=dict(
                                 xaxis=dict(range=xrange, autorange=False, backgroundcolor='#edede9'),
                                 yaxis=dict(range=yrange, autorange=False, backgroundcolor='#edede9'),
                                 zaxis=dict(range=zrange, autorange=False, backgroundcolor='#edede9'),
                                 aspectratio=dict(x=1, y=1, z=1),
                                ),
                      updatemenus = [
                         {
                             "buttons": [
                                 {
                                     "args": [None, frame_args(0)],
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
                             "pad": {"r": 10, "t": 20},
                             "type": "buttons",
                             "x": 0.1,
                             "y": 0,
                         }
                        ],
                       sliders=sliders,
                       uirevision=True
    )


    return fig, velocities_of_selected, velocities_of_pairjoint, skewness, crosscorr

APP.layout = html.Div([
    #title and subtitle
    html.Div([
        html.H1(
            'bb3dDynamicParameters', style={'font-family':'Helvetica', 'margin-top':'0', 'margin-bottom':'0'}, className='eight columns'
        ),
        html.P(
            'a tool for visualizing infant pose data and GMA-related parameters.', style={'font-family':'Helvetica', 'font-size':'120%', 'width':'80%', 'margin-left':'0', 'color':"#191A1A"}, className='eight columns'
        ),
        html.Hr(style={'borderWidth':'6', 'width':'100%','borderColor':'#00000', 'opacity':'unset'})
    ], className='row'),
    #parameters
    html.Div([
        html.Div(
            [
                dcc.Markdown('**Initial and final frame**'),
                html.Div(
                    [
                        dcc.Input(
                        id='init_value',
                        value=0,
                        type='number'),
                    ]),
                html.Div(
                    [
                        dcc.Input(
                        id='last_value',
                        value=200,
                        type='number'),
                    ])
            ], className='two columns', style={'margin-top':'-1%'}),   
        html.Div(
            [
                dcc.Markdown('**Choose data**'),
                dcc.Dropdown(
                    id='data_dropdown',
                    options=DATA_OPTIONS,
                    value='01')
            ], className='two columns', style={'margin-top':'-1%', 'margin-left':'-2%'}),
        html.Div(
            [
                dcc.Markdown('**Choose colorscale**'),
                dcc.Dropdown(
                    id='color_dropdown', 
                    options=COLORSCALES,
                    value='sunset')
            ], className='two columns', style={"margin-top":"-1%", 'margin-left':'0%'}),
    ], className='row'),
    #graphs
    html.Div(
        [
            html.Div([
                dcc.Graph(
                    figure=fig, id='graph', style={'margin-top':'0%'}),
            ], className='six columns'),
            html.Div([
                    dcc.Graph(
                        figure=skewfig, id='skewgraph', style={'margin-top':'4.5%'}),
                    dcc.Graph(
                        figure=crosscorrgraph, id="crosscorrgraph"),
            ], className='six columns')
        ], className='twelve columns'
    ),
    dcc.Store(id="velocities"),
    dcc.Store(id="skewness"),
    dcc.Store(id="velocities_pair"),
    dcc.Store(id='crosscorr')
    ])

if __name__ == '__main__':
    APP.run_server(debug=True)