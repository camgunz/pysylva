# Sylva

Sylva is an applications programming language; it is built for writing
applications like IRC servers or login daemons.

## Hello

```sylva
mod main

req sys

range Age 0u8..250u8

struct Person {
  name: *str(""),
  age: Age(0u8),
}

fn print_usage(msg: String) {
  sys.die("{msg}\nUsage: hello [name] [age]")
}

fn have_birthday(person: &Person!) {
  return (person.age + Age(1u8)).ok_or_die(
    "Person {person.name} is already the max age {person.age}"
  )
}

fn greet_person(person: &Person) {
  sys.echo("Hello {person.name}! You are {person.age} years old.")
}

fn main() {
  let name: (sys.args.get(1)).on_fail(print_usage)
  let age_as_string: (sys.args.get(2)).on_fail(print_usage)
  let age: Age.parse_from_string(age_as_string).on_fail(print_usage)
  let person: Person{name: name, age: age}

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
and does not use garbage collection.

Sylva is pragmatic and unopinionated. Taste and style count, but Sylva is a
tool, and practitioners are free to use Sylva in whatever style and for
whatever purpose they choose.

Sylva is small (but not too small). The language fits in your head, and its
mental models are consistent and broadly applicable.

Sylva is readable. We pay careful attention to how the syntax and organization
scan, as well as to how constructs draw focus and concepts shape thought.

Lastly, Sylva should be familiar to most programmers.  Where possible, it
defers to what the programmer is likely to already know.

These values are in order. If something would be faster but isn't safe, Sylva
prioritizes safety. If something would be more readable but is inconsistent,
Sylva prioritizes consistency. But importantly, we take these conflicts as
drawbacks of the design. If Sylva becomes too unreadable in the service of
consistency, we revisit the design to rebalance.

\* _Unless you use the [FFI](cffi.html)_
