from game import models
import plotly.graph_objects as go

def world_to_html(world):
    # Fetch all instances of the Location model
    locations = models.Location.objects.filter(world=world)
    
    # Extract x, y, and name values from each location
    # TODO: update this to new system
    x_values = [location.x for location in locations]
    y_values = [location.y for location in locations]
    names = [location.name for location in locations]
    types = [location.category for location in locations]
    
    # Map location types to colors
    color_mapping = {'store': 'red', 'house': 'green'}
    colors = [color_mapping.get(location_type, 'blue') for location_type in types]

    # Fetch all instances of the Path model
    paths = models.Path.objects.filter(start__area_id=area_id, end__area_id=area_id)
    
    # Extract start and end locations for each path
    start_locations = [path.start for path in paths]
    end_locations = [path.end for path in paths]
    
    # Convert start and end locations to indices
    start_indices = [names.index(start.name) for start in start_locations]
    end_indices = [names.index(end.name) for end in end_locations]
    
    # Create a scatter plot of the locations using Plotly
    fig = go.Figure(data=go.Scatter(x=x_values, y=y_values, mode='markers', marker=dict(color=colors)))
    
    # Add labels for each point
    for i, name in enumerate(names):
        fig.add_annotation(
            x=x_values[i],
            y=y_values[i],
            text=name,
            showarrow=False,
            # font=dict(size=8),
            xanchor='center',
            yanchor='top',
            # yshift=-10
        )
    
    # Add lines between start and end locations
    for start_idx, end_idx in zip(start_indices, end_indices):
        fig.add_trace(go.Scatter(
            x=[x_values[start_idx], x_values[end_idx]],
            y=[y_values[start_idx], y_values[end_idx]],
            mode='lines',
            line=dict(color='rgba(128, 128, 128, 0.5)', width=1),
            showlegend=False
        ))

    # Set axes labels and title
    fig.update_layout(
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        title= area.name
    )
    
    # Convert the figure to HTML
    plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')