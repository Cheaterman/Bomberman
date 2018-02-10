from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import (
    ListProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.widget import Widget


class Bomb(Widget):
    delay = NumericProperty(3)
    level = ObjectProperty()
    tile = ObjectProperty()
    owner = ObjectProperty()
    no_collision_characters = ListProperty()

    def on_owner(self, bomb, owner):
        if not owner:
            return
        owner.bombs.append(bomb)

    def on_tile(self, bomb, tile):
        if not tile:
            return
        tile.bind(pos=self.setter('pos'), size=self.setter('size'))
        self.pos = tile.pos
        self.size = tile.size

        if self.level and not self.no_collision_characters:
            self.prepare_no_collision()

    def on_level(self, bomb, level):
        if not level:
            return
        if self.tile and not self.no_collision_characters:
            self.prepare_no_collision()
        self.timer = Clock.schedule_once(self.explode, self.delay)
        level.bombs.append(bomb)

    def explode(self, *args):
        level = self.level
        owner = self.owner
        for direction in ((-1, 0), (0, -1), (1, 0), (0, 1)):
            for distance in range(1, owner.bomb_power + 1):
                try:
                    tile = level.tile_at(
                        self.tile.coord_x + direction[0] * distance,
                        self.tile.coord_y + direction[1] * distance,
                    )
                except ValueError:
                    break
                if isinstance(tile, Factory.Rock):
                    break
                if isinstance(tile, Factory.Block):
                    map = level.map
                    index = map.children.index(tile)
                    map.remove_widget(tile)
                    map.add_widget(
                        Factory.Grass(coords=tile.coords),
                        index=index,
                    )
                    if not owner.bomb_wall_traversal:
                        break
        self.parent.remove_widget(self)
        level.bombs.remove(self)
        owner.bombs.remove(self)

    # This whole no_collision system is to prevent characters being "bumped"
    # out of the tile containing the bomb when only their center is out
    def prepare_no_collision(self):
        level = self.level
        for character in level.players:
            if level.tile_at(*level.coords(*character.center)) is self.tile:
                self.no_collision_characters.append(character)
                character.bind(pos=self.update_no_collision)

    def update_no_collision(self, character, pos):
        if not self.collide_widget(character):
            self.no_collision_characters.remove(character)
            character.unbind(pos=self.update_no_collision)

Factory.register('Bomb', module='widgets')
Builder.load_file('widgets/bomb.kv')
