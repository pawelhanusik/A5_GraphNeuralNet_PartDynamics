import sys
import numpy as np
from math import sin, cos, atan2, radians, degrees
from random import randint
import pygame as pg
import sys



FLLSCRN = False
BOIDZ = 50
WRAP = False
BGCOLOR = (0, 0, 0)
WIDTH = 1200
HEIGHT = 800
FPS = 50  # min 48, max 90



class Boid(pg.sprite.Sprite):
    def __init__(self, id, drawSurf, cHSV=None, timeseries_data=None, maxTime=None):
        super().__init__()
        
        self.id = id
        self.timeseries_data = timeseries_data
        self.timeseries_data_index = 0
        self.maxTime = maxTime
        self.affectedBy = []

        self.drawSurf = drawSurf
        self.image = pg.Surface((15, 15))
        self.image.set_colorkey(0)
        randColor = pg.Color(0)  # preps color so we can use hsva
        # randint(10,60) goldfish
        randColor.hsva = (randint(0, 360), 85, 85) if cHSV is None else cHSV
        pg.draw.polygon(self.image, randColor,
                        ((7, 0), (13, 14), (7, 11), (1, 14), (7, 0)))
        self.pSpace = (self.image.get_width() + self.image.get_height()) / 2
        self.orig_image = pg.transform.rotate(self.image.copy(), -90)
        self.direction = pg.Vector2(1, 0)  # sets up forward direction
        dS_w, dS_h = self.drawSurf.get_size()
        
        ts_x, ts_y, ts_angle = self.__get_timeseries_params()
        self.rect = self.image.get_rect(
            center=(ts_x, ts_y))
        
        self.angle = ts_angle
        self.pos = pg.Vector2(ts_x, ts_y)

    def __get_timeseries_params(self):
        if self.timeseries_data_index >= len(self.timeseries_data):
            self.timeseries_data_index = 0
        
        if self.maxTime is not None and self.timeseries_data_index >= self.maxTime:
            self.timeseries_data_index = 0
        
        data = self.timeseries_data[self.timeseries_data_index]
        self.timeseries_data_index += 1
        
        return data

    def update(self, allBoids, dt, ejWrap=False):
        ts_x, ts_y, ts_angle = self.__get_timeseries_params()

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

    def getParams(self):
        return [
            self.pos.x,
            self.pos.y,
            self.angle,
        ]
    
    def getAffectedBy(self):
        return self.affectedBy


def prepareData(data, predictionsAmount = 6):
    if len(data.shape) == 3:
        return [data]

    if len(data.shape) == 4:
        ret = []

        for i in range(predictionsAmount):
            ret.append( data[:,i] )
        
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
    nBoids = pg.sprite.Group()

    COLORS = [
        (250, 85, 85), # timeseries
        ( 50, 85, 85), # predictions
        ( 40, 85, 85),
        ( 30, 85, 85),
        ( 20, 85, 85),
        ( 10, 85, 85),
        (  0, 85, 85),
    ]
    for batchNo,batch_timeseries_data in enumerate(timeseries_data):
        color = COLORS[batchNo]
        for n in range(BOIDZ):  # spawns desired # of boidz
            nBoids.add(Boid(n, screen, color, batch_timeseries_data[:,n,:], maxTime))
    
    allBoids = nBoids.sprites()
    clock = pg.time.Clock()

    running = True

    # main loop
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                running = False
                break

        dt = clock.tick(FPS) / 1000
        screen.fill(BGCOLOR)

        nBoids.update(allBoids, dt, WRAP)
        nBoids.draw(screen)
        pg.display.update()

if __name__ == '__main__':
    main()
    pg.quit()
