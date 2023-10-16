import struct

class DataWriter:
    def __init__(self, path):
        self.path = path
        self.isOpen = False
        self.tmpData = b''
        self.tmpDataAmount = 0
        self.file = None
    
    def open(self):
        self.file = open(self.path, 'wb')
        self.isOpen = True
    
    def close(self):
        self.flush()
        self.isOpen = False
        self.file.close()

    def numberOfBoids(self, n):
        if self.isOpen:
            self.file.write(struct.pack('i', n))
    
    def writeBoidData(self, x, y, a):
        self.tmpData += struct.pack('fff', x, y, a)
        self.tmpDataAmount += 1

        if self.tmpDataAmount >= 1000:
            self.flush()
    
    def flush(self):
        self.file.write(self.tmpData)
        self.tmpData = b''
        self.tmpDataAmount = 0

class DataReader:
    def __init__(self, path) -> None:
        self.path = path
        self.isOpen = False
        self.file = None
        
        self.nBoids = 0
    
    def open(self):
        self.file = open(self.path, 'rb')
        self.isOpen = True

        self.nBoids = struct.unpack('i', self.file.read(4))[0]
    
    def close(self):
        self.file.close()
        self.isOpen = False

    def getNumberOfBoids(self):
        return self.nBoids
    
    def getFrameBoidsData(self):
        data = []

        for i in range(self.nBoids):
            try:
                data.append(struct.unpack('fff', self.file.read(12)))
            except:
                return None
        
        return data
