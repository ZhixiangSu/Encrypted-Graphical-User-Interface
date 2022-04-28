# Starter code for assignment 3 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# NAME
# EMAIL
# STUDENT ID
import socket
import json
import time
from ds_protocol import extract_json
def send(server:str, port:int, username:str, password:str, message:str, bio:str=None):
  '''
  The send function joins a ds server and sends a message, bio, or both

  :param server: The ip address for the ICS 32 DS server.
  :param port: The port where the ICS 32 DS server is accepting connections.
  :param username: The user name to be assigned to the message.
  :param password: The password associated with the username.
  :param message: The message to be sent to the server.
  :param bio: Optional, a bio for the user.
  '''
  #TODO: return either True or False depending on results of required operation
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.connect((server,port))
  msg=json.dumps({"join": {"username": username,"password": password,"token":""}})
  s.sendall(msg.encode('UTF-8'))
  response=extract_json(s.recv(4096).decode('UTF-8'))
  if response.type=="Error":
    print("Error:"+response.message)
    return False
  else:
    print(response.message)
  token=response.token
  if token is None:
    print("Error: No token received")
    return False
  if bio is None:
    msg=json.dumps({"token":token, "post": {"entry": message,"timestamp": time.time()}})
    s.sendall(msg.encode('UTF-8'))
    response = extract_json(s.recv(4096).decode('UTF-8'))
    if response.type == "Error":
      print("Error:" + response.message)
      return False
    else:
      print(response.message)
  else:
    msg=json.dumps({"token":token, "post": {"entry": message,"timestamp": time.time()},"bio": {"entry": bio,"timestamp": time.time()}})
    s.sendall(msg.encode('UTF-8'))
    response = extract_json(s.recv(4096).decode('UTF-8'))
    if response.type == "Error":
      print("Error:" + response.message)
      return False
    else:
      print(response.message)
    msg = json.dumps({"token": token,"bio": {"entry": bio, "timestamp": time.time()}})
    s.sendall(msg.encode('UTF-8'))
    response = extract_json(s.recv(4096).decode('UTF-8'))
    if response.type == "Error":
      print("Error:" + response.message)
      return False
    else:
      print(response.message)

  return True

# send('localhost',3021,'user1','pwd123',"this is message.","this is bio.")