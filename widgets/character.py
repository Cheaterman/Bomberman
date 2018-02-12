from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.widget import Widget
from widgets import Bomb
import math


class Character(Widget):
    keymap = DictProperty({
        273: '+up',
        274: '+down',
        275: '+right',
        276: '+left',
        32: '+bomb',
    })
    current_actions = ListProperty()
    radius = NumericProperty(30)
    movement_speed = NumericProperty(300)
    level = ObjectProperty()
    bombs = ListProperty()
    bomb_power = NumericProperty(2)
    bomb_wall_traversal = BooleanProperty(False)

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
        for action in self.current_actions[:]:
            if action == 'up':
                self.y += self.movement_speed * dt
            if action == 'down':
                self.y -= self.movement_speed * dt
            if action == 'right':
                self.x += self.movement_speed * dt
            if action == 'left':
                self.x -= self.movement_speed * dt
            if action == 'bomb':
                self.current_actions.remove('bomb')
                level = self.level
                tile = level.tile_at(*level.coords(*self.center))
                if any([bomb.tile is tile for bomb in level.bombs]):
                    continue
                bomb = Bomb(
                    level=level,
                    tile=tile,
                    owner=self,
                )
                level.add_widget(bomb)
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

        # Evaluate the 8 neighboring tiles
        for nid, offset in enumerate((
            (-1, +1), (+0, +1), (+1, +1),
            (-1, +0),           (+1, +0),
            (-1, -1), (+0, -1), (+1, -1),
        )):
            neighbor = [coords[i] + offset[i] for i in range(2)]
            if(
                neighbor[0] < 0 or neighbor[1] < 0 or
                neighbor[0] >= level.map_size[0] or
                neighbor[1] >= level.map_size[1]
            ):
                # Outside of map
                continue
            tile = level.tile_at(*neighbor)
            if level.collides(tile, self):
                # Check tile edges
                for edge_pos, edge_direction, target in (
                    (tile.top, 'horizontal', 'y'),
                    (tile.x, 'vertical', 'right'),
                    (tile.y, 'horizontal', 'top'),
                    (tile.right, 'vertical', 'x'),
                ):
                    min_pos, max_pos, target_ortho, min_ortho, max_ortho = (
                        self.x, self.right, self.center_y, tile.y, tile.top
                    ) if edge_direction == 'vertical' else (
                        self.y, self.top, self.center_x, tile.x, tile.right
                    )
                    if(
                        min_pos < edge_pos < max_pos and
                        min_ortho <= target_ortho <= max_ortho
                    ):
                        setattr(self, target, edge_pos)
                # Check tile corners
                for corner, neighbors_offset in (
                    ((tile.x, tile.y), ((-1, 0), (0, -1))),
                    ((tile.x, tile.top), ((-1, 0), (0, 1))),
                    ((tile.right, tile.y), ((1, 0), (0, -1))),
                    ((tile.right, tile.top), ((1, 0), (0, 1))),
                ):
                    radius = math.hypot(*[
                        self.center[i] - corner[i] for i in range(2)
                    ])
                    if radius < self.radius and all([
                        self.pos[i] < corner[i] < self.pos[i] + self.size[i]
                        for i in range(2)
                    ]) and not any([
                        level.collides(
                            level.tile_at(*[
                                neighbor[i] + offset[i]
                                for i in range(2)
                            ]),
                            self
                        ) for offset in neighbors_offset
                    ]):
                        ratio = self.radius / radius
                        self.center = [
                            corner[i] + sum(
                                [offset[i] for offset in neighbors_offset]
                            ) * abs(self.center[i] - corner[i]) * ratio
                            for i in range(2)
                        ]


Factory.register('Character', module='widgets')
Builder.load_file('widgets/character.kv')
