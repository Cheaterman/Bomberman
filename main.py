from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from widgets import Character


class Bomberman(App):
    level = ObjectProperty()

    def build(self):
        self.level = self.root.ids.level
        Clock.schedule_once(lambda _: self.start_game(), 3)

    def start_game(self):
        character = Character()
        self.level.spawn(character)


if __name__ == '__main__':
    app = Bomberman()
    app.run()
