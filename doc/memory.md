# Memory

Sylva uses a handful of concepts to manage memory; chief among these are:
bindings, mutability, exclusivity, and memspace.

## Bindings and mutability

In Sylva, data starts out as just data, and it exists in the memory scope where
it's first created.

```sylva
fn main() {
  val person: Person(name: "Charlie", age: 36) # Exists in memory scope "main"
}
```

Here, `person` is bound to a `Person` object, in memory scope "main".  Because
the binding uses `val`, the binding cannot be changed:

```sylva
fn main() {
  val person: Person(name: "Charlie", age: 36)

  person = Person(name: "Hank", age: 34) # Error!
}
```

If it used `var`, then we could bind `person` to something else later:

```sylva
fn main() {
  var person: Person(name: "Charlie", age: 36)

  person = Person(name: "Hank", age: 34)
}
```

However, any value bound to `person` must be a `Person`:

```sylva
fn main() {
  var person: Person(name: "Charlie", age: 36)

  person = Dog("Ishi", age: 10) # Error!
}
```

Additionally, `person` is immutable.  If we were to try and change its age, the
compiler would give us an error:

```sylva
fn main() {
  val person: Person(name: "Charlie", age: 36)

  person.age = 37 # Error!
}
```

In order to do this, we need to make `person` mutable:

```sylva
fn main() {
  val person!: Person(name: "Charlie", age: 36)

  person.age = 37
}
```

We can also pass data around, but for that we need references:

```sylva
fn echo_name(person: &Person) {
  echo(person.name)
}

fn main() {
  val person: Person(name: "Charlie", age: 36)

  echo_name(&person)
}
```

This reference is immutable and cannot be changed:

```sylva
fn have_birthday(person: &Person) {
  person.age++
}

fn main() {
  val person: Person(name: "Charlie", age: 36)

  have_birthday(&person) # Error!
}
```

In order to do that, we need to make `person` mutable and _also_ pass a mutable
reference to `have_birthday`:

```sylva
fn have_birthday(person: &Person!) {
  person.age++
}

fn main() {
  val person!: Person(name: "Charlie", age: 36)

  have_birthday(&person!) # Error!
}
```

## Memory Scope

Although somewhat complex, perhaps the most important concept in Sylva memory
management is memory scope (memscope).  When memory is allocated, it is tied to
a memscope, and there are three kinds: structs, arrays, functions, and blocks.
Memscopes are nestable, e.g.  functions can exist inside of modules, arrays can
exist inside of structs, and so on.

References to allocated memory can be passed to nested memscopes.  A function
can store a reference inside a nested struct, because that struct memscope will
close before the function memscope.  References cannot be passed up to outer
memscopes, however.  Consider (with credit to Rust):

```sylva
struct Cat {
  name: &str
}

fn set_cat_name(cat: &Cat!, name: &str) {
  cat.name = name
}

fn main() {
  val moni!: Cat(name: "Monica")
  {
    val feebs_name: "Phoebe"
    set_cat_name(&moni!, &feebs_name) # Error!
  }
  echo("${moni.name}")
}
```

The memscopes here are:

    main
    |
    -- moni
    |
    -- anonymous block
       |
       -- feebs_name
       |
       -- set_cat_name

In this example, `feebs_name`'s memscope is the anonymous block, and `moni`'s
memscope is the `main` function.

Sylva knows that `set_cat_name` passes a reference to a memscope at
`cat.name = name`.  Therefore whenever it sees a call to that function, it
ensures that `cat` is in or nested in the same memscope as `name`.  In this
case it's the opposite: `name` is nested in `cat`'s memscope, so Sylva
generates an error at the site of the call.

Once allocated in a scope, memory must be explicitly transferred to another
scope.

In order to transfer memory to outer memscopes, it has to be able to escape the
memscope it starts in.  For that, we declare our variables a little
differently:

```sylva
struct Cat {
  name: *str
}

fn set_cat_name(cat: &Cat!, name: *str) {
  cat.name = name
}

fn main() {
  val moni: Cat(name: "Monica")
  {
    val *feebs_name: "Phoebe"
    set_cat_name(&moni!, *feebs_name)
  }
  echo("{moni.name}")
}
```

Using `*`, we can freely move memory through any memscope we like.  However,
once it's escaped, it's no longer valid there:

```sylva
struct Cat {
  name: *str
}

fn set_cat_name(cat: &Cat!, name: *str) {
  cat.name = name
}

fn main() {
  val moni: Cat(name: "Monica")
  {
    val *feebs_name: "Phoebe"
    set_cat_name(&moni!, *feebs_name)
    echo("{feebs_name} escaped!") # Error!
  }
  echo("{moni.name}")
}
```
