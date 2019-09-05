# Interfaces

Often when writing a function you only require certain attributes or behavior,
and if some piece of data satisfies those requirements then you're happy to
ignore its other particulars.  In Sylva, interfaces provide that functionality.

```sylva
requirement sys
requirement math
requirement random

struct Circle {
  radius: num
}

struct Square {
  side_length: num
}

struct Rectangle {
  length: num
  height: num
}

interface Shape {
  fn make_random(): *Shape
  fn get_area(self: &Shape): num
  fn increase_area(self: &Shape!)
  fn print(self: &Shape)
}

implementation(Circle): Shape {
  fn make_random(): *Circle {
    return(*Shape.Circle(radius: random.random_num()))
  }

  fn get_area(self: &Circle): num {
    return(math.PI * (self.radius ** 2))
  }

  fn increase_area(self: &Circle!) {
    self.radius += random.random_num()
  }

  fn print(self: &Circle) {
    sys.echo("Circle({self.get_area()})")
  }
}

implementation(Square): Shape {
  fn make_random(): *Square {
    return(*Shape.Square(side_length: random.random_num()))
  }

  fn get_area(self: &Square): num {
    return(self.side_length ** 2)
  }

  fn increase_area(self: &Square!) {
    self.side_length += random.random_num()
  }

  fn print(self: &Square) {
    sys.echo("Square({self.get_area()})")
  }
}

implementation(Rectangle): Shape {
  fn make_random(): *Rectangle {
    return(*Shape.Rectangle(
      length: random.random_num(),
      height: random.random_num()
    ))
  }

  fn get_area(self: &Rectangle): num {
    return(self.length * self.height)
  }

  fn increase_area(self: &Rectangle!) {
    self.length += random.random_num()
    self.height += random.random_num()
  }

  fn print(self: &Rectangle) {
    sys.echo("Rectangle({self.get_area()})")
  }
}

fn make_random_shape(): *Shape {
  if(random.odds(1, 1000)) {
    error("Sometimes I just don't feel like making a shape")
  }

  switch(random.choices(3)) {
    case(1) {
      return(Circle.make_random())
    }
    case(2) {
      return(Square.make_random())
    }
    case(3) {
      return(Rectangle.make_random())
    }
  }
}

fn main() {
  for(_: 10000000) {
    with(shape: make_random_shape()) {
      increase_shape_area(&shape!)
      print_shape(&shape)
    }
    else(err) {
      echoerr("Error making a random shape: {err}")
    }
  }
}
```

Interfaces can be useful in some case--Sylva's `Error` is a good example.
However, much of the time [variants](variants.md) are the better choice.
