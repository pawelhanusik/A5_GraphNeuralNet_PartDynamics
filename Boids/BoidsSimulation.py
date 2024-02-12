import pyglet
import pickle
import imageio
import math
from pyglet.gl import (
    Config,
    glEnable, glBlendFunc, glLoadIdentity, glClearColor,
    GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_COLOR_BUFFER_BIT)
from pyglet.window import key
from World import World

frames = []
fps = []

# Config
numBoids = 150
walls = 1  # 0 = no walls, 1 = walls
rangeClustering = 3  # 0=none, 1=DBSCAN, 2=Tiling, 3=DBSCAN w/ Tiling
reclusterNum = 20
tileWidth = 40
clusterIndicators = 1  # 0 = no indicator, 1 = indicators

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

boidConfig = [boidRange, boidCollisionRange, boidCollisionWeight, boidVelMatchingWeight, boidFlockCenteringWeight,
              boidwalAvoidWeight, boidMinSpeed, boidMaxSpeed, boidSize, boidViewAngle, walls, boidWallRange]
# 640, 360
world = World(width, height, numBoids, boidConfig, rangeClustering, reclusterNum, tileWidth, clusterIndicators);

window = pyglet.window.Window(width, height,
                              fullscreen=False,
                              caption="Boids Simulation")

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

fps_display = pyglet.window.FPSDisplay(window=window)


def write_simulation_data_to_file(world, filename):
    with open(filename, 'ab') as f:
        for boid in world.boids:
            data = (boid.position[0], boid.position[1], math.sqrt(boid.velocity[0] ** 2 + boid.velocity[1] ** 2))
            pickle.dump(data, f)


def update(dt):
    world.updateLocalBoids()
    world.updateBoidPos(1 / 15)
    write_simulation_data_to_file(world, './output/simulation_data.dat')
    pyglet.image.get_buffer_manager().get_color_buffer().save('./frames/frame.png')
    frames.append(imageio.v2.imread('./frames/frame.png'))


# schedule world updates as often as possible
pyglet.clock.schedule(update)


@window.event
def on_draw():
    glClearColor(0.1, 0.1, 0.1, 1.0)
    window.clear()
    glLoadIdentity()

    # fps_display.draw()

    batch = pyglet.graphics.Batch()
    vl = world.getVetexBatch()
    cl = world.getColourBatch()
    for i in range(0, len(vl)):
        batch.add(3, pyglet.gl.GL_TRIANGLES, None,
                  ('v2f', (vl[i][0], vl[i][1], vl[i][2], vl[i][3], vl[i][4], vl[i][5])),
                  ('c3B', (cl[i][0], cl[i][1], cl[i][2], cl[i][0], cl[i][1], cl[i][2], cl[i][0], cl[i][1], cl[i][2])))

    batch.draw()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.Q:
        if rangeClustering == 0:
            imageio.mimsave('recordings/simulation.mp4', frames)
        if rangeClustering == 1:
            imageio.mimsave('recordings/simulation_DBSCAN.mp4', frames)
        if rangeClustering == 2:
            imageio.mimsave('recordings/simulation_Tiling.mp4', frames)
        if rangeClustering == 3:
            imageio.mimsave('recordings/simulation_DBSCAN_Tiling.mp4', frames)

        pyglet.app.exit()


pyglet.app.run()
