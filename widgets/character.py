from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import (
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
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
    radius = NumericProperty(30)
    movement_speed = NumericProperty(300)
    level = ObjectProperty()

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
        self.update_collisions()

    def update_collisions(self):
        level = self.level
        try:
            coords = level.coords(*self.center)
        except ValueError:
            return

        # Check map edges
        self.x = max(self.x, level.x)
        self.y = max(self.y, level.y)
        self.right = min(self.right, level.right)
        self.top = min(self.top, level.top)

        for nid, neighbor in enumerate((
            (coords[0] - 1, coords[1] - 1),
            (coords[0] + 0, coords[1] - 1),
            (coords[0] + 1, coords[1] - 1),
            (coords[0] - 1, coords[1] + 0),
            (coords[0] + 1, coords[1] + 0),
            (coords[0] - 1, coords[1] + 1),
            (coords[0] + 0, coords[1] + 1),
            (coords[0] + 1, coords[1] + 1),
        )):
            if(
                neighbor[0] < 0 or neighbor[1] < 0 or
                neighbor[0] >= level.map_size[0] or
                neighbor[1] >= level.map_size[1]
            ):
                # Outside of map
                continue
            tile = level.tile_at(*neighbor)
            if isinstance(tile, (Factory.Block, Factory.Rock)):
                # Check tile edges
                if(
                    self.y < tile.top and self.top > tile.top and
                    self.center_x >= tile.x and self.center_x <= tile.right
                ):
                    self.y = tile.top
                if(
                    self.right > tile.x and self.x < tile.x and
                    self.center_y >= tile.y and self.center_y <= tile.top
                ):
                    self.right = tile.x
                if(
                    self.top > tile.y and self.y < tile.y and
                    self.center_x >= tile.x and self.center_x <= tile.right
                ):
                    self.top = tile.y
                if(
                    self.x < tile.right and self.right > tile.right and
                    self.center_y >= tile.y and self.center_y <= tile.top
                ):
                    self.x = tile.right
                # Check tile corners
                # XXX: Bug when hitting the edges of two tiles simultaneously
                # FIXME: Also, does it really need to be so complicated?
                hypotenuse = (
                    (self.center_x - tile.x) ** 2 +
                    (self.center_y - tile.top) ** 2
                ) ** .5
                if(
                    self.right > tile.x and self.x < tile.x and
                    self.y < tile.top and self.top > tile.top and
                    hypotenuse < self.radius
                ):
                    ratio = self.radius / hypotenuse
                    self.center_x = tile.x - abs(self.center_x - tile.x) * ratio
                    self.center_y = tile.top + abs(self.center_y - tile.top) * ratio
                hypotenuse = (
                    (self.center_x - tile.x) ** 2 +
                    (self.center_y - tile.y) ** 2
                ) ** .5
                if(
                    self.right > tile.x and self.x < tile.x and
                    self.top > tile.y and self.y < tile.y and
                    hypotenuse < self.radius
                ):
                    ratio = self.radius / hypotenuse
                    self.center_x = tile.x - abs(self.center_x - tile.x) * ratio
                    self.center_y = tile.y - abs(self.center_y - tile.y) * ratio
                hypotenuse = (
                    (self.center_x - tile.right) ** 2 +
                    (self.center_y - tile.y) ** 2
                ) ** .5
                if(
                    self.x < tile.right and self.right > tile.right and
                    self.top > tile.y and self.y < tile.y and
                    hypotenuse < self.radius
                ):
                    ratio = self.radius / hypotenuse
                    self.center_x = tile.right + abs(self.center_x - tile.right) * ratio
                    self.center_y = tile.y - abs(self.center_y - tile.y) * ratio
                hypotenuse = (
                    (self.center_x - tile.right) ** 2 +
                    (self.center_y - tile.top) ** 2
                ) ** .5
                if(
                    self.x < tile.right and self.right > tile.right and
                    self.y < tile.top and self.top > tile.top and
                    hypotenuse < self.radius
                ):
                    ratio = self.radius / hypotenuse
                    self.center_x = tile.right + abs(self.center_x - tile.right) * ratio
                    self.center_y = tile.top + abs(self.center_y - tile.top) * ratio


Factory.register('Character', module='widgets')
Builder.load_file('widgets/character.kv')
