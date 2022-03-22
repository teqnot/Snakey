# Snakey PyGame Online Game
###### A basic game of Snake with a twist. A two-player multiplayer option is available

## Server Part

Server plays the role of an app distributing the data between two connected game clients. Receiving coordinates from the first client, sending them to the second one, and vice-versa. 

It operates on the **sockets** library, creating a dedicated connection to each one of the clients and then receiving the data through **SOCK_DGRAM**.
Basically, all this host does is rerouting the received data to the right addressee.

## Client Part
That's where the magic happens. Connecting to server, your client starts to send all the data about the game to the server. So every screen update the position of the apple, your snake and a flag, determining the existance of the apple, will be send to the server. If there's a second player, in parallel with sending data your client will receive such, drawing the position of the second snake on your screen. 

This happens with the help of previously mentioned **sockets** library, connecting to the server through a designated channel. 
