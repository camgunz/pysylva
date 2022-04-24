# Arrays

Sylva offers three array types: `array`, `dynarray`, and `slice`.

```sylva
req sys

struct Person {
  name: str,
  age: u8,
}

array Triumverate [Person * 3]

fn print_people(people: &Triumverate) {
  for (i: people::indices) {
    let person: &people[i]

    sys.echo("{person.name} is {person.age} years old")
  }
}
```

Here, `Triumverate` is a sized `array`, therefore `::indices` is a compile-time
constant that allows us to index into it directly. This works similarly for
`dynarray` and `slice`, with the caveat that since their sizes can change at
runtime, `::indices` must also be built at runtime whenever asked for.

```sylva
req sys

struct Person {
  name: str,
  age: u8,
}

alias Triumverate: dynarray(Person)

fn print_people(people: &Triumverate) {
  for (i: people::indices) { # Built at runtime based on the current size of
    let person: &people[i]   # `people`.

    sys.echo("{person.name} is {person.age} years old")
  }
}
```

*N.B. `dynarray` allocates its data on the heap, so any program using it requires
heap allocation.*

```sylva
struct dynarray(element_type) {
  size: uint(0),
  alloc: uint(0),
  data: *element_type
}

struct slice(array_type, start) {
  start: uint,
  data: &[array_type::element_type * array_type::element_size]
}
```

```sylva
# An element count is specified here, but it doesn't do us a lot of good
# because the domain of `index` is greater than that of `Triumverate`'s
# indices.
fn print_stored_person(people: &Triumverate, index: u8) {
  let person: people[index].succeed_or_die()

  sys.echo("{person.name} is {person.age} years old")
}

# Here though, it allows us to avoid an `on_failure` check.
fn print_third_person(people: &[Person * 3]) {
  let person: people[2]

  sys.echo("{person.name} is {person.age} years old")
}

fn main() {
  let dems: Triumverate[
    Person{name: "Barack Obama", age: 61u8},
    Person{name: "Hillary Clinton", age: 75u8},
    Person{name: "Joe Biden", age: 79u8},
  ]
  let dogs: [str * 2]["Fido", "Rover"]
  let cats: [str("") * 3]

  cats[0] = "Whiskers"
  cats[2] = "Ms. Paws"

  print_people(&dems)
  print_stored_person(&dems, 1)
}
```
