# Memory, variables, and safety

In service of memory and data race safety, Sylva's use of variables (binding
values to names within a scope) is somewhat different than most other
programming languages, It establishes a set of rules for maintaining memory
safety in order to make these guarantees, and provides some helpful syntax as
well.

## Values, pointers, and references

Values are Sylva's simplest form of memory. They're allocated on the stack, are
mutable, and can be either scalars or aggregates. Owned pointers (often simply
"pointers") are similar, only they are allocated on the heap.

References are different than either values or pointers. There are two types:
shared (`&value`) and exclusive (`&value!`). Shared references can be copied,
but cannot be mutated. Exclusive references cannot be copied, but _can_ be
mutated.

### Stack vs. heap

If you're not familiar with the stack and the heap, the quick explanation is
that the stack is a preallocated section of memory in which functions do their
work.  For example:

```sylva
fn main() {
  let a: [i32 * 4][1i32, 2i32, 3i32, 4i32]
  let b: true
  let d: [i32...][1i32, 2i32, 3i32, 4i32]
  let f: 4.8f32
  let i: 4u
  let r: '🌲'
  let s: "Hello World!"
}
```

Here we have several variables defined using literals, all allocated on the
stack (though, note that while `d` itself is allocated on the stack, its data
is allocated on the heap).

Using the stack is fast, as it's preallocated. On the other hand, stack space
is limited, and references to values allocated on the stack cannot exist
outside the function. This is because once the function returns its stack space
may be reused by a different function, so it's no longer guaranteed to hold the
values it once did.

Although it's slower, by allocating values on the heap we are able to create
values that aren't restricted by the stack's size or the function's scope. As
an application language, Sylva provides easy support for heap allocation using
`*`:

```sylva
struct Person {
  name: str,
  age: u8,
}

fn make_person(name: str, age: u8): *Person {
  return *Person{name, age} # Allocates and moves simultaneously
}

fn main() {
  let barack: make_person("Barack", 57)
}
```

Heap allocation allows `make_person` to create a value that outlives its scope,
such that returning it is safe. Its caller becomes the owner, in this case
that's `main`, so the return value will be freed when `main` returns.

By itself, Sylva does not require heap allocation from the target platform.
A program without `*`, template strings, and dynarrays will not employ heap
allocation.

## Scalars vs. aggregates

Sylva's scalar types are `bool`, `float`, `int`, `uint`, `rune`, and `str`.
Everything else (`array`, `dynarray`, `enum`, `iface`, `string`, `struct`,
`variant`) is an aggregate type.

Sylva will copy scalars for you (using `=`), but it will not copy aggregates (
this would undermine pointer tracking by potentially creating multiple owners
or exclusive references when the enclosing aggregate is copied). This means
that aggregates must be passed by reference--using `*` or `&`--into detached
scopes (this does not apply to function return values, as returning a value is
not passing it into a detached scope).

Additionally, only scalar variables may be reassigned:

```sylva
struct Person {
  name: str,
  age: u8
}

fn main() {
  let age: 60

  age = 61 # could also use age++

  let p: Person{"Barack", age}

  p = Person{"Charlie", 38} # Error!
}
```

## Scopes and sigils

Sylva defines several types of scopes. Scopes can often nest, e.g. arrays and
structs can exist within functions or each other, and so on. Whether something
is allocated on the stack or the heap, it starts inside a scope:

```sylva
fn main() {
  let age: 61
}
```

Here, `age` exists in `main`'s scope. As a scalar value, it can be copied into
a different scope like a struct:

```sylva
struct Person {
  name: str,
  age: u8,
}

fn main() {
  let age: 61
  let barack: Person{"Barack", 0}

  barack.age = age
}
```

Again, this flexibility doesn't extend to aggregate types. In order to put
something more complicated inside `Person`, we need a reference or a pointer:

```sylva
req sys

struct Pet {
  name: str,
}

struct Person {
  name: str,
  age: u8,
  pet: &Pet,
}

fn print_person(person: &Person) {
  sys.echo("{person.name} has a pet {person.pet.name}")
}

fn print_obama_with_pet(pet: &Pet) {
  let barack: Person{"Barack", 57, &pet} # n.b. the '&' before "pet" here is
                                         # unnecessary
  print_person(&barack)
}

fn main() {
  let bo: Pet{"Bo"}
  print_obama_with_pet(&bo)
}
```

### Normal vs. detached scopes

Sylva makes a distinction between "normal" and "detached" scopes:

**Normal scopes:**
- expressions
- statement blocks
- variables

**Detached scopes:**
- arrays
- dynarrays
- functions
- structs
- variants

Detached scopes are scopes that might not be direct descendants of the current
scope, and therefore we have to be careful about what we put into or take out
of them.

### Sigils

When defining detached scopes, we need to indicate the types of variables they
accept, and we do so with a small number of sigils:

**Identifiers**:
- `&<var>`: Take a shared reference
  - Shared references don't need to be moved into detached scopes; they can be
    copied instead
- `&<var>!`: Take an exclusive reference and move it into this scope
- `*<var>`: Move this owned pointer into this scope

**Literals**:
- `&<literal>`: Create a temporary value and take a shared reference to it
- `&<literal>!`: Create a temporary value, take an exclusive reference to it,
                 and move the reference into this scope
- `*<literal>`: Allocate a value on the heap, and move the resulting owned
                pointer into this scope

A code example:

```sylva
fn try_to_alias_scalar(i: int) {
  let i2: i # Copies i
}

fn try_to_alias_ref(i: &int) {
  let i2: i # Creates a copy (an alias) of the shared reference
  let i3: &i # Creates another copy (an alias) of the shared reference
}

fn try_to_alias_exref(i: &int!) {
  let i2: i # Error: Cannot copy an exclusive reference
  let i3: &i # Error: Cannot copy an exclusive reference
  let i4: &i! # Moves i into i4; i is no longer valid
}

fn try_to_alias_owned_pointer(i: *int) {
  let i2: i # Error: Cannot copy an owned pointer
  let i3: *i # Moves i into i3, i is no longer valid
  let i4: &i # Takes a reference to the value pointed at by i; i is no longer
             # valid and will be deallocated when this scope closes
  let i5: &i! # Takes an exclusive reference to the value pointed at by i; i is
              # no longer valid and will be deallocated when this scope closes
}
```

Why the syntax overload in `try_to_alias_ref`? Sylva doesn't have the concept
of references to other references. Taking a shared reference to another shared
reference simply copies the shared reference. Copying is also what a `let`
binding does to an identifier like `i` (not a literal like `14u`). So these two
syntaxes have the same semantics.
"Movement" here means the variables move into another scope, and can no longer
be accessed in any other scopes.

Sigils are used in consistent, overlapping ways:
- When defining a detached scope, they signify reference/pointer types
- In expressions, they heap allocate + move or take a reference (and maybe
  move, in the case of exclusive references)

To see what we mean by "overlapping", consider this example:

For example, we would say `[&i32 * 27]` for an array of 27 references to 32-bit
signed integers, or `[*i32 * 27]` for an array of 27 owned pointers to 32-bit
signed integers, and so on.

We do the same when passing variables into and out of detached scopes:

```sylva
fn main() {
  let deciduous: '🌳'
  let pine:'🌲'
  let xmas: '🎄'
  let palm: '🌴'
  let tanabata: '🎋'
  let little: '🌱'
  let broccoli: '🥦'
  let trees: [&rune * 6][&deciduous, &pine, &xmas, &palm, &tanabata, &little]

  # We use the `&` sigil on broccoli to conform with its element type `&rune`,
  # that is, the sigils "overlap" across a detached scope.
  trees[5] = &broccoli

  for (i: trees::indices) {
    sys.echo("Tree: {&trees[i]}")
  }
}
```

In normal (direct descendant) scopes, we don't use sigils:

```sylva
struct TreeMoji {
  pine: rune('🌲')
  palm: rune('🌴')
  tree: rune('🌳')
}

fn print_treemoji(tm: *TreeMoji, name: str) {
  let treemoji: ''

  # There's no need to use `*` when referencing `tm` here, as the `if`
  # statement block is a normal scope, not a detached scope
  if (name == "pine") {
    treemoji = tm.pine
  }
  else if (tree == "palm") {
    treemoji = tm.palm
  }
  else if (tree == "deciduous") {
    treemoji = tm.deciduous
  }

  sys.echo("Treemoji is {treemoji}")
}
```

However, passing values into detached scopes requires sigils:

```sylva
struct Pet {
  name: str
}

struct Person {
  name: str,
  age: u8,
  pet: *Pet
}

fn print_person(p: &Person) {
  sys.echo("{p.name}'s pet's name is {p.pet.name}")
}

fn main() {
  let p: Person{
    name: "Barack",
    age: 61u8,
    pet: *Pet{
      name: "Bo"
    }
  }

  print_person(&p)

  let pref: &p

  print_person(pref)
}
```

When creating a value for the `pet` field we used `*`. This allocates it on the
heap and moves it into `p`'s scope. This overlaps with the `pet` field's type,
which is `*Pet`. Similarly for `print_person(&p)`, we take a shared reference
to `p` and pass it into `print_person`, which is a detached scope. This
overlaps with `print_person`'s `p` argument, which is a `&Person`.

### References to owned pointers

When taking a reference to an owned pointer, if that reference exists in the
same scope as the pointer, the pointer's value will be deallocated when the
scope closes because its pointer went out of scope.

To avoid this, use the reference sigils in lower scopes, like directly in the
function call:

```sylva
req sys

struct Person {
  name: str,
  age: u8
}

fn print_person(p: &Person!) {
  sys.echo("{p.name} is {p.age} years old")
}

fn lose_person_forever(p: *Person) {
  let pref: &p! # p is now invalid in this scope
  print_person(pref)
}

fn keep_person_around(p: *Person) {
  print_person(&p!) # Could still use p after this if we wanted
}
```

### Sigils and aggregate values

An aggregate value and its members are package deals with it comes to sigils.

An aggregate value's members cannot be moved on their own.
  - e.g. `*p.pet` would fail
Taking a reference to an aggregate value's members imposes its restrictions on
the aggregate value as well
  - e.g. `&p.name` means a `&p!` in the same scope would fail

## Safety rules and scope hierarchy

Sigils are designed to help you know what's possible with variables at a
glance. Their visual representation and semantics are guides to help describe
the consequences of various referencing operations, and narrow what is possible
with a variable:

- Taking a shared reference to a bare value disallows taking exclusive
  references of that value in that scope
- Taking a shared reference to an owned pointer disallows using the owned
  pointer in that scope
- Taking a shared reference to a shared reference copies the shared reference
- Taking a shared reference to an exclusive reference is not allowed
- Taking an exclusive reference to a bare value disallows taking other
  exclusive references of that value in that scope
- Taking an exclusive reference to an owned pointer invalidates the owned
  pointer in that scope

Along these lines, Sylva imposes a further condition on references: they can
never ascend scopes.

*[TODO] Figure out how to impose restrictions on multithreaded code (it does
seem like we need language-level (not library-level) support because of this
need*

Sylva tracks the scope of every value, pointer, and reference, as well as any
time they might change scopes, and disallows any situation where a reference
might potentially ascend. For example (with credit to Rust):

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
variables, e.g. 

## Aliasing

Though the above may have implied Sylva's aliasing semantics, to be explicit,
Sylva's syntax and semantics only allow aliasing (multiple pointers or
references to the same value) through shared references. Here are the gamut of
bindings:

