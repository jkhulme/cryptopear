#!/usr/bin/env ruby

require 'socket'
require 'thread'

require_relative './lib/client'


class PearServer
  def initialize
    @server_socket = TCPServer.new 8008
  end

  def work
    loop { Thread.start(@server_socket.accept) { |client_socket|

      client = PearClient.new(client_socket).commit
      puts "# New connection! ID: #{client.id}, Random Name: #{client.name}"

      loop do
        data = client.listen
        return if data.nil?

        line = "<#{client.name}(#{client.id})> #{data}"
        puts line

        PearClient.all.each { |c| c.speak line }
      end

    } }
  end

end

PearServer.new.work

