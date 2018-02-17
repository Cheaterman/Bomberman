from kivy.atlas import Atlas
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
    StringProperty,
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
    last_action = StringProperty('down')
    current_actions = ListProperty()
    radius = NumericProperty(30)
    atlas = ObjectProperty(Atlas('data/images/character.atlas'))
    animation_frame = NumericProperty(1)
    animation_timer = ObjectProperty(allownone=True)
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
        if self.current_actions:
            self.last_action = self.current_actions[-1]
            if not self.animation_timer:
                self.animation_timer = Clock.schedule_interval(
                    self.update_animation, .25
                )
        else:
            Clock.unschedule(self.animation_timer)
            self.animation_timer = None
            self.animation_frame = 1
        self.update_collisions()

    def update_animation(self, dt):
        animation_duration = len([
            key for key in self.atlas.textures
            if key.startswith(self.last_action)
            and key.split('_')[1].isdigit()
        ])
        if self.animation_frame < animation_duration:
            self.animation_frame += 1
        else:
            self.animation_frame = 1

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
                pos, size, center, tpos, tsize = (
                    self.pos, self.size, self.center, tile.pos, tile.size
                )
                # Check tile edges
                for edge_pos, axis, target in (
                    (tile.x, 0, 'right'),
                    (tile.y, 1, 'top'),
                    (tile.right, 0, 'x'),
                    (tile.top, 1, 'y'),
                ):
                    na = not axis
                    if(
                        pos[axis] < edge_pos < pos[axis] + size[axis] and
                        tpos[na] <= center[na] <= tpos[na] + tsize[na]
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
                        center[i] - corner[i] for i in range(2)
                    ])
                    if radius < self.radius and all([
                        pos[i] < corner[i] < pos[i] + size[i] for i in range(2)
                    ]) and not any([
                        level.collides(level.tile_at(
                            *[neighbor[i] + offset[i] for i in range(2)]
                        ), self) for offset in neighbors_offset
                    ]):
                        ratio = self.radius / radius
                        self.center = [
                            corner[i] + sum(
                                [offset[i] for offset in neighbors_offset]
                            ) * abs(center[i] - corner[i]) * ratio
                            for i in range(2)
                        ]


Factory.register('Character', module='widgets')
Builder.load_file('widgets/character.kv')
