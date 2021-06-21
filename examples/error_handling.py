import abc
import sys
import math
import random


class Shape(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def Random(cls):
        ...

    @property
    @abc.abstractmethod
    def area(self):
        ...

    @abc.abstractmethod
    def increase_area(self):
        ...

    def __str__(self):
        return f'{type(self).__name__}({self.area})'


class Circle(Shape):

    def __init__(self, radius):
        self.radius = radius

    @classmethod
    def Random(cls):
        return cls(random.random())

    @property
    def area(self):
        return math.pi * (self.radius ** 2)

    def increase_area(self):
        self.radius += random.random()


class Square(Shape):

    def __init__(self, side_length):
        self.side_length = side_length

    @classmethod
    def Random(cls):
        return cls(random.random())

    @property
    def area(self):
        return self.side_length ** 2

    def increase_area(self):
        self.side_length += random.random()


class Rectangle(Shape):

    def __init__(self, length, height):
        self.length = length
        self.height = height

    @classmethod
    def Random(cls):
        return cls(random.random(), random.random())

    @property
    def area(self):
        return self.length * self.height

    def increase_area(self):
        self.length += random.random()
        self.height += random.random()


def make_random_shape():
    if random.randrange(1, 1000) == 1:
        raise Exception("Sometimes I just don't feel like making a shape")

    return random.choice([Circle, Square, Rectangle]).Random()


def main():
    for _ in range(1000000):
        try:
            shape = make_random_shape()
        except Exception as exc:  # pylint: disable=broad-except
            print(f'Error making a random shape: {exc}', file=sys.stderr)
            continue
        shape.increase_area()
        print(shape)
