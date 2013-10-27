require 'thread'
require 'socket'
require 'openssl'
require 'base64'
require 'json'

require_relative 'namespoofer'

class Pearader

  def initialize(total_clients=2)
    @mutex = Mutex.new
    @total = total_clients
    @connected = []
    @num_connects = 0
  end

  def connect(client)
    @mutex.synchronize do
      @connected.push({name: client.realname, photo: client.photo})
      @num_connects += 1
    end
    self
  end

  def broadcast_all(client)
    ready = false
    until ready
      @mutex.synchronize { ready = @num_connects == @total }
      break if ready
      puts "Waiting for everyone, #{@num_connects} so far"
      sleep 1
    end

    client.speak @connected.to_json
  end

end

class PearClient
  @@clients = []

  attr_reader :id, :socket, :name, :realname, :photo

  def initialize(socket, encoded_pubkey)
    @socket = socket
    puts "Receiving their pubkey"
    ident = JSON.parse(listen)
    puts ident
    @realname = ident['ident']['name']
    @photo = ident['ident']['photo']
    @pubkey = ident['ident']['pubkey']
    @messages = Queue.new
    puts "Sending out pubkey"
    @messages.push (encoded_pubkey << "\n")
    @responder = Thread.new do
      while (message = @messages.pop)
        @socket.write (Base64.encode64(message) << "\n")
      end
    end
    puts "Ident complete"
  end

  def pkey_encrypt(message)
    key = OpenSSL::PKey::RSA.new @pubkey
    key.public_encrypt(message)
  end

  def speak(message)
    @messages.push message
  end

  def listen
   Base64.decode64 @socket.gets
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

