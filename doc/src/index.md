# Sylva

Sylva is an applications programming language; it is built for writing
applications like IRC servers or login daemons.

## Hello

```sylva
mod main

req sys

range Age 0u8..250u8

struct Person {
  name: str(""),
  age: Age(0u8),
}

fn print_usage() {
  sys.die("Usage: hello [name] [age]")
}

fn have_birthday(person: &Person!) {
  let add_result: person.age + Age(1u8)

  match (add_result) {
    case (age: OK) {
      person.age = age
    }
    case (f: Fail) {
      sys.die("Person {person.name} is already the max age {person.age}")
    }
  }
}

fn greet_person(person: &Person) {
  sys.echo("Hello {person.name}!")
}

fn main() {
  let name_index_result: sys.args.get(1)
  let age_index_result: sys.args.get(2)
  let person: Person{}

  match (name_index_result) {
    case (name: OK) {
      person.name = name
    }
    case (f: Fail) {
      print_usage()
    }
  }

  match (age_index_result) {
    case (age_string: OK) {
      let parse_result = Age.parse_from_string(age_string)
      match (parse_result) {
        case (age: OK) {
          person.age = age
        }
        case (f: Fail) {
          sys.echoerr("Invalid age: {r}")
          print_usage()
        }
      }
    }
    case (f: Fail) {
      print_usage()
    }
  }

  person.have_birthday()
  greet_person(&person)
}
```

Sylva is largely [memory and data race safe](memory.html)\*, providing
protection against bugs like use after free, torn reads/writes, out-of-bounds
memory accesses, [unexpected integer wraparounds](numbers.html), etc. It is
designed to encourage the programmer to do the [robust thing](failures.html),
and to structure applications such that the robust thing is also the easy
thing.

Sylva is fast.  It is statically typed, compiled to native code ahead of time,
does not use garbage collection, and requires no runtime.

Sylva is pragmatic and unopinionated. Taste and style count, but Sylva is a
tool, and practitioners are free to use Sylva in whatever style and for
whatever purpose they choose.

Sylva is small (but not too small). The language fits in your head, and its
mental models are consistent and broadly applicable.

Sylva should be familiar to most programmers.  Where possible, it defers to
what the programmer is likely to know.

Lastly, Sylva is readable. We pay careful attention to how the syntax and
organization scan, but also to how constructs draw focus and shape thought.

These values are in order. If something would be faster but isn't safe, Sylva
prioritizes safety. If something would be more readable but is inconsistent,
Sylva prioritizes consistency. But importantly, we take these conflicts as
drawbacks of the design. If Sylva becomes too unreadable in the service of
consistency, we revisit the design to rebalance.

\* _Unless you use the [FFI](cffi.html)_
