# Failures

Sometimes things don't go your way. While we can't anticipate everything (gamma
rays, children), it is within our power to anticipate a great number of
failures. Sylva does this using variants, specifically a `Result` `struct`,
very similar to Rust:

```sylva
struct Result (ok_type, failed_type) {
  variant OK: ok_type
  variant Failed: failed_type
}
```

[Errors are values](https://blog.golang.org/errors-are-values); we would go so
far as to not call them "errors"--which are *mistakes*--but rather "failures",
which are a *lack of success*. Sylva knows what is and isn't valid Sylva and is
thus qualified to judge errors there (say at lex or parse time), but is too
polite to say what is or isn't a mistake in an application's behavior. To that
end, it provides facilities to group results into successes or failures:

```sylva
requirement sys

range Age (0u8, 250u8)

fn increment(age: Age): Age {
  return age + Age(1) # Failure!
}

fn main() {
  increment(Age(37))
  increment(Age(250))
}
```

Here, we have a simple function that has the potential to extend a value beyond
its range, and as a result, the operation returns a `Result` instead of an
`Age`. Simply changing the function's return type fixes this error:

```sylva
requirement sys

range Age (0u8, 250u8)

fn increment(age: Age): Result {
  return (age + Age(1)) # Potential failure!
}

fn main() {
  increment(Age(37))
  increment(Age(250))
}
```

However, this isn't very useful. It would be better if we handled the failure
case at the site:

```sylva
requirement sys

range Age (0u8, 250u8)

fn increment(age: Age): Age {
  return (age + Age(1)).on_failure(fn (f: Failure) {
    sys.die("Age {age} is already the max age")
  }).value
}

fn main() {
  increment(Age(37))
  increment(Age(250))
}
```

You may be thinking "`sys.die` doesn't return an `Age`, that should also be an
error". Good catch! Sylva is smart enough to not worry about cases that
definitely exit\*.

\* _Keep in mind, however, that branching or flow control of any kind will foil
this analysis._

## Building blocks

The `Result` system is fairly barebones, whose goal is to provide a complete
failure handling solution that can be built upon by the programmer, making
their own decisions about the tradeoffs involved. Here's an example that adds
a little more information at the expense of some memory and performance:

```sylva
module checked

# Mathematical "errors" we want to catch

enum MathFailures {
  DivisionByZero: "Division by zero"
  NonPositiveLogarithm: "Non-Positive logarithm"
  NegativeSquareRoot: "Negative square root"
}

alias FloatResult: Result(f64, MathFailures)

fn div(x: f64, y: f64): FloatResult {
  if (y == 0.0) {
    # This operation would 'fail', instead let's return the reason of the
    # failure wrapped in Failure
    return FloatResult.Failed.DivisionByZero
  }
  return FloatResult.OK(x / y)
}

fn sqrt(x: f64): FloatResult {
  if (x < 0.0) {
    return FloatResult.Failed.NegativeSquareRoot
  }

  return FloatResult.OK(x.sqrt())
}

fn ln(x: f64): FloatResult {
  if (x <= 0.0) {
    return FloatResult.Failed.NonPositiveLogarithm
  }

  return FloatResult.OK(x.ln())
}

module main

requirement sys
requirement checked

fn quit_because_math_too_hard(f: MathFailure) {
  sys.die(f.message)
}

# `op(x, y)` == `sqrt(ln(x / y))`
fn op(x: f64, y: f64): f64 {
  # This is a three level match pyramid!
  var div_res: checked.div(x, y)
    .on_failure(quit_because_math_too_hard).value
  var ln_res: checked.ln(div_res)
    .on_failure(quit_because_math_too_hard).value
  var sqrt_res: checked.sqrt(ln_res)
    .on_failure(quit_because_math_too_hard).value

  return sqrt_res
}

fn main() {
  # Will this fail?
  echo("{op(1.0, 10.0)}")
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
