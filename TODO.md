# To Do

## `lookup_attribute`

Something here about "look at fields, then impls, then fail" or whatever.

## Dynarray

 `dynarray` must be special, we must guarantee its `length` and `capacity`
 members are correct, `[<type>...]` means `dynarray`.

## `str`s

`str`s are odd types. Here's what we know:
- They're literals
- They're syntax sugar for `array`s
  - Their element type is `u8`
- Their size is known at compile time
- Don't want them to be passable as `array`s
  - Unless it's as an interface
- They basically will never be function parameters

There's something here about allowing constants as type parameters. Like, in
this case you could define a `str` enum that just had a bunch of different
element counts:

```sylva
enum str {
  one: [u8 * 1],
  two: [u8 * 2],
  three: [u8 * 3],
  four: [u8 * 4],
  # ...
}
```

The friction here is that `enum`s are constants, so you can't create them on
the fly as needed, and you thus don't get multiple copies.

Generally you don't consider a value as part of a type, but if you want it to
be available at compile time, it has to be. That's why leaving it to be set at
runtime is insufficient.

Fortunately for `str`s they're `array`s, so.

Wait, are we coming out against the `str` type? I think so? The differentiator
is that `str` has to contain encoded string data, which we can't at all enforce
with types.

OK well, I think maybe all this comes out of starting from the wrong place
(function parameters). If we think of `str` as the answer to "what is the type
of a string literal", I think all of our problems go away:
- Encoding is whatever the source file is encoded in (probably bite it and just
say UTF-8 here)
- We always know byte length
- We can add an `element_count` specifier to a `str`:
  - `struct Person { name: str(8)(""), age: u8(0) }`

## Sized types

There's a conflict between "must specify the size of a(n) array/string value"
and "can't possibly specify every length for a(n) array/string parameter".
We're smoothing this over with interfaces.

## Stdlib

- Need an in-compiler interface for `String`
- Need a base `impl String(str)` that has at least `get_length`
- Need a base `impl String(string)` that has at least `get_length`

## Language

### Generics

Generic type parameters have to become part of the type, accessible by methods.
Otherwise syntax becomes pretty difficult.

### Iteration

[TODO] haha

### Returning a reference

### Add `cnull` type

n.b.

### Deprecate `dec`

Decimals require allocation, and having raw number literals not be integers is
pretty confusing.

### Create an interface for `sys.print`.

It's super handy to have some kind of default function to pass something to
`sys.print`. It's not super clear what this should be called:
- Stringable
- Printable
- Displayable

I think `Stringable` and `to_string` win here. OK.

Is `Stringable` better than `::string`?
- Yes, because you can override the behavior of a `Stringable`

### Error handling

`on_failure` is too painful. You need to know the type of failure you're
dealing with to provide a handler, which can result in a lot of reflection, and
you need some pretty specific knowledge (indexing failures yield an
<array>::IndexFailure or whatever). Plus it's pretty verbose, for basically no
reason, and without string coercion you need a lot of custom error handling
code even just to die.

### Interfaces

It would be cool if interfaces didn't require a deref. I think they don't?

### String templates

If we define string coercion for everything, can string templates use const
exprs? No, because const exprs have dynamic stringified sizes.

## Builder

- Module definition files
  - Build a library, get a module definition file back
  - Depend on a library, use the module definition file to build correctly
    - Memscope analysis depends on looking into functions, but we won't always
      have them. How can module definition files notate functions with their
      scoping requirements?

- can't exref a ref
- can't ref an exref
- can't copy an exref
- can't copy an aggregate
- can't copy a pointer

`self[i]`: ImpossibleCopy (could be exref, aggregate, or pointer)
`&self[i]`: Duplicate reference (is an exref)
`&self[i]!`: Duplicate reference (is a ref)
