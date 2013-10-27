require 'thread'
require 'socket'
require 'openssl'
require 'base64'

require_relative 'namespoofer'

class PearClient
  @@clients = []

  attr_reader :id, :socket, :name

  def initialize(socket, encoded_pubkey)
    @socket = socket
    puts "Receiving their pubkey"
    @pubkey = Base64.decode64(socket.gets)
    @messages = Queue.new
    puts "Sending out pubkey"
    @messages.push (encoded_pubkey << "\n")
    @responder = Thread.new do
      while (message = @messages.pop)
        @socket.puts message
      end
    end
    puts "Ident complete"
  end

  def pkey_encrypt(message)
    key = OpenSSL::PKey::RSA.new @pubkey
    Base64.encode64 key.public_encrypt(message)
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

