# Error Handling

Sometimes things go wrong: a network connection fails, disk I/O times out, and
you need to define behavior for those cases.  For that, Sylva provides `error`:

```sylva
requirement sys

fn i_fail(): int {
  error("Should've seen this coming!!")
  return 14
}

fn main() {
  with(n: i_fail()) {
    sys.echo("{n}")
  }
  else(e) {
    sys.echoerr("Got error: {e}")
  }
}
```

The `with` statement binds the result of `i_fail` to `n` if it succeeds, and
the error result to `e` if it fails.  If you only want to handle the error
case, use `iferr`:

```sylva
requirement sys

fn i_fail(): int {
  error("Should've seen this coming!!")
  return 14
}

fn main() {
  iferr(e: i_fail()) {
    sys.echoerr("Got error: {e}")
  }
}
```

Notably, `iferr` has no success branch.  If you want to handle both the success
and error cases, use `with`/`else`.

In case you don't need the exact success or error value, or the function simply
doesn't return a success value, you can omit the binding:

```sylva
requirement sys

fn i_fail() {
  error("Should've seen this coming!!")
}

fn main() {
  with(i_fail()) {
    sys.echo("This totes worked")
  }
  else {
    sys.echoerr("Got an error, good luck figuring it out!")
  }
}
```

Further, the `else` statements are unnecessary in any case (with or without
binding):

```sylva
requirement sys

fn i_fail() {
  error("Should've seen this coming!!")
}

fn call_ifail() {
  with(i_fail()) {
    sys.echo("This totes worked")
  }
}

fn main() {
  iferr(call_ifail()) {
    sys.echoerr("Predictably, ifail failed")
  }
}
```

Note that omitting the `else` block from `with` means that function must also
be called with `with` or `iferr`.

```sylva
requirement sys

fn i_fail() {
  error("Should've seen this coming!!")
}

fn main() {
  iferr(i_fail()) {
    sys.echoerr("Got an error, good luck figuring it out!")
  }
}
```

`with` and `iferr` accept any expression:

```sylva
requirement sys

fn main() {
  with(quo: 14 / 0) {
    sys.echo("Quotient: {quo}")
  }
  else(err) {
    sys.echoerr("Error: {err}")
  }

  iferr(wrap: 255u8 * 4) {
    sys.echo("Error: {err}")
  }
}
```

## Safety

Any expression that may return an error **must** be handled inside a `with`
or `iferr` block.

## `Error`

`Error` is an interface, and its only required function is `__str`.
Consequently most builtin types can be used.  Additionally, more complex error
types can be defined and used with `match`:

```sylva
requirement sys

struct BetterError {
  msg: str
  code: uint
}

implementation(BetterError): Error {
  fn __str(self: &BetterError): str {
    return self.msg
  }
}

fn berror(code: uint, msg: str) {
  error(BetterError(code: code, msg: msg))
}

fn i_fail(): int {
  berror(666, "Should've seen this coming!!")
}

fn main() {
  with(n: i_fail()) {
    sys.echo("{n}")
  }
  else(err) {
    match(err) {
      case(BetterError) {
        sys.echoerr("Error {err.code}: {err.msg}")
      }
      case(Error) {
        sys.echoerr("Got error: {e}")
      }
    }
  }
}
```
