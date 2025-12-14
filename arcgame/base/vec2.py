"""2D vector math matching DDNet's vector math implementation"""
import math


class Vec2:
    """2D vector matching DDNet's vector math"""
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other):
        """Add two vectors"""
        return Vec2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        """Subtract two vectors"""
        return Vec2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        """Multiply vector by scalar"""
        return Vec2(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar):
        """Multiply vector by scalar (reverse)"""
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        """Divide vector by scalar"""
        return Vec2(self.x / scalar, self.y / scalar)
    
    def __neg__(self):
        """Negate vector"""
        return Vec2(-self.x, -self.y)
    
    def __eq__(self, other):
        """Check equality with small tolerance"""
        return abs(self.x - other.x) < 1e-6 and abs(self.y - other.y) < 1e-6
    
    def length(self):
        """Get the length of the vector"""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def length_sq(self):
        """Get the squared length of the vector (faster than length())"""
        return self.x * self.x + self.y * self.y
    
    def distance(self, other):
        """Get the distance to another vector"""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)
    
    def distance_sq(self, other):
        """Get the squared distance to another vector (faster than distance())"""
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy
    
    def normalize(self):
        """Normalize the vector to unit length"""
        length = self.length()
        if length == 0:
            return Vec2(0, 0)
        return Vec2(self.x / length, self.y / length)
    
    def dot(self, other):
        """Calculate the dot product with another vector"""
        return self.x * other.x + self.y * other.y
    
    def cross(self, other):
        """Calculate the cross product with another vector (in 2D, returns scalar)"""
        return self.x * other.y - self.y * other.x
    
    def rotate(self, angle):
        """Rotate the vector by an angle (in radians)"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        new_x = self.x * cos_a - self.y * sin_a
        new_y = self.x * sin_a + self.y * cos_a
        return Vec2(new_x, new_y)
    
    def angle(self):
        """Get the angle of the vector in radians"""
        return math.atan2(self.y, self.x)
    
    def clamp_length(self, max_length):
        """Clamp the vector to a maximum length"""
        length = self.length()
        if length > max_length and length != 0:
            factor = max_length / length
            return Vec2(self.x * factor, self.y * factor)
        return Vec2(self.x, self.y)
    
    def copy(self):
        """Create a copy of the vector"""
        return Vec2(self.x, self.y)
    
    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"
    
    def __str__(self):
        return f"({self.x:.3f}, {self.y:.3f})"


def closest_point_on_line(start, end, point):
    """Find the closest point on a line segment to a given point"""
    line_vec = end - start
    point_vec = point - start
    
    line_len_sq = line_vec.length_sq()
    if line_len_sq < 1e-8:  # Line is basically a point
        return start.copy()
    
    t = max(0.0, min(1.0, point_vec.dot(line_vec) / line_len_sq))
    return start + line_vec * t


def closest_point_on_rectangle(rect_top_left, rect_size, point):
    """Find the closest point on a rectangle to a given point"""
    closest_x = max(rect_top_left.x, min(point.x, rect_top_left.x + rect_size.x))
    closest_y = max(rect_top_left.y, min(point.y, rect_top_left.y + rect_size.y))
    return Vec2(closest_x, closest_y)


def lerp(a, b, t):
    """Linear interpolation between two vectors"""
    return a + (b - a) * max(0.0, min(1.0, t))


if __name__ == "__main__":
    # Test the vector operations
    v1 = Vec2(3, 4)
    v2 = Vec2(1, 2)
    
    print(f"v1: {v1}")
    print(f"v2: {v2}")
    print(f"v1 + v2: {v1 + v2}")
    print(f"v1 - v2: {v1 - v2}")
    print(f"v1 * 3: {v1 * 3}")
    print(f"Length of v1: {v1.length()}")
    print(f"Normalized v1: {v1.normalize()}")
    print(f"Dot product v1·v2: {v1.dot(v2)}")
    print(f"Distance v1 to v2: {v1.distance(v2)}")