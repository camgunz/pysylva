# Flow Control

Sylva provides typical flow control and looping constructs.

## Conditionals and looping

Some old friends here:

```sylva
req random

fn get_random_name(): str {
  let index: random.random(int)(0, 3)

  switch (index) {
    case (0) { return "Alice" }
    case (1) { return "Bernadette" }
    case (2) { return "Charlie" }
    case (3) { return "Diana" }
    default  { return "" }
  }

  return ""
}

fn main() {
  loop {
    let loop_name: get_random_name()

    if (loop_name == "Alice") {
      break
    }

    if (loop_name == "Bernadette") {
      continue
    }

    if (loop_name == "Charlie") {
      sys.echo("Whoa! Hey there {loop_name}")
    }
    else {
      sys.echo("Got a name: {loop_name}")
    }
  }

  let while_name: get_random_name()

  while (while_name != "Alice") {
    sys.echo("Got a name: {while_name}")
    while_name = get_random_name()
  }

  for (i: 0..14) {
    sys.echo("Got a name: {name}")
  }
}
```

## Pattern matching

A very basic version of pattern matching on [variants](variants.html) exists in
Sylva:

```sylva
req sys
req math

variant Shape {
  Circle: {
    radius: f64,
  },

  Square: {
    side_length: f64,
  },

  Rectangle: {
    width: f64,
    height: f64,
  },
}

fn get_shape_area(shape: &Shape): f64 {
  match (shape) {
    case (c: Circle) {
      return math.PI * (c.radius ** 2)
    }
    case (s: Square) {
      return s.side_length ** 2
    }
    case (r: Rectangle) {
      return r.width * r.height
    }
  }
}

fn main() {
  let circle = Shape.Circle{radius: 14}
  let rectangle = Shape.Rectangle{width: 8, height: 9}

  sys.echo(
    "Area of a circle of radius {circle.radius}: {get_shape_area(circle)}"
  )

  sys.echo(
    "Area of a rectangle of width {rectangle.width} and height "
    "{rectangle.height}: {get_shape_area(rectangle)}"
  )
}
```
