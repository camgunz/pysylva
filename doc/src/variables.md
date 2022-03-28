# Variables

In Sylva, variables are defined using `var`:

```sylva
fn main() {
  var name: "Barack"
}
```

Sylva's expressions are typed. `"Barack"` is a string literal expression thus
the type of `name` is `str`.

Variables bound to constants can be reassigned; other variables cannot:

```sylva
struct Person {
  name: str,
  age: dec,
}

fn main() {
  var age: 57
  var person: Person{name: "Barack", age: age}

  person = Person(name: "Michelle", age: 56) # Error
}
```

This however would be fine:

```sylva
struct Person {
  name: str,
  age: dec,
}

enum People {
  Barack: Person{name: "Barack", age: 57},
  Michelle: Person{name: "Michelle", age: 56},
}

fn main() {
  var age: 57
  var person: Barack

  age += 1
}
```

By default, memory is allocated on the stack:

```sylva
struct Person {
  name: str,
  age: dec,
}

fn main() {
  var person: Person{name: "Barack", age: 57} # On the stack
}
```

Passing constants this way is no problem, but passing something else is not
allowed:

```sylva
req sys

struct Person {
  name: str,
  age: dec,
}

fn print_age(age: dec) {
  sys.echo("Age: {age}")
}

fn say_hey(person: Person) { # Will not compile
  sys.echo("Hey {person.name}")
}

fn main() {
  var age: 57
  var person: Person{name: "Barack", age: 57}
  print_age(age)
  say_hey(person)
}
```

Sylva would have to implicitly copy the data in order to implement this, and
while we could easily copy a `Person`, more complicated `struct`s that contain
owned pointers or references would require deep copying in order to preserve
the [ownership/reference semantics](memory.html).

## Mutable references

Here, `have_birthday` requires a mutable reference to `person` in order to
mutate its `age` field. But `main` passes an immutable reference instead, which
is an error:

```sylva
struct Person {
  name: str,
  age: dec,
}

fn have_birthday(person: &Person!) {
  person.age++
}

fn main() {
  var person: Person{name: "Barack", age: 57}

  have_birthday(&person) # Error!
}
```

In order to do that, we need to pass a mutable reference to `have_birthday`:

```sylva
fn have_birthday(person: &Person!) {
  person.age++
}

fn main() {
  var person: Person{name: "Barack", age: 57}

  have_birthday(&person!)
}
```

In order to make a mutable reference, there can be no other references:

```sylva
req sys

struct Person {
  name: str,
  age: dec,
}

fn main() {
  var person: Person{name: "Barack", age: 57}
  var immutable_person_ref: &person
  var mutable_person_ref: &person! # Error!
}
```

## Moving

Moving also requires there are no other references.

```sylva
req sys

struct Person {
  name: str,
  age: dec,
}

fn main() {
  var person: *Person{name: "Barack", age: 57}
  var person_ref: &person
  var moved_person: *person # Error!
}
```

## Hierarchy

There's a short hierarchy here:

- Owned pointer / Stack allocated object (*Person, Person)
  - Mutable reference (&Person!)
    - Immutable reference (&Person)
