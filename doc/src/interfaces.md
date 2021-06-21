# Interfaces

Interfaces are an alternative to variants, intended to allow the programmer to
signal that some set of functionality is available on a specific shape of data.
Variants and their functions must be modified to extend them in this way, which
is not always possible or practical.

```sylva
interface Sortable {
  fn sort(self: Sortable!)
}

interface Orderable {
  fn get_rank(self: Orderable): num
  fn comes_before(self: Orderable, other: Orderable): bool {
    return(self.get_rank() < other.get_rank())
  }
}

implementation Orderable: int {
  fn get_rank(self: int): num {
    return self
  }
}

implementation Sortable: array[Orderable] {
  fn sort(self: array[Orderable]!) {
    ...
  }
}
```

Interfaces can have concrete methods:

```sylva
requirement sys

interface Animal {
  fn get_greeting(animal: &Animal): str
}

fn greet(animal: &Animal) {
  sys.echo("{animal.get_greeting()}!")
}

struct Cat {}

implementation Animal: Cat {
  fn get_greeting(self: &Cat): str { return "Meow" }
}

struct Dog {}

implementation Animal: Dog {
  fn get_greeting(self: &Dog): str { return "Woof" }
}
```

## Interfaces vs. variants

While sometimes convenient, interfaces have a number of drawbacks compared with
variants:
- slightly slower (dereferencing, function call overhead)
- slightly more verbose
- difficult to handle failure cases

The last point bears some exposition. If, for example, failures were an
interface, then opening a file would have to look something like:

```sylva
interface OpenFileResult {
  fn succeeded(): bool
  fn get_file(): *File
  fn get_failure_code(): uint
  fn get_failure_message(): str
}

fn main() {
  var file_path = "/home/dmr/.secrets"
  var res = sys.open(file_path, "r")
  if res.succeeded() {
    sys.echo("Data: {res.get_file().read_all()}")
  }
  else {
    sys.echoerr(
      "[{res.get_code()}] Failed to read {file_path}: {res.get_message()}"
    )
  }
}
```

In this way, the result of `sys.open` evades type checking. If we want to
implement `res.get_file()` when `res.succeeed()` would return `false`, we have
a couple of bad options:
- Return some kind of "null"
- Return an ersatz "File" that has a bunch of "this isn't a real file" results,
  like `.read_all()` returns `""`, and so on.

However, with variants this becomes robust:

```sylva
fn main() {
  var file_path = "/home/dmr/.secrets"
  var res: sys.open(file_path, "r")

  match (res) {
    case (OK) {
      sys.echo("Data: {file.read_utf8()}")
    }
    case (Failed) {
      sys.echoerr("[{res.code}] Failed to open {file_path}: {res.message}")
    }
  }
}
```
