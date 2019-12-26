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
# or_df = df[df['cluster_id'] == 190]
# or_coords = or_df.as_matrix(columns=['coordinates.latitude', 'coordinates.longitude'])
# or_score = or_df.as_matrix(columns=['score'])

# or_coords = np.insert(or_coords, 0, or_coords[0], axis=0)
# or_score = np.insert(or_score, 0, 0, axis=0)

# or_coords.shape

g = df[df['id'] == 0]
for i in range(1, df['cluster_id'].iloc[-1] + 1):
    #print(i)
    or_df = df[df['cluster_id'] == i]
    print(len(or_df.index))
    if len(or_df.index) > 25:
        continue
    or_coords = or_df.as_matrix(columns=['coordinates.latitude', 'coordinates.longitude'])
    or_score = or_df.as_matrix(columns=['score'])
    or_coords = np.insert(or_coords, 0, or_coords[0], axis=0)
    or_score = np.insert(or_score, 0, 0, axis=0)
    
    print(or_df.shape)

    def create_data():
      """Creates the data."""
      data = {}
      data['API_key'] = 'AIzaSyDLMl_uIgWubmKtrUlfB9qqCx3TwsOLFL8'
      data['coording'] = or_coords
      return data

    def create_distance_matrix(data):
      addresses = data["coording"]
      API_key = data["API_key"]
      # Distance Matrix API only accepts 100 elements per request, so get rows in multiple requests.
      max_elements = 100
      num_addresses = len(addresses) # 16 in this example.
      # Maximum number of rows that can be computed per request (6 in this example).
      max_rows = max_elements // num_addresses
      # num_addresses = q * max_rows + r (q = 2 and r = 4 in this example).
      q, r = divmod(num_addresses, max_rows)
      dest_addresses = addresses
      distance_matrix = []
      # Send q requests, returning max_rows rows per request.
      for i in range(q):
        origin_addresses = addresses[i * max_rows: (i + 1) * max_rows]
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)

      # Get the remaining remaining r rows, if necessary.
      if r > 0:
        origin_addresses = addresses[q * max_rows: q * max_rows + r]
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)
      return distance_matrix

    def send_request(origin_addresses, dest_addresses, API_key):
      """ Build and send request for the given origin and destination addresses."""
      def build_address_str(addresses):
        # Build a pipe-separated string of addresses
        address_str = ''
        for i in range(len(addresses)):
          match = re.search('[[]\s*(\S*)\s*(\S*)\s*[]]', str(or_coords[i]))
          if match:
              if (i < len(addresses)-1):
                address_str += str(match.group(1) + ',' + match.group(2) + '|')
              else:
                address_str += str(match.group(1) + ',' + match.group(2))
        #print(address_str)
        return address_str

      request = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'
      origin_address_str = build_address_str(origin_addresses)
      dest_address_str = build_address_str(dest_addresses)
      request = request + '&origins=' + origin_address_str + '&destinations=' + \
                           dest_address_str + '&key=' + API_key
      jsonResult = urllib.request.urlopen(request).read()
      response = json.loads(jsonResult)
      return response

    def build_distance_matrix(response):
      distance_matrix = []
      l = 0
      for row in response['rows']:
        row_list = [row['elements'][j]['distance']['value'] for j in range(len(row['elements']))]
        row_list[0] = 0
        if l == 0:
           for n in range(len(row_list)):
               row_list[n] = 0
        l += 1
        distance_matrix.append(row_list)
        #print(distance_matrix)
      return distance_matrix

    def create_data_model(distance_matrix):
        """Stores the data for the problem."""
        data = {}
        data['distance_matrix'] = distance_matrix

        data['demands'] = or_score
        #print(data['demands'])
        vehicle_total = len(or_score)
        #print(vehicle_total)
        data['vehicle_capacities'] = [np.median(or_score)*vehicle_total/math.log(vehicle_total)]
        data['num_vehicles'] = 1
        data['depot'] = 0
        return data

    def print_solution(data, manager, routing, assignment):
        arr = []
        """Prints assignment on console."""
        # Display dropped nodes.
        dropped_nodes = 'Dropped nodes:'
        for node in range(routing.Size()):
            if routing.IsStart(node) or routing.IsEnd(node):
                continue
            if assignment.Value(routing.NextVar(node)) == node:
                dropped_nodes += ' {}'.format(manager.IndexToNode(node))
        print(dropped_nodes)
        # Display routes
        total_distance = 0
        total_load = 0
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
            route_distance = 0
            route_load = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                arr.append(node_index)
                route_load += data['demands'][node_index]
                plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
                previous_index = index
                index = assignment.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
            plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                     route_load)
            plan_output += 'Distance of the route: {}m\n'.format(route_distance)
            plan_output += 'Load of the route: {}\n'.format(route_load)
            print(plan_output)
            total_distance += route_distance
            total_load += route_load
        arr.pop(0)
        print('Total Distance of all routes: {}m'.format(total_distance))
        print('Total Load of all routes: {}'.format(total_load))
        return arr


    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_data()
    addresses = data['coording']
    API_key = data['API_key']
    distance_matrix = create_distance_matrix(data)
    #print(distance_matrix)
    data = create_data_model(distance_matrix)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)


    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')
    # Allow to drop nodes.
    penalty = 100000
    for node in range(1, len(data['distance_matrix'])):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if assignment:
        arr = print_solution(data, manager, routing, assignment)
        print("here")

    length = len(or_df)
    order = [0] * length

    for i,j in enumerate(arr):
        print(j, i+1)
        order[j-1] = i+1

    or_df['order'] = order
    or_df = or_df.sort_values(by=['order'])
    g = pd.concat([g, or_df], sort=False)

g = g[g['order'] != 0]
g.to_csv('most30.csv')