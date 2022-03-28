# Flow Control

Sylva provides typical flow control and looping constructs.

## Conditionals and looping

Some old friends here:

```sylva
req random

fn get_random_name(): str {
  var index: random.random(int)(0, 3)

  switch (index) {
    case (0) { return "Alice" }
    case (1) { return "Bernadette" }
    case (2) { return "Cynthia" }
    case (3) { return "Diana" }
    default  { return "" }
  }

  return ""
}

fn main() {
  loop {
    var loop_name: get_random_name()

    if (loop_name == "Alice") {
      break
    }

    sys.echo("Got a name: {loop_name}")
  }

  var while_name: get_random_name()

  while (while_name != "Alice") {
    sys.echo("Got a name: {while_name}")
    while_name = get_random_name()
  }

  for (name: get_random_name(); name != "Alice"; name = get_random_name()) {
    sys.echo("Got a name: {name}")
  }

  loop {
    var loop_name: get_random_name()

    if (loop_name == "Alice") {
      continue
    }

    sys.echo("Got a name: {loop_name}")
  }
}

```

In practice, try to avoid explicit looping constructs. There are usually
other methods that are semantically clearer, such as using an `.each` or `.map`
method.

## Pattern matching

A very basic version of pattern matching on [variants](variants.html) exists in
Sylva:

```sylva
req sys
req math

variant Shape {
  Circle: {
    radius: dec,
  },

  Square: {
    side_length: dec,
  },

  Rectangle: {
    width: dec,
    height: dec,
  },
}

fn get_shape_area(shape: &Shape): dec {
  match (shape) {
    case (c: Shape.Circle) {
      return math.PI * (c.radius ** 2)
    }
    case (s: Shape.Square) {
      return s.side_length ** 2
    }
    case (r: Shape.Rectangle) {
      return r.width * r.height
    }
  }
}

fn main() {
  var circle = Shape.Circle{radius: 14}
  var rectangle = Shape.Rectangle{width: 8, height: 9}

  sys.echo(
    "Area of a circle of radius {circle.radius}: {get_shape_area(circle)}"
  )

  sys.echo(
    "Area of a rectangle of width {rectangle.width} and height "
    "{rectangle.height}: {get_shape_area(rectangle)}"
  )
}
```
