#!/usr/bin/env python
#198.211.120.146

from termcolor import colored
import socket as sok
import select
import string
import sys
import os
import json

LOCALHOST, PORT, BUFFER_S = '127.0.0.1', 8008, 1024

if len(sys.argv) > 1:
  DESTINATION = sys.argv[1]
else:
  DESTINATION = LOCALHOST

IO_TIMEOUT_S = 0.1
MESSAGE_LIMIT = 40

server = sok.socket(sok.AF_INET, sok.SOCK_STREAM)
server.connect((DESTINATION, PORT))
server.setblocking(0)

messages = []

server.send("The magic word\n")

def handle_parsed_json(parsed):
  if parsed['type'] == 'quitjoin':
    name = parsed['quitjoin']['name']
    if parsed['quitjoin']['event'] == 'join':
      return colored(parsed['time'] + ' -> ' + name + ' has joined the channel.\n', 'yellow')
    else:
      return colored(parsed['time'] + ' <- ' + name + ' has left the channel.\n', 'red')
  elif parsed['type'] == 'message':
    sender = parsed['message']['sender']
    return colored('<' + sender + '> ', 'green') + parsed['message']['body']
  elif parsed['type'] == 'event':
    return colored(parsed['event']['message'] + '\n', 'cyan')

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

    try:
      # Parse received json data
      parsed = json.loads(data)
    except ValueError:
      continue

    message = handle_parsed_json(parsed)

    messages.append(message)
    # Replace the screen contents with the updated message buffer
    os.system('clear')
    print "".join(messages[-MESSAGE_LIMIT:])

server.close()
