#!/usr/bin/env python
#198.211.120.146

import socket as sok
import select
import string
import sys
import os
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
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
    self.server = server

    self.messages = []
    print "Generating RSA keypair..."
    new_key = RSA.generate(1024, e=65537)

    self.pub = new_key.publickey()
    self.pri = new_key
    print "Generated pubkey: " + self.pub.exportKey()

  def __decrypt__(self, data):
    def pkcs1_unpad(text):
      if len(text) > 0 and text[0] == '\x02':
        # Find end of padding marked by nul
        pos = text.find('\x00')
        if pos > 0:
          return text[pos+1:]
      return None
    decrypted = self.pri.decrypt(base64.b64decode(data))
    return pkcs1_unpad(decrypted)

  def __encrypt__(self, data):
    encrypted = PKCS1_OAEP.new(self.server_pub).encrypt(data)
    return base64.b64encode(encrypted) + "\n"

  def ident(self):
    print "Sending our pubkey"
    self.server.send(base64.b64encode(self.pub.exportKey()) + "\n")
    print "Receiving server's pubkey"
    data = self.server.recv(BUFFER_S)
    self.server.setblocking(0)
    decoded = base64.b64decode(data)
    key = json.loads(decoded)['pubkey']
    self.server_pub = RSA.importKey(key)
    print "Stored pubkey: " + self.server_pub.exportKey()
    print "Ident complete"
    return self

  def loop(self):
    while True:
      # Check if any user input should be sent
      term_action = select.select([sys.stdin], [], [], IO_TIMEOUT_S)[0]
      if term_action:
        outgoing_message = sys.stdin.readline()
        self.server.send(self.__encrypt__(outgoing_message))

      #Check if there there is any received data in the socket buffer
      sock_action = select.select([self.server], [], [], IO_TIMEOUT_S)[0]
      if sock_action:
        # Parse received json data
        data = self.server.recv(BUFFER_S)
        parsed = json.loads(self.__decrypt__(data))

        message = handle_event_json(parsed)
        self.messages.append(message)

        # Replace the screen contents with the updated message buffer
        os.system('clear')
        print "".join(self.messages[-MESSAGE_LIMIT:])
    self.server.close()

PearClient().ident().loop()
