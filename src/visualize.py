import sys
import numpy as np
from math import sin, cos, atan2, radians, degrees
from random import randint
import pygame as pg
import sys
from boids import Boid



FLLSCRN = False
BOIDZ = 50
WRAP = False
BGCOLOR = (0, 0, 0)
WIDTH = 1200
HEIGHT = 800
FPS = 50  # min 48, max 90



class ArtificialBoid(Boid):
    def __init__(self, id, drawSurf, cHSV=None, timeseries_data=None, maxTime=None):
        super().__init__(id, drawSurf, cHSV)
        
        self.timeseries_data = timeseries_data
        self.timeseries_data_index = 0
        self.maxTime = maxTime
        
        ts_x, ts_y, ts_angle = self.__get_timeseries_params()
        self.rect = self.image.get_rect(
            center=(ts_x, ts_y))
        
        self.angle = ts_angle
        self.pos = pg.Vector2(ts_x, ts_y)

    def __get_timeseries_params(self):
        if self.maxTime is not None and self.timeseries_data_index >= self.maxTime:
            self.timeseries_data_index = 0
        
        if self.timeseries_data_index >= len(self.timeseries_data):
            self.timeseries_data_index += 1
            return None, None, None
        
        data = self.timeseries_data[self.timeseries_data_index]
        self.timeseries_data_index += 1
        
        return data

    def update(self, allBoids, dt, ejWrap=False):
        ts_x, ts_y, ts_angle = self.__get_timeseries_params()

        if ts_x is None or ts_y is None or ts_angle is None:
            # if do not have any more data, use default update
            return
            # return super().update(allBoids, dt, ejWrap)

        self.angle = ts_angle
        self.pos = pg.Vector2(ts_x, ts_y)

        selfCenter = pg.Vector2(self.rect.center)
        curW, curH = self.drawSurf.get_size()
        turnDir = xvt = yvt = yat = xat = 0
        turnRate = 120 * dt
        margin = 48
        
        # adjusts angle of boid image to match heading
        self.image = pg.transform.rotate(self.orig_image, -self.angle)
        self.rect = self.image.get_rect(
            center=self.rect.center)  # recentering fix
        self.direction = pg.Vector2(1, 0).rotate(self.angle).normalize()
        # (3.5 + (7-ncount)/14) * (fps * dt)
        # next_pos = self.pos + self.direction * (180 + (7-ncount)**2) * dt
        # self.pos = next_pos

        # optional screen wrap
        if ejWrap and not self.drawSurf.get_rect().contains(self.rect):
            if self.rect.bottom < 0:
                self.pos.y = curH
            elif self.rect.top > curH:
                self.pos.y = 0
            if self.rect.right < 0:
                self.pos.x = curW
            elif self.rect.left > curW:
                self.pos.x = 0
        
        # actually update position of boid
        self.rect.center = self.pos

def prepareData(data, predictionsAmount = 6):
    if len(data.shape) == 3:
        return [data]

    if len(data.shape) == 4:
        ret = []

        for i in range(predictionsAmount):
            # ret.append( data[:,i] )
            ret.append( data[i] )
        
        return ret
    
    raise Exception("Invalid data shape")

def main():
    if len(sys.argv) <= 3:
        print("Not enough args")
        sys.exit(1)

    timeseriesFilePath = sys.argv[1]
    predictionFilePath = sys.argv[2]
    predictionsAmount = int(sys.argv[3])

    maxTime = None
    
    if len(sys.argv) >= 5:
        if sys.argv[4] != 'None':
            maxTime = int(sys.argv[4])
    
    if len(sys.argv) >= 6:
        FPS = int(sys.argv[5])

    # np load timeseriesFilePath
    timeseries_data = np.load(timeseriesFilePath)
    prediction_data = np.load(predictionFilePath)

    timeseries_data = prepareData(timeseries_data, predictionsAmount)
    prediction_data = prepareData(prediction_data, predictionsAmount)


    # print(prediction_data[0].shape)
    # return

    timeseries_data = timeseries_data + prediction_data

    # INIT PYGAME
    pg.init()  # prepare window
    pg.display.set_caption("PyNBoids")
    
    try:
        pg.display.set_icon(pg.image.load("nboids.png"))
    except:
        print("FYI: nboids.png icon not found, skipping..")
    
    # setup fullscreen or window mode
    if FLLSCRN:  # screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        # pg.display.toggle_fullscreen()
        screen = pg.display.set_mode(currentRez, pg.SCALED)
        pg.mouse.set_visible(False)
    else:
        screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
    
    nBoids = []
    for batchNo in range(len(timeseries_data)):
        nBoids.append(pg.sprite.Group())

    COLORS = [(250, 85, 85)] # timeseries
    
    for i in range(1, len(timeseries_data)):
        COLORS.append((np.linspace(0, 50, len(timeseries_data)-1)[i-1], 85, 85)) # predictions
    
    for batchNo,batch_timeseries_data in enumerate(timeseries_data):
        color = COLORS[batchNo]
        for n in range(BOIDZ):  # spawns desired # of boidz
            nBoids[batchNo].add(ArtificialBoid(n, screen, color, batch_timeseries_data[:,n,:], maxTime))
    
    allBoids = []

    for batchNo in range(len(timeseries_data)):
        allBoids.append(nBoids[batchNo].sprites())
    

    clock = pg.time.Clock()

    running = True
    frame_count = 0

    # main loop
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                running = False
                break

        dt = clock.tick(FPS) / 1000
        screen.fill(BGCOLOR)

        for batchNo in range(len(timeseries_data)):
            nBoids[batchNo].update(allBoids[batchNo], dt, WRAP)
            nBoids[batchNo].draw(screen)
        
        pg.display.update()

        # frame_count += 1
        # filename = "ss/screen_%04d.png" % ( frame_count )
        # pg.image.save( screen, filename )

if __name__ == '__main__':
    main()
    pg.quit()
