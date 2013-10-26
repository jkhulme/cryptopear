#!/usr/bin/env ruby

require 'socket'
require 'thread'
require 'json'
require 'openssl'
require 'base64'

require_relative './lib/client'

class PearServer

  def initialize
    @server_socket = TCPServer.new 8008
    @rsa = OpenSSL::PKey::RSA.new(2048)
  end

  def work
    # Error handling
    errors = Queue.new
    Thread.new do
      while (error = errors.pop) do
        puts error.inspect
      end
    end

    # Spawn a new worker thread for each client socket opened
    loop { Thread.start(@server_socket.accept) { |client_socket|
      begin
        # State is handled via the user model, first transmission is pubkey
        client = PearClient.new(client_socket, encoded_pubkey).commit
        announce quitjoin_event :join, client.name

        # Relay any received data to the other clients
        loop do
          if !(data = client.listen).nil?
            announce message_from client.name, data
          else
            announce quitjoin_event :quit, client.name
            return
          end
        end
      rescue Exception => ex
        errors.push ex
      end
    } }
  end

  private

  def encoded_pubkey
    Base64.encode64 @rsa.public_key.to_pem
  end

  def the_time
    Time.now.strftime '%H:%M'
  end

  def announce(line)
    puts line
    PearClient.all.each { |c| c.speak c.pkey_encrypt(line.to_json) }
  end

  def server_event(message)
    {
      time: the_time,
      type: 'event',
      event: {
        message: message
      }
    }
  end

  def quitjoin_event(type, name)
    {
      time: the_time,
      type: 'quitjoin',
      quitjoin: {
        event: type.to_s,
        name: name
      }
    }
  end

  def message_from(name, message)
    {
      time: the_time,
      type: 'message',
      message: {
        sender: name,
        body: message
      }
    }
  end

end

PearServer.new.work

