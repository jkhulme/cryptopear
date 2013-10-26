#!/usr/bin/env python
#198.211.120.146

import socket as sok
import select
import string
import sys
import os
import json
import rsa
import base64

from event_printer import handle_event_json

LOCALHOST, PORT, BUFFER_S = '127.0.0.1', 8008, 1024

if len(sys.argv) > 1:
  DESTINATION = sys.argv[1]
else:
  DESTINATION = LOCALHOST

IO_TIMEOUT_S = 0.1
MESSAGE_LIMIT = 40

class PearClient:
  def __init__(self):
    server = sok.socket(sok.AF_INET, sok.SOCK_STREAM)
    server.connect((DESTINATION, PORT))
    server.setblocking(0)
    self.server = server

    self.messages = []

    self.pub, self.pri = rsa.newkeys(2048, poolsize=4)

  def ident(self):
    self.server.send(base64.b64encode(self.pub._save_pkcs1_pem()) + "\n")
    return self

  def loop(self):
    while True:
      # Check if any user input should be sent
      term_action = select.select([sys.stdin], [], [], IO_TIMEOUT_S)[0]
      if term_action:
        outgoing_message = sys.stdin.readline()
        self.server.send(outgoing_message)

      #Check if there there is any received data in the socket buffer
      sock_action = select.select([self.server], [], [], IO_TIMEOUT_S)[0]
      if sock_action:
        try:
          # Parse received json data
          data = self.server.recv(BUFFER_S)
          decrypted = rsa.decrypt(base64.b64decode(data), self.pri)
          parsed = json.loads(decrypted)
        except ValueError:
          continue

        message = handle_event_json(parsed)
        self.messages.append(message)

        # Replace the screen contents with the updated message buffer
        os.system('clear')
        print "".join(self.messages[-MESSAGE_LIMIT:])
    self.server.close()

PearClient().ident().loop()
