# This is heavily based off of the code available at http://www.redblobgames.com/grids/hexagons/

import collections
import math


Point = collections.namedtuple("Point", ["x", "y"])


class Hex(collections.namedtuple("Hex", ["q", "r", "s"])):
    @classmethod
    def from_axial(cls, q, r):
        return cls(q, r, -q-r)

    def add(self, other):
        return Hex(self.q + other.q, self.r + other.r, self.s + other.s)

    def scale(self, k):
        return Hex(self.q * k, self.r * k, self.s * k)

    __add__ = add
    __mul__ = scale

    def rotate_left(self):
        return Hex(-self.s, -self.q, -self.r)

    def rotate_right(self):
        return Hex(-self.r, -self.s, -self.q)

    def neighbor(self, direction):
        return self + _HEX_DIRECTIONS[direction]

    def neighbors(self):
        for direction in _HEX_DIRECTIONS:
            yield self + direction


_HEX_DIRECTIONS = [Hex(1, 0, -1), Hex(1, -1, 0), Hex(0, -1, 1), Hex(-1, 0, 1), Hex(-1, 1, 0), Hex(0, 1, -1)]


class Orientation(collections.namedtuple("Orientation", ["f0", "f1", "f2", "f3", "b0", "b1", "b2", "b3", "start_angle"])):
    pass


Orientation.POINTY = Orientation(math.sqrt(3.0), math.sqrt(3.0) / 2.0, 0.0, 3.0 / 2.0, math.sqrt(3.0) / 3.0, -1.0 / 3.0, 0.0, 2.0 / 3.0, 0.5)


class Layout(collections.namedtuple("Layout", ["orientation", "size", "origin"])):
    def hex_to_pixel(self, h):
        M = self.orientation
        size = self.size
        origin = self.origin
        x = (M.f0 * h.q + M.f1 * h.r) * size.x
        y = (M.f2 * h.q + M.f3 * h.r) * size.y
        return Point(x + origin.x, y + origin.y)

    def pixel_to_hex(self, p):
        M = self.orientation
        size = self.size
        origin = self.origin
        pt = Point((p.x - origin.x) / size.x, (p.y - origin.y) / size.y)
        q = M.b0 * pt.x + M.b1 * pt.y
        r = M.b2 * pt.x + M.b3 * pt.y
        return Hex(q, r, -q - r)

    def hex_corner_offset(self, corner):
        M = self.orientation
        size = self.size
        angle = 2.0 * math.pi * (M.start_angle - corner) / 6
        return Point(size.x * math.cos(angle), size.y * math.sin(angle))

    def polygon_corners(self, h):
        corners = []
        center = self.hex_to_pixel(h)
        for i in range(0, 6):
            offset = self.hex_corner_offset(i)
            corners.append(Point(center.x + offset.x, center.y + offset.y))
        return corners
