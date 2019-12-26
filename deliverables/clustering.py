from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import pandas as pd, numpy as np, csv
import json
import requests
import urllib
import re
import math
import matplotlib.pyplot as plt
from __future__ import print_function
from __future__ import division
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

df = pd.read_json('losangeles.json')
json_struct = json.loads(df.to_json(orient="records"))    
df_flat = pd.io.json.json_normalize(json_struct)
df_flat = df_flat[df_flat['location.address1'].str.strip().astype(bool)]

with open('LA_county_zip.txt') as f:
    lines = f.read().splitlines()
df_flat = df_flat[df_flat['location.postal_code'].isin(lines)]
#df_flat = df_flat[df_flat['location.postal_code'] == "90012"]
df_flat = df_flat[df_flat['location.country'] == 'US']
df_flat = df_flat.drop_duplicates(subset=['id'])
df_flat.sort_values(by=['location.postal_code'], inplace=True)
df_flat.reset_index(drop=True)
df_flat.count()


coords = df_flat.as_matrix(columns=['coordinates.latitude', 'coordinates.longitude'])
coords.shape
neigh = NearestNeighbors(n_neighbors=2)
nbrs = neigh.fit(coords)
distances, indices = nbrs.kneighbors(coords)

distances = np.sort(distances, axis=0)
distances = distances[:,1]
plt.plot(distances)
min = 6;
db = DBSCAN(eps=.0028, min_samples=min, algorithm='ball_tree', metric='haversine').fit(coords)
cluster_labels = db.labels_
num_clusters = len(set(cluster_labels))
num_clusters
df = df_flat.assign(cluster_id = cluster_labels.flatten())
df['score'] = df['review_count'].apply(lambda x: math.log10(x))
df['score'] = df['rating']+(df['score'])
#df.reset_index()
#df.sort_values(by=['id'])
#df.sort_values(by=['cluster_id', 'score'], inplace=True)
#df.reset_index(inplace=True)
#df.drop_duplicates(subset=['id'])

import matplotlib.pyplot as plt
colors = ['royalblue', 'maroon', 'forestgreen', 'mediumorchid', 'tan', 'deeppink', 'olive', 'goldenrod', 'lightcyan', 'navy']
vectorizer = np.vectorize(lambda x: colors[x % len(colors)])
plt.scatter(x=df['coordinates.latitude'], y=df['coordinates.longitude'], c=vectorizer(df['cluster_id']))
plt.show()

df = df[df['cluster_id'] != -1]
df.sort_values(by=['cluster_id'], inplace=True)
pd.DataFrame.hist(data=df, column='cluster_id', bins = 100)
df = df.reset_index(drop=True)
df.count()