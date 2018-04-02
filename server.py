#!/usr/bin/env python3

import capnp
import bomberman_capnp
import time


class Login(bomberman_capnp.Login.Server):
    def __init__(self):
        self.server = server

    def connect(self, client, name, _context):
        if not self.server.validate_login(self.address, name):
            raise ValueError('Invalid username or client already connected.')

        print('New user connected: %s (%s:%d)' % ((name,) + self.address))
        return self.server.connect(client, name, self)

    def on_connect(self, client):
        self.address = client
        print('New connection from: %s:%d' % client)

    def on_disconnect(self):
        print('User %s (%s:%d) disconnected.' % (
            (self.server.clients[self.address].name,) + self.address
        ))
        self.server.disconnect(self.address)


class LoginHandle(bomberman_capnp.Login.LoginHandle.Server):
    def __init__(self, login):
        self.login = login

    def __del__(self):
        self.login.on_disconnect()


class GameServer(bomberman_capnp.Server.Server):
    def __init__(self, client, server):
        self.client = client
        self.server = server

    def join(self, _context):
        return Character(self)

    def send(self, command, _context):
        pass


class Character(bomberman_capnp.Character.Server):
    def __init__(self, server):
        self.server = server

    def do(self, action, _context):
        self.server.client.send(bomberman_capnp.Command.new_message(
            name='update',
            args=[action],
        ))


class Client(object):
    def __init__(self, address, client_handle, name):
        self.address = address
        self._client_handle = client_handle
        self.name = name

    def send(self, command):
        return self._client_handle.send(command)


class Server(object):
    def __init__(self, **kwargs):
        self.address = kwargs.get('address', '0.0.0.0')
        self.port = kwargs.get('port', 25000)
        self.sv_fps = kwargs.get('sv_fps', 60)
        self.clients = {}

    def validate_login(self, address, name):
        if address not in self.clients and self.validate_nickname(name):
            return True

    def validate_nickname(self, name):
        if(
            name and
            name not in [client.name for client in self.clients.values()]
        ):
            return True

    def connect(self, client_handle, name, login):
        client = Client(login.address, client_handle, name)
        self.clients[login.address] = client
        return GameServer(client, self), LoginHandle(login)

    def disconnect(self, address):
        del self.clients[address]

    def update(self):
        pass

    def run(self):
        listen_address = '%s:%d' % (self.address, self.port)
        self.server = capnp.TwoPartyServer(
            listen_address,
            bootstrap=Login,
        )
        print('Listening on %s' % listen_address)
        tick_duration = 1. / self.sv_fps

        while True:
            self.update()
            start_time = time.time()
            capnp.getTimer().after_delay(tick_duration).wait()
            time.sleep(tick_duration - (time.time() - start_time))


if __name__ == '__main__':
    server = Server()
    server.run()
