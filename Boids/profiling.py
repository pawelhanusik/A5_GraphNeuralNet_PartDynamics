import time
import matplotlib.pyplot as plt
from World import *
from collections import defaultdict
from tqdm import tqdm

# Config
numBoids = 200
walls = 1  # 0 = no walls, 1 = walls
reclusterNum = 20
tileWidth = 40
clusterIndicators = 0  # 0 = no indicator, 1 = indicators
global rangeClustering

boidRange = tileWidth ** 2
boidCollisionRange = 14 ** 2
boidCollisionWeight = 4
boidVelMatchingWeight = 0.5
boidFlockCenteringWeight = 0.3
boidWallRange = 60
boidwalAvoidWeight = 5000
boidMinSpeed = 45
boidMaxSpeed = 60
boidSize = 15
boidViewAngle = 290 * (math.pi / 180)

width = 1200
height = 800


def profile_simulation(num_boids_list, basic_time=None):
    slowdowns = []
    boidConfig = [boidRange, boidCollisionRange, boidCollisionWeight, boidVelMatchingWeight,
                  boidFlockCenteringWeight, boidwalAvoidWeight, boidMinSpeed, boidMaxSpeed, boidSize, boidViewAngle,
                  walls, boidWallRange]

    if basic_time is None:
        basic_value = 200
        iter_range = np.concatenate(([basic_value], num_boids_list))
    else:
        iter_range = num_boids_list

    for num_boids in iter_range:
        start_time = time.time()
        world = World(width, height, num_boids, boidConfig, rangeClustering, reclusterNum, tileWidth, clusterIndicators)

        world.updateLocalBoids()
        world.updateBoidPos(1 / 15)

        simulation_time = time.time() - start_time

        if basic_time is None:
            basic_time = simulation_time
        else:
            slowdown = basic_time / simulation_time
            slowdowns.append(slowdown)

    return slowdowns, basic_time


def generate_slowdowns_plot(num_boids_list, slowdowns):
    plt.figure()
    plt.plot(num_boids_list, slowdowns, label='Basic simulation, without any spatial divisions')
    plt.xlabel('Number of boids')
    plt.ylabel('Slowdown')
    plt.title('Slowdowns with respect to the number of boids (200 boids as reference)')
    plt.grid()
    plt.legend()
    plt.savefig('results/slowdowns.png')


def generate_all_slowdowns_plot(num_boids_list, slowdowns_all):
    algorithms = {
        0: "basic",
        1: "DBSCAN",
        2: "Tiling",
        3: "DBSCAN with Tiling"
    }

    plt.figure()
    for i in range(0, 4):
        plt.plot(num_boids_list, slowdowns_all[i], label=f'{algorithms[i]}')
    plt.xlabel('Number of boids')
    plt.ylabel('Slowdown')
    plt.title('Comparison of slowdowns for different algorithms')
    plt.yscale("log")
    plt.grid()
    plt.legend()
    plt.savefig('results/slowdowns_all.png')


def main():
    global rangeClustering
    num_boids_list = np.arange(50, 1001, 50)
    slowdowns_all = defaultdict(lambda: [])
    basic_time = None
    for i in tqdm([0, 1, 2, 3]):  # 0=none, 1=DBSCAN, 2=Tiling, 3=DBSCAN w/ Tiling
        rangeClustering = i
        if basic_time is None:
            slowdowns, basic_time = profile_simulation(num_boids_list, basic_time)
        else:
            slowdowns, _ = profile_simulation(num_boids_list, basic_time)
        slowdowns_all[rangeClustering] = slowdowns
        if rangeClustering == 0:
            generate_slowdowns_plot(num_boids_list, slowdowns)
    generate_all_slowdowns_plot(num_boids_list, slowdowns_all)




if __name__ == "__main__":
    main()
