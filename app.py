from dash import Dash, dcc, html, Input, Output, State, callback, no_update, callback_context

from InteractiveModel import InteractiveModel
from Model import Model

#scene_builder = SceneBuilder(texture_path='Lego Figure Images\lego-cowboy-figure.png')
interactive_model = InteractiveModel(Model())

in_preview_mode: bool = False
preview_mode_text = lambda in_preview_mode: 'Preview Mode: On' if in_preview_mode else 'Preview Mode: Off'

app = Dash(__name__)

app.layout = html.Div([

    html.H1("3D Lego Model Viewer - Interactive"),

    html.H3(preview_mode_text(in_preview_mode), id='preview-mode-text'),

    html.Button('Toggle Preview Mode', id='preview-toggle'),

    dcc.Graph(
        id='3d-model-viewer',
        figure=interactive_model.figure,
        style={'height': '80vh'}
    ),

    html.Div([
        html.P("Click on the model to place a marker and see coordinates."),
        html.Div(id='click-data'),
        html.Button('Clear Markers', id='clear-button', n_clicks=0)
    ], style={'margin-top': '20px'})

])

@callback(
    Output('3d-model-viewer', 'figure'),
    Output('click-data', 'children'),
    Output('preview-mode-text', 'children'),
    Input('3d-model-viewer', 'clickData'),
    Input('clear-button', 'n_clicks'),
    Input('preview-toggle', 'n_clicks'),
    State('3d-model-viewer', 'relayoutData'),  # Add this to get current camera state
    prevent_initial_call=True
)
def handle_click(clickData, clear_clicks, preview_clicks, relayout_data):
    global in_preview_mode

    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Get current camera state if available
    camera_state = None
    if relayout_data and 'scene.camera' in relayout_data:
        camera_state = relayout_data['scene.camera']
        
    if triggered_id == 'clear-button':
        interactive_model.clear_points()
        figure = interactive_model.get_figure_with_camera(camera_state)
        return figure, 'Markers cleared', preview_mode_text(in_preview_mode)
    
    if triggered_id == 'preview-toggle':
        in_preview_mode = not in_preview_mode
        return no_update, no_update, preview_mode_text(in_preview_mode)

    if clickData:
        point = clickData['points'][0]
        x, y, z = round(point['x'], 6), round(point['y'], 6), round(point['z'], 6)

        if not in_preview_mode:
            interactive_model.add_point(x, y, z)
        else: # in preview mode 
            interactive_model.interact_with_point(x, y, z)
    
        figure = interactive_model.get_figure_with_camera(camera_state)
        return figure, f"Clicked at: X={x:.2f}, Y={y:.2f}, Z={z:.2f}", preview_mode_text(in_preview_mode)
    
    return no_update, "", no_update

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)