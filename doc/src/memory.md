# Memory

Sylva uses a handful of concepts to manage memory; chief among these are
exclusivity, and memory scope (memscope).

# Memscopes

There are four types of memscopes:
- structs
- arrays
- functions
- blocks

Memscopes (generally, though blocks can only exist inside functions) are
nestable, e.g. functions can exist inside of functions, arrays can exist inside
of structs, and so on.

Whether something is allocated on the stack or the heap, it starts inside a
memscope:

```sylva
fn main() {
  var age: 59;
}
```

Here, `age` is bound to memscope `main.main`.

As a scalar, `age` can be passed around--Sylva will copy its value as needed.
But if we allocate a more complex type, Sylva will impose more restrictions
on us.

```sylva
requirement sys

struct Person {
  name: str
  age: dec
}

fn say_hey(person: Person) {  # Error!
  sys.echo("Hey {person.name}")
}

fn main() {
  var person: Person{name: "Barack", age: 59}
  say_hey(person)
}
```

Sylva will give an error on the definition of `say_hey`--complex types cannot
be passed by value. In order to do so, we can either pass by reference, or
allocate on the heap and move using `*`.

## References

References can descend into lower memscopes, and they return once those scopes
close:

```sylva
requirement sys

struct Person {
  name: str
  age: dec
}

fn say_hey(person: &Person) {
  sys.echo("Hey {person.name}")
}

fn main() {
  var person: Person{name: "Barack", age: 59}
  say_hey(&person)
  say_hey(&person)
}
```

However, they cannot ascend into higher memscopes. Consider (with credit to
Rust):

```sylva
requirement sys

struct Person {
  name: &str
  age: dec
}

fn set_person_name(person: &Person!, name: &str) {
  person.name = name
}

fn main() {
  var barack: Person{name: &"Barack", age: 59}
  var joe: Person{name: "Joe", age: 78}

  # This function call will trigger an error in Sylva
  set_person_name(&barack!, &joe.name) # Error!

  # Without Sylva's memscope checking, this function call would change joe.name
  # and leave barack.name dangling, vulnerable to a use-after-free bug.
  set_person_name(&joe!, "Joseph")
  sys.echo("{barack.name}")
}
```

The memscopes here are:

    set_person_name
    set_person_name.person

    main
    main.barack
    main.joe

When Sylva reads the definition of `set_person_name`, it sees it passes `name`
into the `person` memscope. As a result, it enforces a requirement on every
call to `set_person_name` that `name` must exist at `person`'s memscope or
higher.

In this example, `joe` and `barack`'s memscope is the `main` function, and
`joe.name`'s memscope is `joe`.

Sylva knows that `set_person_name` passes a reference to a memscope at
`person.name = name`.  Therefore whenever it sees a call to that function, it
ensures that `name` is passed down or laterally to the same scope as `person`.
But in this case it's the opposite: `name` is passed up to `person`'s memscope,
so Sylva generates an error at the site of the call.

After the first `set_person_name` call, `barack.name` is a reference to
`joe.name`. But the second `set_person_name` call changes `joe.name`,
invalidating `barack.name` and making it vulnerable to a use-after-free error.
Sylva's memscope checks prevent this from happening.

## Moving

References can only descend into lower memscopes, but we can explicitly
**move** memory into higher memscopes using `*`.

```sylva
requirement sys

struct Person {
  name: *str
  age: dec
}

fn set_person_name(person: &Person!, name: *str) {
  person.name = *name
}

fn main() {
  var barack: Person{name: *"Barack", age: 59}
  var joe_name: *"Joe"

  set_person_name(&barack!, *joe_name)
  sys.echo("{barack.name}")
}
```

Using `*`, we can freely move memory through any memscope we like.  However,
once it's moved, it's gone:

```sylva
requirement sys

struct Person {
  name: *str
  age: dec
}

fn set_person_name(person: &Person!, name: *str) {
  person.name = *name
}

fn main() {
  var barack: Person{name: *"Barack", age: 59}
  var joe_name: *"Joe"

  set_person_name(&barack!, *joe_name)
  sys.echo("{barack.name}")
  sys.echo("{joe_name}") # Error!
}
```
