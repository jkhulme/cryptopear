require 'thread'
require 'socket'

require_relative 'namespoofer'

class PearClient
  @@clients = []

  attr_reader :id, :socket, :name

  def initialize(socket)
    @socket = socket
    @messages = Queue.new
    @responder = Thread.new do
      while (message = @messages.pop)
        @socket.puts message
      end
    end
  end

  def speak(message)
    @messages.push message
  end

  def listen
    @socket.gets
  end

  def commit
    @@clients.push self
    @id = @@clients.length
    @name = NameSpoofer.new.random_name
    self
  end

  def self.all
    @@clients
  end

end

