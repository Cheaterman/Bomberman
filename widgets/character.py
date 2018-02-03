from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import (
    DictProperty,
    ListProperty,
    NumericProperty,
)
from kivy.uix.widget import Widget


class Character(Widget):
    keymap = DictProperty({
        273: '+up',
        274: '+down',
        275: '+right',
        276: '+left',
    })
    current_actions = ListProperty()
    movement_speed = NumericProperty(300)

    def __init__(self, **kwargs):
        super(Character, self).__init__(**kwargs)
        Window.bind(
            on_key_down=lambda w, keycode, *_: self.update_keys('down', keycode),
            on_key_up=lambda w, keycode, *_: self.update_keys('up', keycode),
        )
        Clock.schedule_interval(self.update, 1 / 60.)

    def update_keys(self, state, keycode):
        if keycode in self.keymap:
            reverse_trigger = self.keymap[keycode][0] == '-'
            action = self.keymap[keycode][1:]
            if state == 'down' or (state == 'up' and reverse_trigger):
                if action not in self.current_actions:
                    self.current_actions.append(action)
            if state == 'up' or (state == 'down' and reverse_trigger):
                if action in self.current_actions:
                    self.current_actions.remove(action)

    def update(self, dt):
        for action in self.current_actions:
            if action == 'up':
                self.y += self.movement_speed * dt
            if action == 'down':
                self.y -= self.movement_speed * dt
            if action == 'right':
                self.x += self.movement_speed * dt
            if action == 'left':
                self.x -= self.movement_speed * dt
        

Factory.register('Character', module='widgets')
Builder.load_file('widgets/character.kv')
