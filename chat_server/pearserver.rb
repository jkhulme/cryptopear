#!/usr/bin/env ruby

require 'socket'
require 'thread'
require 'colored'

require_relative './lib/client'


class PearServer
  def initialize
    @server_socket = TCPServer.new 8008
  end

  def announce(line)
    puts line
    PearClient.all.each { |c| c.speak line }
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
      announce "-> #{client.name} has joined the chat.".yellow

      # Relay any received data to the other clients
      loop do
        data = client.listen

        if data.nil?
          announce "<- #{client.name} has left the chat.".red
          return
        end

        announce "<#{client.name}(#{client.id})>".green << " #{data}"
      end

    } }
  end

end

PearServer.new.work

