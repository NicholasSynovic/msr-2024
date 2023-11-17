import plotly.graph_objects as go

# Define nodes
nodes = ['Source1', 'Source2', 'Source3', 'Sink1', 'Sink2']

# Set up the Sankey diagram with custom vertical positions
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color='black', width=0.5),
        label=nodes,
    ),
    link=dict(
        source=[0, 0, 0, 1, 1, 2, 2, 0, 1, 0],
        target=[3, 4, 3, 3, 4, 3, 4, 3, 4, 3],
        value=[1, 2, 1, 1, 1, 1, 1, 1, 1, 1],  # Adjust the values based on your data
    )
)])

# Customize layout
fig.update_layout(title_text="Customized Sankey Diagram", font_size=12)

# Show the figure
fig.show()
