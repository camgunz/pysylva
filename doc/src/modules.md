# Modules

Modules are the top-level building block of Sylva code.  Sylva can optionally
generate module description files.  If you are shipping a library, these are
necessary.

```sylva
mod pets

variant Pet {
  Cat: {
    name: str,
  },
  Dog: {
    name: str,
  },
}

mod vehicles

struct Car {
  make: str,
  model: str,
}

mod vehicles.badass

struct Motorcycle {
  make: str,
  model: str,
}
```

Multiple modules can exist in a single file, and modules can exist across
files. This allows the programmer to organize code as they see fit, without
worrying about filesystem-related concerns.

## Submodules

Contrary to their appearance, submodules aren't specifically connected to their
parent module.

```sylva
mod pets

iface Pet {
  greet: fn(): *str
}

mod pets.dog

req pets # `pets.dog` doesn't automatically pull in definitions from `pets`

struct Dog {
  name: *str
}

impl Pet(Dog) {
  greet: fn(self: &Dog): *str {
    return *"Woof!"
  }
}

mod main

req pets.dog # Only pulls in `pets` as a result of the `req` in `pets.dog`

fn main() {
  let dog: pets.dog.Dog{"Rover"}
  dog.greet()
}
```

## Constants

Modules can contain constants:

```sylva

const NAME: "Charlie"

fn main() {
  echo("Hey {NAME}")
}
```

## Clashes

It's possible to do something like:

```sylva

mod objects.fruits.apple

struct Seed {
  poisonous: bool
}

mod objects.fruits.apple.Seed

```

This causes a namespace clash and "objects.fruits.apple.Seed" is now ambiguous;
the identifier `objects.fruits.apple.Seed` may refer to both the struct and the
module.

Sylva simply won't allow this; compilation will fail should it occur.
