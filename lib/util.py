def static_init(cls):
    if getattr(cls, "static_init", None):
        cls.static_init()
    return cls


class Point:
    def __init__(self, x, y):
        if isinstance(x, int) or isinstance(x, float):
            self.x = x
        else:
            raise TypeError("X coordinate is not a number")
        if isinstance(y, int) or isinstance(y, float):
            self.y = y
        else:
            raise TypeError("Y coordinate is not a number")

    def __add__(self, other):
        new_point = Point(self.x + other.x, self.y + other.y)
        return new_point

    def __sub__(self, other):
        new_point = Point(self.x - other.x, self.y - other.y)
        return new_point

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False

    def __mul__(self, other):
        return Point(self.x * other, self.y * other)

    def __copy__(self):
        return Point(self.x, self.y)

    def __str__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'

    def is_inside_world(self, world_dimensions):
        if self.x < 0:
            return False
        elif self.x >= world_dimensions.x:
            return False
        elif self.y < 0:
            return False
        elif self.y >= world_dimensions.y:
            return False
        else:
            return True


# Searches the adjacent positions to one point
# If any position is occupied, the objects in it and its relative position to that point is returned
# Output: list of occupied positions, as well as their relative position to the initial point
def search_nearby_positions(grid, size: Point, position: Point):
    nearby_objects = []
    for i in [-1, 0, 1]:
        x = position.x + i
        if 0 <= x < size.x:
            for j in [-1, 0, 1]:
                y = position.y + j
                if 0 <= y < size.y:
                    this_near_position = grid[x][y]
                    if this_near_position is not None:
                        if isinstance(this_near_position, list):
                            for ele in this_near_position:
                                nearby_objects.append([ele, Point(i, j)])
                        else:
                            nearby_objects.append([this_near_position, Point(i, j)])
    return nearby_objects
