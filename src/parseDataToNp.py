import numpy as np
from data import DataReader
import sys

if len(sys.argv) <= 3:
    print("Not enough args")
    sys.exit(1)

inputFilePath = sys.argv[1]
outputFilesPrefix = sys.argv[2]
outputFilesPostfix = sys.argv[3]



dataReader = DataReader(inputFilePath)
dataReader.open()

boidsAmount = dataReader.getNumberOfBoids()
data = []

while True:
    newFrame = dataReader.getFrameBoidsData()
    
    if newFrame is None:
        break

    data.append(newFrame)

# -----

time_steps = len(data)

# Preparing the timeseries data as a numpy array
timeseries_data = np.array(data)

# Assuming you have a function to calculate whether two boids are connected
# For example, you can consider them connected if they are within a certain distance
def are_connected(boid1, boid2):
    distance = np.sqrt((boid1[0] - boid2[0])**2 + (boid1[1] - boid2[1])**2)
    # Define your connection criteria here (e.g., distance threshold)
    connection_threshold = 12 * 15
    return distance < connection_threshold

# Preparing the edge data as a binary adjacency matrix
"""
edge_data = np.zeros((time_steps, boidsAmount, boidsAmount), dtype=np.int8)
for t in range(time_steps):
    for i in range(boidsAmount):
        for j in range(boidsAmount):
            if i != j:
                edge_data[t, i, j] = are_connected(data[t][i], data[t][j])
"""
edge_data = np.zeros((boidsAmount, boidsAmount), dtype=np.int8)
for i in range(boidsAmount):
    for j in range(boidsAmount):
        if i != j:
            edge_data[i, j] = 1

# Preparing the time data (you can use an array of time steps or actual timestamps if available)
time_data = np.arange(time_steps)

# Save the numpy arrays to files
np.save(outputFilesPrefix + 'timeseries' + outputFilesPostfix + '.npy', timeseries_data)
np.save(outputFilesPrefix + 'edge' + outputFilesPostfix + '.npy', edge_data)
np.save(outputFilesPrefix + 'time' + outputFilesPostfix + '.npy', time_data)
