#!/usr/bin/env python3

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from network import Client
from widgets import Character
import capnp
import bomberman_capnp


class Bomberman(App):
    level = ObjectProperty()
    # XXX Don't commit me!        
    username = StringProperty('Cheaterman')

    def build(self):
        self.level = self.root.ids.level

    def start_game(self):
        self.root.current = 'game'
        character = Character()
        self.level.spawn(character)

    def connect(self, address):
        self.capnp_client = client = capnp.TwoPartyClient(str(address))
        self.capnp_login = client.bootstrap().cast_as(bomberman_capnp.Login)
        self.login(self.username)

    def login(self, name):
        self.client = client = Client()
        response = self.capnp_login.connect(
            client.capnp_client,
            self.username
        ).wait()
        self.server, self.login_handle = response.server, response.handle
        self.character = self.server.join().wait().character
        Clock.schedule_interval(self.update_network, 0)

        client.bind(on_update=self.on_update)
        self.start_game()

    def update_network(self, dt):
        capnp.getTimer().after_delay(.004 * 10 ** 9).wait()

    def on_update(self, client, command):
        print(args)


if __name__ == '__main__':
    app = Bomberman()
    app.run()
