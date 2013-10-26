#!/usr/bin/env ruby

require 'socket'
require 'thread'
require 'json'

require_relative './lib/client'

class PearServer

  def initialize
    @server_socket = TCPServer.new 8008
  end

  def work
    # Spawn a new worker thread for each client socket opened
    loop { Thread.start(@server_socket.accept) { |client_socket|

      # State is handled via the user model
      client = PearClient.new(client_socket).commit
      announce "-> #{client.name} has joined the chat.".yellow

      # First transmission is authentication
      handshake = client.listen
      return unless handshake == "The magic word\n"
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

    } }
  end

  private

  def the_time
    Time.now.strftime '%H:%M'
  end

  def announce(line)
    puts line
    PearClient.all.each { |c| c.speak line.to_json }
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

