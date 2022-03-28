# Arrays

Arrays in Sylva have both an element type and count:

```sylva
req sys

struct Person {
  name: str,
  age: u8,
}

array Triumverate [Person * 3]

# Element counts can be left off of arrays
fn print_people(people: &[Person]) {
  for (&person: people) {
    sys.echo("{person.name} is {person.age} years old")
  }
}

# An element count is specified here, but it doesn't do us a lot of good
fn print_stored_person(people: &Triumverate, index: u8) {
  var person: people[index].on_failure(fn (f: Failure) {
    sys.die("Failed to get person at {index}: {f}")
  }).value

  sys.echo("{person.name} is {person.age} years old")
}

# Here though, it allows us to avoid an `on_failure` check.
fn print_third_person(people: &[Person * 3]) {
  var person: people[2]

  sys.echo("{person.name} is {person.age} years old")
}

fn main() {
  var dems: [Person * 3][
    Person{name: "Barack Obama", age: 61u8},
    Person{name: "Hillary Clinton", age: 75u8},
    Person{name: "Joe Biden", age: 79u8},
  ]
  var dogs: [str * 2]["Fido", "Rover"]
  var cats: [str("") * 3]

  cats[0] = "Whiskers"
  cats[2] = "Ms. Paws"

  print_people(&dems)
  print_stored_person(&dems, 1)
}
```
