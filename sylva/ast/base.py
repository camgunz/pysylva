class Node:

    def __init__(self, location):
        self.location = location


class Decl(Node):

    def __init__(self, location, name):
        Node.__init__(self, location)
        self.name = name
