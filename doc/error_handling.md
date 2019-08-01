# Error Handling

To return an Error, simply use `error`:

```sylva
extern sys

fn i_fail(): int {
  error("Should've seen this coming!!")
  return 14
}

fn main() {
  with (n: i_fail()) {
    sys.echo("{n}")
  }
  else (e) {
    sys.echo("Got error: {e}")
  }
}
```

The `with` statement binds the result of `i_fail` to `n` if it succeeds, and
the error result to `e` if it fails.  The inverse is also possible with
`iferr`:

```sylva
extern sys

fn i_fail(): int {
  error("Should've seen this coming!!")
  return 14
}

fn main() {
  iferr (e: i_fail()) {
    sys.echo("Got error: {e}")
  }
  else (n) {
    sys.echo("{n}")
  }
}
```

In case the exact success or error value is unneeded, or the function simply
doesn't return a success value, you can omit the binding:

```sylva
extern sys

fn i_fail() {
  error("Should've seen this coming!!")
}

fn main() {
  with (i_fail()) {
    sys.echo("This totes worked")
  }
  else {
    sys.echo("Got an error, good luck figuring it out!")
  }
}
```

```sylva
extern sys

fn i_fail() {
  error("Should've seen this coming!!")
}

fn main() {
  iferr (i_fail()) {
    sys.echo("Got an error, good luck figuring it out!")
  }
  else {
    sys.echo("This totes worked")
  }
}
```

Further, the `else` statements are unnecessary in any case (with or without
binding):

```sylva
extern sys

fn i_fail() {
  error("Should've seen this coming!!")
}

fn main() {
  with (i_fail()) {
    sys.echo("This totes worked")
  }
}
```

```sylva
extern sys

fn i_fail() {
  error("Should've seen this coming!!")
}

fn main() {
  iferr (i_fail()) {
    sys.echo("Got an error, good luck figuring it out!")
  }
}
```

`with` and `iferr` accept any expression:

```sylva
extern sys

fn main() {
  with (quo: 14 / 0) {
    sys.echo("Quotient: {quo}")
  }
  else (err) {
    sys.echo("Error: {err}")
  }

  iferr (wrap: 255u8 * 4) {
    sys.echo("Error: {err}")
  }
  else (res) {
    sys.echo("Result: {res}")
  }
}
```

## Safety

Any expression that may return an error  **must** be handled inside a `with`
or `iferr` statement.

## `Error`

`Error` is an interface, and its only required function is `__str`.
Consequently most builtin types can be used.
