# Enums

Enums define a set of constants as a type.

```sylva
enum EvenNumber {
  Two: 2,
  Four: 4,
  Six: 6,
  Eight: 8,
}
```

Enums can also contain arrays and structs, though these will be immutable:

```sylva
struct Person {
  name: str,
  age: dec,
}

enum Justice {
  John: Person{name: "John Roberts", age: 65},
  Clarence: Person{name: "Clarence Thomas", age: 72},
  Ruth: Person{name: "Ruth Bader Ginsburg", age: 87},
  Stephen: Person{name: "Stephen Breyer", age: 82},
  Samuel: Person{name: "Samuel Alito", age: 70},
  Sonia: Person{name: "Sonia Sotomayor", age: 66},
  Elena: Person{name: "Elena Kagen", age: 60},
  Neil: Person{name: "Neil Gorsuch", age: 53},
  Brett: Person{name: "Brett Kavanaugh", age: 55},
}
```

Enum members can be referenced like struct variants:

```sylva
req sys

enum Day {
  Sunday: "Sunday",
  Monday: "Monday",
  Tuesday: "Tuesday",
  Wednesday: "Wednesday",
  Thursday: "Thursday",
  Friday: "Friday",
  Saturday: "Saturday",
}

fn print_today(today: Day) {
  sys.echo("Today is {today}")
}

fn main() {
  print_today(Day.Sunday)
}
```

## Special methods and fields

Enums have some special methods and fields that are quite convenient.

### `first` and `last`

Enums have `first` and `last` fields that return the first and last member
respectively:

```sylva
req sys

enum Day {
  Sunday: "Sunday",
  Monday: "Monday",
  Tuesday: "Tuesday",
  Wednesday: "Wednesday",
  Thursday: "Thursday",
  Friday: "Friday",
  Saturday: "Saturday",
}

fn main() {
  sys.echo("First day of the week is {Day::first}")
  sys.echo("Last day of the week is {Day::last}")
}
```

### `count`

`count` contains the number of values in an enum.

```sylva
req sys

enum Day {
  Sunday: "Sunday",
  Monday: "Monday",
  Tuesday: "Tuesday",
  Wednesday: "Wednesday",
  Thursday: "Thursday",
  Friday: "Friday",
  Saturday: "Saturday",
}

fn main() {
  sys.echo("There are {Day::count} days in a week")
}
```

### Iterating

Using `::indices` and `::get`, it's possible to iterate over an enum's values:

```sylva
req sys

enum Day {
  Sunday: "Sunday",
  Monday: "Monday",
  Tuesday: "Tuesday",
  Wednesday: "Wednesday",
  Thursday: "Thursday",
  Friday: "Friday",
  Saturday: "Saturday",
}

fn main() {
  for (i: Day::indices) {
    sys.echo("Day: {Day::get(i)}")
  }
}
```

## Enums vs. ranges and variants

- Range: sequence of numbers
- Enum: set of named constant values
- Variant: set of named types

It may help to distinguish between enums and ranges by keeping in mind that
arithmetic on enums is impossible. Enums are required to be neither continuous
nor numeric. To return to the above example, the expression `Day("Sunday") -
Day("Monday")` is nonsensical; enum values cannot be constructed, only
referenced.
