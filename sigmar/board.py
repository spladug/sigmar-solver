import enum
import itertools

from sigmar.hex import Hex


class Element(enum.IntEnum):
    EMPTY = 0

    AIR = 1
    FIRE = 2
    WATER = 3
    EARTH = 4
    SALT = 5

    MORS = 6
    VITAE = 7

    LEAD = 8
    TIN = 9
    IRON = 10
    COPPER = 11
    SILVER = 12
    GOLD = 13

    QUICKSILVER = 14


Element.Cardinals = [
    Element.AIR,
    Element.FIRE,
    Element.WATER,
    Element.EARTH,
]


Element.Metals = [
    Element.LEAD,
    Element.TIN,
    Element.COPPER,
    Element.IRON,
    Element.SILVER,
    Element.GOLD,
]


class Board(object):
    center = Hex.from_axial(0, 0)

    @classmethod
    def new(cls):
        tiles = {}
        radius = 5
        for q in range(-radius, radius+1):
            r1 = max(-radius, -q - radius)
            r2 = min(radius, -q + radius)

            for r in range(r1, r2+1):
                h = Hex.from_axial(q, r)
                tiles[h] = None
        return cls(tiles)

    def __init__(self, tiles):
        self.board = tiles

    def __hash__(self):
        return hash(repr(self.board))

    def set(self, h, el):
        assert el is None or isinstance(el, Element)
        assert h in self.board
        self.board[h] = el

    def get(self, h):
        return self.board.get(h)

    def take(self, h):
        value = self.get(h)
        self.set(h, None)
        return value

    def clone(self):
        return Board(self.board.copy())

    @property
    def tiles(self):
        for h in self.board.keys():
            yield h, self.board[h]

    def is_open(self, target):
        neighbors = itertools.cycle((self.get(h) for h in target.neighbors()))
        run_length = 0
        for neighbor in itertools.islice(neighbors, 6+2):
            if not neighbor:
                run_length += 1
                if run_length == 3:
                    return True
            else:
                run_length = 0
        return False
