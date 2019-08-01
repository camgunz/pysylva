# Modules

Modules are the top-level building block of Sylva code.  Sylva can optionally
generate module description files.  If you are shipping a library, these are
necessary.

## Clashes

It's possible to do something like:

```sylva

module "objects.fruits.apple"

struct Seed {
  poisonous: bool
}

module "objects.fruits.apple.Seed"

```

This causes a namespace clash and "objects.fruits.apple.Seed" is now ambiguous:
does "objects.fruits.apple.Seed" refer to the struct or the module?

Sylva simply won't allow this; compilation will fail should it occur.
