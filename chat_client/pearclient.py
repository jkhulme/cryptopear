#!/usr/bin/env python

import socket as sok
import select
import string
import sys
import os

LOCALHOST, PORT, BUFFER_S = '127.0.0.1', 8008, 1024

if len(sys.argv) > 1:
  DESTINATION = sys.argv[1]
else:
  DESTINATION = LOCALHOST

IO_TIMEOUT_S = 0.1
MESSAGE_LIMIT = 10

server = sok.socket(sok.AF_INET, sok.SOCK_STREAM)
server.connect((DESTINATION, PORT))
server.setblocking(0)

messages = []

server.send("The magic word\n")

while True:
  # Check if any user input should be sent
  term_action = select.select([sys.stdin], [], [], IO_TIMEOUT_S)[0]
  if term_action:
    outgoing_message = sys.stdin.readline()
    server.send(outgoing_message)

  #Check if there there is any received data in the socket buffer
  sock_action = select.select([server], [], [], IO_TIMEOUT_S)[0]
  if sock_action:
    data = server.recv(BUFFER_S)
    messages.append(data)
    # Replace the screen contents with the updated message buffer
    os.system('clear')
    print "".join(messages[-MESSAGE_LIMIT:])

server.close()
