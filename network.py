from __future__ import print_function
import asyncore
import socket
import collections
import logging
import threading
import objlists
from gui import *

port = 21179
MAX_MESSAGE_LENGTH = 1024

class RemoteClient(asyncore.dispatcher):

	"""Wraps a remote client socket."""

	def __init__(self, host, socket, address):
		asyncore.dispatcher.__init__(self, socket)
		self.host = host
		self.outbox = collections.deque()

	def say(self, message):
		self.outbox.append(message)

	def handle_read(self):
		client_message = self.recv(MAX_MESSAGE_LENGTH)
		self.host.broadcast(client_message)

	def handle_write(self):
		if not self.outbox:
			return
		message = self.outbox.popleft()
		if len(message) > MAX_MESSAGE_LENGTH:
			raise ValueError('Message too long')
		self.send(message)

class Host(asyncore.dispatcher):
	
	log = logging.getLogger('Host')

	def __init__(self, address=('localhost', port)):
		asyncore.dispatcher.__init__(self)
		objlists.sockets.append(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind(address)
		self.listen(1)
		self.remote_clients = []

	def handle_accept(self):
		socket, addr = self.accept() # For the remote client.
		self.log.info('Accepted client at %s', addr)
		self.remote_clients.append(RemoteClient(self, socket, addr))

	def handle_read(self):
		message = self.read()
		self.log.info('Received message: %s', self.read())
		self.broadcast(message)

	def broadcast(self, message):
		self.log.info('Broadcasting message: %s', message)
		for remote_client in self.remote_clients:
			remote_client.say(message)
	
	def handle_close(self):
		self.close()

class Client(asyncore.dispatcher):
	def __init__(self, host_ip):
		host_address = (host_ip, port)
		asyncore.dispatcher.__init__(self)
		self.log = logging.getLogger('Client (%7s)' % "self")
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.log.info('Connecting to host at %s', host_address)
		self.connect(host_address)
		self.outbox = collections.deque()

		objlists.sockets.append(self)
		
		chatexample(self.say)

	def say(self, message):
		self.outbox.append(message)
		print("sending message")
		self.log.info('Enqueued message: %s', message)

	def handle_write(self):
		if not self.outbox:
			return
		message = self.outbox.popleft()
		if len(message) > MAX_MESSAGE_LENGTH:
			raise ValueError('Message too long')
		self.send(message)

	def handle_close(self):
		self.close()

	def handle_read(self):
		message = self.recv(MAX_MESSAGE_LENGTH)
		self.log.info('Received message: %s', message)
		print('Received message: ', message)

class chatexample(Window):
	def __init__(self, sendmethod):
		Window.__init__(self, "Chat Example")
		self.entrybox = entry(self, 100, method=self.send)
		self.pack(self.entrybox)
		self.sendmethod = sendmethod

	def send(self):
		print(self.entrybox.text)
		self.sendmethod(self.entrybox.text)

class hostexample(Window):
	def __init__(self, host):
		Window.__init__(self, "Host")
		self.host = host
	
	def close(self):
		Window.close(self)
		self.host.close()

def runasyncoreloop():
	asyncore.loop()

def loop():
	asyncoreloop = threading.Thread(target=runasyncoreloop)
	asyncoreloop.start()
