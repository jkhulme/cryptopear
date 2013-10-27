#!/usr/bin/env ruby

require 'socket'
require 'thread'
require 'json'
require 'openssl'
require 'base64'

require_relative './lib/client'

class PearServer

  def initialize(total)
    @mutex = Mutex.new
    @server_socket = TCPServer.new 8008
    @rsa = OpenSSL::PKey::RSA.new(2048)
    puts "Generated pubkey: " << @rsa.public_key.to_pem

    @ready = 0
    @total = total
  end

  def block_until_all_ready
    ready = false
    while !ready
      @mutex.synchronize { ready = @ready == @total }
      break if ready
      sleep 1
    end
  end

  def client_ready
    @mutex.synchronize { @ready += 1 }
  end

  def work
    # Error handling
    errors = Queue.new
    Thread.new do
      while (error = errors.pop) do
        puts error.inspect
      end
    end

    pearader = Pearader.new(@total)

    # Spawn a new worker thread for each client socket opened
    loop { Thread.start(@server_socket.accept) { |client_socket|
      begin
        puts "New client thread"
        # State is handled via the user model, first transmission is pubkey
        client = PearClient.new(client_socket, pubkey).commit
        pearader.connect(client).broadcast_all(client)

        votes = client.listen

        client_ready
        block_until_all_ready

        announce quitjoin_event :join, client.name

        # Relay any received data to the other clients
        loop do
          if !(data = client.listen).nil?
            announce message_from client.name, decrypt_message(data)
          else
            announce quitjoin_event :quit, client.name
            break
          end
        end
      rescue Exception => ex
        errors.push ex
        errors.push ex.backtrace
      end
    } }
  end

  private

  def decrypt_message(data)
    @rsa.private_decrypt(data, OpenSSL::PKey::RSA::PKCS1_OAEP_PADDING)
  end

  def pubkey
    {type: 'pubkey', pubkey: @rsa.public_key.to_pem}.to_json
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

PearServer.new(ARGV.last.to_i).work

