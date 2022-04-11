# Memory

Sylva uses a handful of concepts to manage menory, chief among these are scope,
automatic dereferencing, and exclusivity.

## Stack vs. heap

If you're not familiar with the stack and the heap, the quick explanation is
that the stack is a preallocated section of memory in which functions do their
work.  For example:

```sylva
fn main() {
  let age: 42
}
```

Here, `age` is allocated on the stack.

Using the stack is fast, as it's preallocated. On the other hand, stack space
is limited, and references to values allocated on the stack cannot exist
outside the function. This is because once the function returns its stack space
may be reused by a different function, so it's no longer guaranteed to hold the
values it once did.

By allocating values on the heap, we are able to create values that aren't
restricted by the stack's size or the function's scope. However, it is slower,
and in languages like C and C++, heap values aren't automatically cleaned up
when a function returns (i.e. the memory "leaks").

## Heap allocation

As an application language, Sylva provides easy support for heap allocation
using `*`:

```sylva
req sys

struct Person {
  name: str,
  age: u8,
}

fn main() {
  let barack: *Person{name: "Barack", age: 57}
  let obamas: *[Person * 2][
    Person{name: "Barack", age: 57},
    Person{name: "Michelle", age: 56},
  ]
}
```

`*` is also used in different contexts:

- When moving into a different scope (function call, variable assignment)
  - `greet(*barack)`
  - `let new_barack: *barack`
- When declaring a scope that requires ownership over a parameter
  - `struct Person { name: *str, age: u8 }`
  - `fn greet(person *Person)`
- When declaring a function that sends its return value into the calling
  scope
  - `fn make_person(name: str, age: u8): *Person`

The reason for this reuse is to keep the mental model consistent. Heap
allocations must **move** through different scopes, so `*` acts something
like a tag.

By itself, Sylva does not require heap allocation from the target platform.
A program without `*` and template strings will not employ heap allocation.

## Safety

Memory and data race safety boil down to two guarantees:
- when writing to memory, nothing else will read or write that memory
- any memory read reads valid memory

Sylva establishes a set of rules or maintaining memory safety in order to make
these guarantees, and provides some helpful syntax as well.

### Values, pointers, and references

Values are Sylva's simplest form of memory. They exist on the stack and are
mutable. They can be either scalars or aggregates; scalars include `bool`,
`(u)int`, `float`, and `rune`; aggregates include `str`, and any defined
`struct`s or arrays.

Sylva will copy scalars for you, but it will not copy aggregates (deep
copying). This also means that aggregate values must be passed to other scopes
by creating a reference to them (pass by reference).

Pointers exist on the heap and are mutable. They are allocated and moved into
different scopes using `*`:

```sylva
mod main
req sys

struct Person {
  name: str,
  age: u8
}

fn say_hey(person *Person) {
  sys.echo("Hey {person.name}")
}

fn main() {
  let person: *Person{"Barack", 57}

  say_hey(*person)

  say_hey(*Person{"Michelle", 56}) # `*` serves both as allocate and move here
}
```

References are different than either values or pointers. There are two types:
shared (`&value`) and exclusive (`&value!`). Shared references can be copied,
but cannot be mutated. Exclusive references cannot be copied, but _can_ be
mutated.

### Scope

In Sylva, values, pointers, and references all have a scope. There are six
types of scopes:
- structs/variants
- arrays
- functions
- variable bindings
- blocks
- expressions

Scopes can nest, e.g. arrays and structs can exist within functions or other
structs, and so on.

Whether something is allocated on the stack or the heap, it starts inside a
scope:

```sylva
fn main() { # scope main.main
  let age: 57; # scope main.main.let1
}
```

Here, `age` exists in scope `main.main.let1`. As a scalar value, it can be
copied into a different scope like a struct:

```sylva
struct Person {
  name: str,
  age: u8,
}

fn main() {
  let age: 57
  let barack: Person{"Barack", 0}

  barack.age = age
}
```

But aggregate values cannot be so copied:

```sylva
struct Pet {
  name: str,
}

struct Person {
  name: str,
  age: u8,
  pet: Pet,
}

fn main() {
  let bo: Pet{"Bo"}
  let barack: Person{"Barack", 57, bo} # Error!
}
```

Sylva disallows deep copies like this because they can undermine its pointer
tracking by creating multiple owners or exclusive references.

So we can't copy it, but we still need to refer to it, even if it's allocated
in another scope. This is exactly what references are for:

```sylva
struct Pet {
  name: str,
}

struct Person {
  name: str,
  age: u8,
  pet: &Pet,
}

fn main() {
  let bo: Pet{"Bo"}
  let barack: Person{"Barack", 57, &bo}
}
```

Here, we're sending a reference to `bo` into a _lower_ scope `barack.pet`. We
would also be successful if we defined another variable like `let bo2: &bo`,
because that would be an _adjacent_ scope. References cannot _ascend_ in scope,
however, which is a problem when trying to hand a value off:

```sylva
struct Person {
  name: str,
  age: u8,
}

fn make_person(name: str, age: u8): &Person! {
  let person: Person{name, age}

  return &person! # Error!
}

fn main() {
  let barack: make_person("Barack", 57)
}
```

This is where pointers are useful:

```sylva
struct Person {
  name: str,
  age: u8,
}

fn make_person(name: str, age: u8): *Person {
  return *Person{name, age}
}

fn main() {
  let barack: make_person("Barack", 57)
}
```

Here, `barack` is now a heap-allocated pointer to a `Person` struct, which will
be freed when `main` returns.

### Safety Rules

As stated above, Sylva establishes rules in order to guarantee memory safety.
We've encountered two rules already:

- References cannot ascend scopes
- Pointers must be moved into other scopes
- Values must be passed by reference into other scopes
- Pointers must either be passed by reference or moved into other scopes
  - Pointers do not need the `&` prefix to be passed by shared reference
  - Pointers do need the `!` suffix to be passed by exclusive reference

These rules alone are insufficient for our guarantee. Here are the rest:

- An exclusive reference cannot be made if another reference exists
- Once an exclusive reference to a value is made, another reference to that
  value cannot be made in any adjacent or lower scope
- Once an exclusive reference to a value is made, that value cannot be used in
  that scope or any lower scope.
- Once a pointer is moved, it cannot be used in that scope or any lower scope
- References to references cannot be made
- Pointers to pointers cannot be made

### Mechanism

How does Sylva use the constraints to ensure memory and data race safety?

The first way is through Sylva's syntax. Most scopes note their capability
requirements through the types; e.g. using `&Person!` means the function (or
struct, or array, etc.) needs to modify that value. Matching the notation when
moving values through scopes (`*` for `*Person`, `&` for `&Person`) maintains
memory safety.

Further, Sylva will enforce validity (reference exclusivity, etc.).

Finally, Sylva tracks the scope of every value, pointer, and reference as well
as any time they might change scopes, and disallows any situation where a
reference might potentially ascend. For example (with credit to Rust):

```sylva
req sys

struct Pet {
  name: str
}

struct Person {
  name: str
  age: u8
  pet: &Pet
}

fn set_person_pet(person: &Person!, pet: &Pet) {
  # Creates a requirement on `set_person_pet` that `pet`'s scope is at or
  # higher than `person.pet`'s scope
  person.pet = pet;
}

fn main() {
  let bo: Pet{name: "Bo"}
  let barack: Person{name: *"Barack", age: 59, pet: &bo}

  if (true) {
    let sunny: Pet{name: "Sunny"}

    # Without scope checking, `sunny` would be stored as `barack.pet`
    # (ascending # in scope from `main.main.if1.sunny` to
    # `main.main.barack.pet`), and then freed at the close of this `if` block,
    # creating the potential for a use-after-free bug.
    set_person_pet(&barack!, &sunny) # Error!
  }

  sys.echo(barack.pet.name)
}
```

The scopes here are:

    main.set_person_pet
    main.set_person_pet.person

    main.main
    main.main.barack
    main.main.joe

When Sylva reads the definition of `set_person_pet`, it sees it passes `pet`
into the `person.pet` scope. As a result, it enforces a requirement on every
call to `set_person_pet` that `pet` must exist at `person.pet`'s scope or
higher.

In this example, `barack`'s scope is the `main` function, and `sunny`'s scope
is `main.if1`.

Sylva knows that `set_person_pet` passes a reference to a scope at `person.pet
= pet`.  Therefore whenever it sees a call to that function, it ensures that
`pet` exists at or above the same scope as `person`. But in this case `pet` is
passed up to `person`'s scope, so Sylva generates an error at the site of the
call.

Otherwise, `barack.pet` is a reference to `sunny` after the `set_person_pet`
call, but `sunny` is freed when the `if` block closes, leaving `barack.pet`
dangling and vulnerable to a use-after-free error.
