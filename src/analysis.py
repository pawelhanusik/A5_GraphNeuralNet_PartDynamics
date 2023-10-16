from data import DataReader

dataReader = DataReader("data.txt")
dataReader.open()

nBoids = dataReader.getNumberOfBoids()
print("Number of boids:", nBoids)

for i in range(1000000):
    boidsData = dataReader.getFrameBoidsData()

    if boidsData is None:
        break

    print(boidsData)
