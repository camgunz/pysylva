# Interfaces

Interfaces allow the programmer to indicate that a set of functionality is
available on a specific shape of data.

```sylva
iface Orderable {
  get_rank: (self: Orderable): uint,
  comes_before: (self: Orderable, other: Orderable): bool {
    return self.get_rank() < other.get_rank()
  },
}

iface Sortable {
  sort: (self: Sortable!),
}

impl Sortable(&[Orderable]) {
  sort: (self: &[Orderable]!) {
    ...
  },
}

impl Orderable(int) {
  get_rank: (self: int): uint {
    return self
  },
}
```

Interfaces can have concrete methods:

```sylva
req sys

iface Greeter {
  get_greeting: (animal: &Animal): str
}

fn greet(animal: &Animal) {
  sys.echo("{animal.get_greeting()}!")
}

struct Cat {}

impl Greeter(Cat) {
  get_greeting: (self: &Cat): str { return "Meow" }
}

struct Dog {}

impl Greeter(Dog) {
  get_greeting: (self: &Dog): str { return "Woof" }
}
```

## Interfaces vs. variants

Interfaces and variants are similar in that they allow the programmer to extend
types, but dissimilar in the kind of extension they enable. Variants allow
extension of the _shape_ of a type (i.e. its fields), whereas interfaces allow
extension of the _abilities_ of a type (i.e. its functions). When deciding
whether to use interfaces or variants, consider whether you'll likely be adding
new shapes or new abilities.

In particular, avoid using interfaces _instead of_ variants. In most cases,
they are orthogonal. For example, if Sylva's failures were an interface opening
a file would have to look something like:

```sylva
mod sys

iface OpenFileResult {
  succeeded: (): bool
  get_file: (): *File
  get_failure_code: (): uint
  get_failure_message: (): str
}

mod main

req sys

fn main() {
  let file_path = "/home/dmr/.secrets"
  let res = sys.open(file_path, "r") # `res` is an `OpenFileResult` here

  if (res.succeeded()) {
    sys.echo("Data: {res.get_file().read_all()}")
  }
  else {
    sys.echoerr(
      "[{res.get_code()}] Failed to read {file_path}: {res.get_message()}"
    )
  }
}
```

Here, the result of `sys.open` evades type checking. If we want to implement
`res.get_file()` when `res.succeeed()` would return `false`, we have a couple
of non-ideal options:
- Return some kind of "null"
- Return an ersatz "File" that has a bunch of "this isn't a real file" results,
  like `.read_all()` returns `""`, and so on.

However, with variants this becomes robust:

```sylva
fn main() {
  let file_path = "/home/dmr/.secrets"
  let res: sys.open(file_path, "r")

  match (res) {
    case (file: FileOpen.OK) {
      sys.echo("Data: {file.read_utf8()}")
    }
    case (f: FileOpen.Failed) {
      sys.echoerr("[{f.code}] Failed to open {file_path}: {f}")
    }
  }
}
```

<!-- [NOTE] A good example in favor of interfaces are streams -->

Finally, bear in mind the tradeoffs of interfaces and variants. Sylva's
implementation of interfaces requires dereferencing, and the very concept of
interfaces necessitates function call overhead--after all interfaces are simply
additional functions, so you must call those functions in order to take
advantage of the interface. Sylva's implementation of variants requires
additional information in data structures, and in general uses more memory than
necessary to represent every possible variant.
