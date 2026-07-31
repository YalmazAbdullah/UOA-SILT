This client serves as an intermediary between the server and target.
Its main purpose is to handle client side state logic, OS level logging and forward requests from the target to the server

Client Setup
- Create Session
- Send Hello message to server

Create dummy client in Python, C#, Javascript
- sends a hello world log over UDP websocket

Client
- Receive UPD messages 
- Forward the messages to the server
- Capture Mouse movement
- Capture Keyboard movement


========================================

Here is short documentation to what I did 

## Dummy Targets

HOST = "127.0.0.1"
PORT = 5000 

In Python, C#, and Javascript will send a UDP packet. 

## Target_Listener 

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 5000

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000 

Will first connect to a target socket and listen in, then when data comes in- will grab it and add the client_time and try to send it to the server. 