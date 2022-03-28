# Failures

Sometimes things don't go your way. While we can't anticipate everything (gamma
rays, children), it is within our power to anticipate a great number of
failures. Sylva does this using variants, specifically a `Result` `variant`,
very similar to Rust:

```sylva
req sys

variant Result(ok_type, failed_type) {
  OK: ok_type,
  Fail: failed_type,
}

fn on_failure(ok_type, failed_type) (
    r: Result(ok_type, failed_type),
    handler: fntype(f: failed_type)
  ): Result(ok_type, failed_type) {
  match (r) {
    case (failed_variant: Result.Fail) {
      handler(failed_variant)
    }
    default {}
  }

  return r
}

fn succeed_or_die(ok_type, failed_type) (
    r: Result(ok_type, failed_type),
    handler: fntype(f: failed_type)
  ): Result(ok_type, failed_type) {
  match (r) {
    case (f: Result.Fail) {
      sys.die("{f}")
    }
    default {}
  }

  return r
}

fn succeed_or_die(r: Result(ok_type, failed_type)): ok_type {
  r.on_failure(fn(f: failed_type) { sys.die("{failed_type}") }).OK
}
```

[Errors are values](https://blog.golang.org/errors-are-values); we would go so
far as to not call them "errors"--which are *mistakes*--but rather "failures",
which are a *lack of success*. Sylva knows what is and isn't valid Sylva and is
thus qualified to judge errors there (say at lex or parse time), but is too
polite to say what is or isn't a mistake in an application's behavior. To that
end, it provides facilities to group results into successes or failures:

```sylva
req sys

range Age 0u8..250u8

fn increment(age: Age): Age {
  return age++ # Error!
}

fn main() {
  increment(Age(37u8))
  increment(Age(250u8))
}
```

This simple function `increment` attempts to return the result of `age +
Age(1)`, and this surprisingly yields an error. This is because that expression
has the potential to extend the value beyond its range--imagine if `age` were
already `Age(250u8)`--and the operation returns a `Result(age, RangeError)`,
but `increment`'s return value is `Age`. Simply changing the function's return
type fixes this error:

```sylva
req sys

range Age 0u8..250u8

fn increment(age: Age): Result(age, RangeError) {
  return age++ # Potential failure!
}

fn main() {
  increment(Age(37u8))
  increment(Age(250u8))
}
```

However, we've only corrected our own error. It would be better to handle the
failure case at the site:

```sylva
req sys

range Age 0u8..250u8

fn increment(age: Age): Age {
  match (r: age + Age(1u8)) {
    case (new_age: OK) {
      return new_age
    }
    case (failure: RangeError) {
      sys.die("Out of range")
    }
  }
}

fn main() {
  increment(Age(37u8))
  increment(Age(250u8))
}
```

_(You may be thinking "`sys.die` doesn't return an `Age`, that should also be an
error". Good catch! Sylva is smart enough to not worry about cases that
definitely exit. Keep in mind, however, that branching or flow control of any
kind will foil this analysis.)_

Writing `match` statements everywhere an operation may fail is laborious and
tedious. So Sylva provides some helpers we can use:

```sylva
req sys

range Age 0u8..250u8

fn increment(age: Age): Age {
  return (age + Age(1u8)).succeed_or_die()
}

fn main() {
  increment(Age(37u8))
  increment(Age(250u8))
}
```

## Building blocks

`Result` is a fairly barebones system meant to serve as a foundation to the
programmer, making their own decisions about the tradeoffs involved. Here's an
example that adds a little more information at the expense of some memory and
performance:

```sylva
mod checked

# Mathematical "errors" we want to catch

enum MathFailure {
  DivisionByZero: "Division by zero"
  NonPositiveLogarithm: "Non-Positive logarithm"
  NegativeSquareRoot: "Negative square root"
}

alias FloatResult: Result(f64, MathFailure)

fn div(x: f64, y: f64): FloatResult {
  if (y == 0.0) {
    # This operation would 'fail', instead let's return the reason of the
    # failure wrapped in Failure
    return FloatResult.Fail.DivisionByZero
  }
  return FloatResult.OK(x / y)
}

fn sqrt(x: f64): FloatResult {
  if (x < 0.0) {
    return FloatResult.Fail.NegativeSquareRoot
  }

  return FloatResult.OK(x.sqrt())
}

fn ln(x: f64): FloatResult {
  if (x <= 0.0) {
    return FloatResult.Fail.NonPositiveLogarithm
  }

  return FloatResult.OK(x.ln())
}

mod main

req sys
req checked

# `op(x, y)` == `sqrt(ln(x / y))`
fn op(x: f64, y: f64): f64 {
  # This is a three level match pyramid!
  var div_res: checked.div(x, y).succeed_or_die()
  var ln_res: checked.ln(div_res).succeed_or_die()
  var sqrt_res: checked.sqrt(ln_res).succeed_or_die()

  return sqrt_res
}

fn main() {
  # Will this fail?
  sys.echo("{op(1.0f64, 10.0f64)}")
}
```

```rust
mod checked {
    // Mathematical "errors" we want to catch
    #[derive(Debug)]
    pub enum MathError {
        DivisionByZero,
        NonPositiveLogarithm,
        NegativeSquareRoot,
    }

    pub type MathResult = Result<f64, MathError>;

    pub fn div(x: f64, y: f64) -> MathResult {
        if y == 0.0 {
            // This operation would `fail`, instead let's return the reason of
            // the failure wrapped in `Fail`
            Err(MathError::DivisionByZero)
        } else {
            // This operation is valid, return the result wrapped in `Ok`
            Ok(x / y)
        }
    }

    pub fn sqrt(x: f64) -> MathResult {
        if x < 0.0 {
            Err(MathError::NegativeSquareRoot)
        } else {
            Ok(x.sqrt())
        }
    }

    pub fn ln(x: f64) -> MathResult {
        if x <= 0.0 {
            Err(MathError::NonPositiveLogarithm)
        } else {
            Ok(x.ln())
        }
    }
}

// `op(x, y)` === `sqrt(ln(x / y))`
fn op(x: f64, y: f64) -> f64 {
    // This is a three level match pyramid!
    match checked::div(x, y) {
        Err(why) => panic!("{:?}", why),
        Ok(ratio) => match checked::ln(ratio) {
            Err(why) => panic!("{:?}", why),
            Ok(ln) => match checked::sqrt(ln) {
                Err(why) => panic!("{:?}", why),
                Ok(sqrt) => sqrt,
            },
        },
    }
}

fn main() {
    // Will this fail?
    println!("{}", op(1.0, 10.0));
}
```
