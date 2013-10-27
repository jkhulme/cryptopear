#!/usr/bin/env python
#198.211.120.146

import socket as sok
import select
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
  def __init__(self, destination=LOCALHOST):
    self.server = sok.socket(sok.AF_INET, sok.SOCK_STREAM)
    self.server.connect((destination, PORT))

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
    decrypted = self.pri.decrypt(data)
    return pkcs1_unpad(decrypted)

  def __encrypt__(self, data):
    encrypted = PKCS1_OAEP.new(self.server_pub).encrypt(data)
    return encrypted

  def __send__(self, data):
    self.server.send(base64.b64encode(data) + "\n")

  def __receive__(self):
    return base64.b64decode(self.server.recv(BUFFER_S))

  def decrypted_receive(self):
    return self.__decrypt__(self.__receive__())

  def encrypted_send(self, data):
    self.__send__(self.__encrypt__(data))

  def get_recent_messages(self):
    data = self.decrypted_receive()
    message = handle_event_json(json.loads(data))
    self.messages.append(message)
    return self.messages[-MESSAGE_LIMIT:]


  def ident(self, my_ident):
    print "Sending our pubkey"
    identity_dict = {'type' : 'ident', 'ident' : my_ident}
    identity_dict['ident']['pubkey'] = self.pub.exportKey()
    self.__send__(self.pub.exportKey())
    print "Receiving server's pubkey"
    data = self.__receive__()
    key = json.loads(data)['pubkey']
    self.server_pub = RSA.importKey(key)
    print "Stored pubkey: " + self.server_pub.exportKey()
    print "Ident complete"
    return self

  def loop(self):
    self.server.setblocking(0)
    while True:
      # Check if any user input should be sent
      term_action = select.select([sys.stdin], [], [], IO_TIMEOUT_S)[0]
      if term_action:
        outgoing_message = sys.stdin.readline()
        self.encrypted_send(outgoing_message)

      #Check if there there is any received data in the socket buffer
      sock_action = select.select([self.server], [], [], IO_TIMEOUT_S)[0]
      if sock_action:
        # Replace the screen contents with the updated message buffer
        os.system('clear')
        print "".join(self.get_recent_messages())
    self.server.close()

if __name__ == "__main__":
  my_ident = {
    'name' : 'Anne Onymous', 'photo' : 'Null'
  }
  PearClient(destination=DESTINATION).ident(my_ident).loop()
