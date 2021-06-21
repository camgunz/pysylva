# Enums

Enums define a set of constants as a type.

```sylva
enum Evens {
  Two: 2
  Four: 4
  Six: 6
  Eight: 8
}
```

Enums can also contain arrays and structs, though these will be immutable:

```sylva
struct Person {
  name: str
  age: dec
}

enum Justices {
  John: Person{"John Roberts", 65}
  Clarence: Person{"Clarence Thomas", 72}
  Ruth: Person{"Ruth Bader Ginsburg", 87}
  Stephen: Person{"Stephen Breyer", 82}
  Samuel: Person{"Samuel Alito", 70}
  Sonia: Person{"Sonia Sotomayor", 66}
  Elena: Person{"Elena Kagen", 60}
  Neil: Person{"Neil Gorsuch", 53}
  Brett: Person{"Brett Kavanaugh", 55}
}
```

Enum members can be referenced like struct variants:

```sylva
requirement sys

enum Days {
  Sunday: "Sunday"
  Monday: "Monday"
  Tuesday: "Tuesday"
  Wednesday: "Wednesday"
  Thursday: "Thursday"
  Friday: "Friday"
  Saturday: "Saturday"
}

fn print_today(today: Days) {
  sys.echo("Today is {today}")
}

fn main() {
  print_today(Days.Sunday)
}
```

## Special methods and fields

Enums have some special methods and fields that are quite convenient.

### `first` and `last`

Enums have `first` and `last` fields that return the first and last member
respectively:

```sylva
requirement sys

enum Days {
  Sunday: "Sunday"
  Monday: "Monday"
  Tuesday: "Tuesday"
  Wednesday: "Wednesday"
  Thursday: "Thursday"
  Friday: "Friday"
  Saturday: "Saturday"
}

fn main() {
  sys.echo("First day of the week is {Days::first}")
  sys.echo("Last day of the week is {Days::last}")
}
```

### `each`

`each` allows the programmer to iterate over an enum's values:

```sylva
requirement sys

enum Days {
  Sunday: "Sunday"
  Monday: "Monday"
  Tuesday: "Tuesday"
  Wednesday: "Wednesday"
  Thursday: "Thursday"
  Friday: "Friday"
  Saturday: "Saturday"
}

fn main() {
  Days::each(fn (day: Days) {
    sys.echo("Days: {day}")
  })
}
```

## Enums vs. ranges and variants

- Variants: collections of types
- Enums: collections of explicit values
- Ranges: collections of numbers
