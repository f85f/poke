import pandas as pd
import argparse
import os.path
import numpy as np
import folium

parser = argparse.ArgumentParser(description='Visualize Shodan search results on a map')
parser.add_argument('output_dir', type=str, help='Path to the directory containing Shodan search results')
args = parser.parse_args()

# Read nodes.csv and peers.csv files
nodes_df = pd.read_csv(f"{args.output_dir}/nodes.csv")
peers_df = pd.read_csv(f"{args.output_dir}/peers.csv", usecols=['ip', 'latitude', 'longitude', 'country', 'isp'])

# Create a map centered on the mean latitude and longitude of nodes
map_center = [nodes_df['latitude'].mean(), nodes_df['longitude'].mean()]

# Create a feature group for nodes data
nodes_fg = folium.FeatureGroup(name='Nodes')

# Add nodes to the feature group
for _, row in nodes_df.iterrows():
    if not np.isnan(row['latitude']) and not np.isnan(row['longitude']):
        folium.CircleMarker(location=[row['latitude'], row['longitude']], radius=5,
                            popup=f"{row['ip']}<br/>{row['country']}<br/>{row['isp']}",
                            fill=True, fill_opacity=0.7, color='red').add_to(nodes_fg)

# Create a feature group for peers data
peers_fg = folium.FeatureGroup(name='Peers')

# Check if peers-geo.json file exists and is non-empty
if os.path.isfile(f"{args.output_dir}/peers.csv") and os.path.getsize(f"{args.output_dir}/peers.csv") > 0:
    # Add peers.csv data to the feature group
    for _, row in peers_df.iterrows():
        if not pd.isna(row['latitude']) and not pd.isna(row['longitude']):
            folium.CircleMarker(location=[row['latitude'], row['longitude']], radius=5,
                                popup=f"{row['ip']}<br/>{row['country']}<br/>{row['isp']}",
                                fill=True, fill_opacity=0.7, color='blue').add_to(peers_fg)

# Create a map for nodes and save as an HTML file
nodes_map = folium.Map(location=map_center, zoom_start=3)
nodes_fg.add_to(nodes_map)
folium.LayerControl().add_to(nodes_map)
nodes_map.save(f"{args.output_dir}/nodes.html")

# Create a map for peers and save as an HTML file, only if peers-geo.json exists and is non-empty
if os.path.isfile(f"{args.output_dir}/peers.csv") and os.path.getsize(f"{args.output_dir}/peers.csv") > 0:
    peers_map = folium.Map(location=map_center, zoom_start=3)
    peers_fg.add_to(peers_map)
    folium.LayerControl().add_to(peers_map)
    peers_map.save(f"{args.output_dir}/peers.html")
