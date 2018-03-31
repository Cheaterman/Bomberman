from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import (
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty,
)
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
import math


class Level(Widget):
    map_size = ListProperty([13, 13])
    map_tiles = DictProperty({
        's': 'Spawn',
        ' ': 'Grass',
        'o': 'Block',
        'x': 'Rock',
    })
    map_data = ListProperty([
        's', ' ', ' ', 'o', 'o', 'o', 'o', 'o', 'o', 'o', ' ', ' ', 's',
        ' ', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', ' ',
        ' ', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', ' ',
        'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o',
        'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o',
        'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o',
        'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o',
        'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o',
        'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o',
        'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o',
        ' ', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', ' ',
        ' ', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', ' ',
        's', ' ', ' ', 'o', 'o', 'o', 'o', 'o', 'o', 'o', ' ', ' ', 's',
    ])
    map = ObjectProperty()
    players_area = ObjectProperty()
    spawns = ListProperty()
    players = ListProperty()
    bombs = ListProperty()

    def __init__(self, **kwargs):
        super(Level, self).__init__(**kwargs)
        self.init_tiles()

    def init_tiles(self):
        for symbol, tile in self.map_tiles.items():
            if tile == 'Spawn':
                break
        else:
            raise ValueError('No spawn in map tiles description!')
        if symbol not in self.map_data:
            raise ValueError('No spawn in map tiles data!')

        self.clear_widgets()
        self.map = grid = GridLayout(
            cols=self.map_size[0],
            rows=self.map_size[1],
        )
        self.bind(
            pos=grid.setter('pos'),
            size=grid.setter('size'),
        )

        for index, tile in enumerate(self.map_data):
            if self.map_tiles[tile] == 'Spawn':
                self.spawns.append(index)
            grid.add_widget(tile_manager.tile(self.map_tiles[tile])(
                coords=(
                    index % grid.cols,
                    grid.rows - 1 - (index // grid.cols),
                )
            ))

        self.add_widget(grid)

    def spawn(self, character):
        if len(self.spawns) <= len(self.players):
            raise ValueError('No spawns remaining in map!')
        spawn = self.map.children[
            -1 - self.spawns[len(self.players)]
        ]
        character.scale = min(*spawn.size) / 100.
        character.level = self
        character.coords = [xy + .5 for xy in spawn.coords]
        self.players.append(character)
        self.players_area.add_widget(character)

    def coords(self, x, y):
        if(
            x < self.x or y < self.y or
            x > self.right or y > self.top
        ):
            raise ValueError('Invalid position (%d, %d)!' % (x, y))
        return (
            int(math.floor((x - self.x) / self.width * self.map_size[0])),
            int(math.floor((y - self.y) / self.height * self.map_size[1])),
        )

    def tile_at(self, x, y):
        if(
            x < 0 or y < 0 or
            x >= self.map_size[0] or y >= self.map_size[1]
        ):
            raise ValueError('Invalid coordinates (%d, %d)!' % (x, y))
        return self.map.children[self.map_size[0] - x - 1 + y * self.map_size[0]]

    def collides(self, tile, character):
        return (
            isinstance(tile, (Factory.Block, Factory.Rock)) or
            any([
                (
                    bomb.tile is tile and
                    character not in bomb.no_collision_characters
                ) for bomb in self.bombs
            ])
        )


class Tile(Widget):
    coord_x = NumericProperty()
    coord_y = NumericProperty()
    coords = ReferenceListProperty(coord_x, coord_y)

    def __new__(cls, **kwargs):
        tile_manager.register(cls)
        return super(Tile, cls).__new__(cls, **kwargs)


class TileManager(object):
    def __init__(self):
        self.tiles = {}

    def register(self, tile):
        self.tiles[tile.__name__] = tile

    def tile(self, tile_name):
        if tile_name not in self.tiles:
            # Try lazy-loading tiles from the Factory
            try:
                getattr(Factory, tile_name)()
            except:
                raise ValueError('No tile with name %s' % tile_name)
        return self.tiles[tile_name]


tile_manager = TileManager()

Factory.register('Level', module='widgets')
Factory.register('Tile', module='widgets')
Builder.load_file('widgets/level.kv')
