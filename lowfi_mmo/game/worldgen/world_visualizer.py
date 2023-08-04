from game import models
import plotly.graph_objects as go
import networkx as nx

def world_to_html(world):
    # Create a Graph object
    G = nx.Graph()

    # Add nodes for each location
    locations = models.Location.objects.filter(world=world)
    for location in locations:
        G.add_node(location.id)

    # Add edges for each path
    paths = models.Path.objects.filter(start__world=world)
    for path in paths:
        G.add_edge(path.start.id, path.end.id)

    # Compute the layout
    pos = nx.spring_layout(G, seed=12)  # this will use the Fruchterman-Reingold algorithm with a fixed seed

    # Extract x and y coordinates along with labels
    x_values = [pos[n][0] for n in G.nodes()]
    y_values = [pos[n][1] for n in G.nodes()]
    labels = [locations.get(id=n).name for n in G.nodes()]

    # Create a scatter plot for locations
    scatter = go.Scatter(x=x_values, y=y_values, mode='markers', text=labels, showlegend=False)

    # Create a line plot for paths
    lines = [go.Scatter(x=[pos[u][0], pos[v][0]], y=[pos[u][1], pos[v][1]], mode='lines',
                        line=dict(color='gray'), showlegend=False) for u, v in G.edges()]

    # Combine scatter and lines into one figure
    fig = go.Figure(data=[scatter] + lines)

    # Add annotations for each label
    for i, label in enumerate(labels):
        fig.add_annotation(x=x_values[i], y=y_values[i], text=label)

    return fig.to_html(full_html=False, include_plotlyjs='cdn')