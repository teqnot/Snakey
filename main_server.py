import socket, time, random, json, threading
from tkinter import *

port = xxx
host = 'xxx.xxx.xxx.xxx' # ip-idress of your choice

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))

quit = False
label = None
clients = [] #basically adresses of all the clients (but, at this point, not more than 2)
print ('[Server "Snaykey" started]')
time.sleep(0.5)
print ('[Connecting]')

width1 = 640
height1 = 480
cell_size = 20
assert width1 % cell_size == 0, "Window width must be a multiple of cell size."
assert height1 % cell_size == 0, "Window height must be a multiple of cell size."
cell_width = int(width1 / cell_size)
cell_height = int(height1 / cell_size)

def getRandomLocation():
    # getting a new location for the apple
    return {'x': random.randint(0, cell_width - 1), 'y': random.randint(0, cell_height - 1)}

# a window for comfortably seeing the received coordinates
def window():
    global label
    root = Tk()
    label = Label(root, text = '', fg='black')
    label.pack()
    root.mainloop()
    
thread = threading.Thread(target = window)
thread.start()
time.sleep(1)
apple_coords = getRandomLocation()

# main communication loop
while not quit:
    data, adr = s.recvfrom(1024)
    data = data.decode('utf-8')
    data = json.loads(data)
    apple = data[0]
    wormCoords = data[2]

    if data[1] == False:
        apple_coords = getRandomLocation()
        print('[Getting New Apple Location]')

    data2 = [apple_coords, wormCoords]
    data2 = json.dumps(data2)
    data2 = data2.encode('utf-8')

    # adding the client to the base
    if adr not in clients:
        clients.append(adr)

    # checking if the server is not sending the received data to the OP
    for client in clients:
        if adr != client:
            # sending the data (WormCoords, AppleCoords) to the other player
            s.sendto(data2, client)

    my_text = data2
    # displaying the received data
    label.config(text = my_text)
