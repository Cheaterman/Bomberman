from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import (
    DictProperty,
    ListProperty,
    ObjectProperty,
)
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget


class Level(Widget):
    map_size = ListProperty([13, 13])
    map_tiles = DictProperty({
        ' ': 'Grass',
        'o': 'Block',
        'x': 'Rock',
    })
    map_data = ListProperty([
        ' ', ' ', ' ', 'o', 'o', 'o', 'o', 'o', 'o', 'o', ' ', ' ', ' ',
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
        ' ', ' ', ' ', 'o', 'o', 'o', 'o', 'o', 'o', 'o', ' ', ' ', ' ',
    ])
    map = ObjectProperty()

    def __init__(self, **kwargs):
        super(Level, self).__init__(**kwargs)
        self.init_tiles()

    def init_tiles(self):
        self.clear_widgets()
        self.map = grid = GridLayout(
            cols=self.map_size[0],
            rows=self.map_size[1],
        )
        self.bind(size=grid.setter('size'))
        for tile in self.map_data:
            grid.add_widget(tile_manager.tile(self.map_tiles[tile])())
        self.add_widget(grid)


class Tile(Widget):
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
