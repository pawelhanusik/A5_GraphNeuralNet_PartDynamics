import math
import numpy as np

class Boid:
    
    def __init__(self, position, wrapBounds, velocity, colour, numBoids, config):
        self.position = position
        self._wrapBounds = wrapBounds
        self.velocity = velocity
        self._colour = colour 
        self._boidMask = np.zeros(numBoids)

        self._range = config[0]
        self._collisionRange = config[1]
        self._collisionWeight = config[2]
        self._velMatchingWeight = config[3]
        self._flkCenteringWeight = config[4]
        self._walAvoidWeight = config[5]
        self._minSpeed = config[6]
        self._maxSpeed = config[7]
        self._size = config[8]
        self._viewAngle = config[9]
        self._walls = config[10]
        self._wallRange = config[11]


    def getVertexList(self):
        p1 = [self.position[0] + self._size/2, self.position[1]]
        p2 = [self.position[0] - self._size/2, self.position[1] - self._size/2]
        p3 = [self.position[0] - self._size/2, self.position[1] + self._size/2]
        #rotation
        a = math.atan2(self.velocity[1], self.velocity[0])# + 3*math.pi/2
        p2x = math.cos(a) * (p2[0] - p1[0]) - math.sin(a) * (p2[1] - p1[1]) + p1[0]
        p2y = math.sin(a) * (p2[0] - p1[0]) + math.cos(a) * (p2[1] - p1[1]) + p1[1]
        p3x = math.cos(a) * (p3[0] - p1[0]) - math.sin(a) * (p3[1] - p1[1]) + p1[0]
        p3y = math.sin(a) * (p3[0] - p1[0]) + math.cos(a) * (p3[1] - p1[1]) + p1[1]

        return [p1[0], p1[1], p2x, p2y, p3x, p3y]

    def getPosition(self):
        return [self.position[0], self._position[1]]

    def setColour(self, colour):
        self._colour = colour 

    def addLocal(self, boid, distance):
        self._localBoids.append(boid)
        self._localRange.append(distance)

    def updatePos(self, dt, boids):

        indexs = np.where(self._boidMask == 1)
        num = np.size(indexs)
        if num > 0:
            colVec = self.collisionAvoidence(indexs, boids)
            macVec = self.velocityMatching(num, indexs, boids)
            flkVec = self.flockCentering(num, indexs, boids)
         
            self.velocity[0] += colVec[0] * self._collisionWeight    
            self.velocity[1] += colVec[1] * self._collisionWeight   
            self.velocity[0] += macVec[0] * self._velMatchingWeight
            self.velocity[1] += macVec[1] * self._velMatchingWeight
            self.velocity[0] += flkVec[0] * self._flkCenteringWeight
            self.velocity[1] += flkVec[1] * self._flkCenteringWeight

        if self._walls == 1:
            walVec = self.avoidWall()  
            self.velocity[0] += walVec[0] * self._walAvoidWeight     
            self.velocity[1] += walVec[1] * self._walAvoidWeight     

        #Constrain Velocity
        speed = np.sqrt(self.velocity[0]**2 + self.velocity[1]**2) + 1
        if speed > self._maxSpeed:
            self.velocity[0] *= self._maxSpeed / speed
            self.velocity[1] *= self._maxSpeed / speed
        elif speed < self._minSpeed:
            self.velocity[0] *= self._minSpeed / speed 
            self.velocity[1] *= self._minSpeed / speed 

        #move
        self.position[0] += dt * self.velocity[0]
        self.position[1] += dt * self.velocity[1]

        if self._walls == 0:
            if self.position[0] >= self._wrapBounds[0]:
                self.position[0] = 0
            elif self.position[0] < 0:
                self.position[0] = self._wrapBounds[0]
            if self.position[1] >= self._wrapBounds[1]:
                self.position[1] = 0
            elif self.position[1] < 0:
                self.position[1] = self._wrapBounds[1]

    def angleBetweenBoids(self, vel, diff):
        a = math.atan2(self.velocity[1], self.velocity[0])# + 3*math.pi/2 #angle of boid
        a1 = math.atan2(diff[1],  diff[0]) #angle to boid
        if a < 0:
            a += math.pi*2
        if a1 < 0:
            a1 += math.pi*2

        return np.abs(a-a1)

    def collisionAvoidence(self, indexs, boids):
        xTotal, yTotal = 0, 0
        for i in np.nditer(indexs):
            difference = [boids[i].position[0] - self.position[0], boids[i].position[1] - self.position[1]]
       
            if difference[0]**2 + difference[1]**2 < self._collisionRange:
                xTotal -= boids[i].position[0] - self.position[0]
                yTotal -= boids[i].position[1] - self.position[1]

        return [xTotal, yTotal]

    def velocityMatching(self, num, indexs, boids):
        xTotal, yTotal = 0, 0
        for i in np.nditer(indexs):
            xTotal += boids[i].velocity[0]
            yTotal += boids[i].velocity[1]

        return [xTotal/num - self.velocity[0], yTotal/num - self.velocity[1]]
        
    def flockCentering(self, num, indexs, boids):
        xTotal, yTotal = 0, 0
        for i in np.nditer(indexs):
            xTotal += boids[i].position[0]
            yTotal += boids[i].position[1]

            self._boidMask[i] = 0

        return [xTotal/num - self.position[0], yTotal/num - self.position[1]]

    def avoidWall(self):
        x = 0; y = 0;
        if self.position[0] < self._wallRange:
            x = 1/np.max([self.position[0],1])**2
        if self._wrapBounds[0] < self._wallRange + self.position[0]:
            x = -1/np.max([(self._wrapBounds[0]-self.position[0]),1])**2

        if self.position[1] < self._wallRange:
            y = 1/np.max([self.position[1],1])**2
        if self._wrapBounds[1] < self._wallRange + self.position[1]:
            y = -1/np.max([(self._wrapBounds[1]-self.position[1]),1])**2

        return [x,y]