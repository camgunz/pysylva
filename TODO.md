# To Do

* Figure out name mangling
  * This is important so that we can lookup parameterized types without having
    to store them separately from each other
* Figure out automatically adding impls to monomorphizations
  * I think doing this through `implementation_builders` makes the most sense
- Figure out registering monomorphizations in the module
  - We should just never be constructing types in ast-land, then we can do it
    manually in `module_builder`
- Fix `emit_attribute_lookup` to look through impls also
- Add `Lookup` expr
- Add an `element_count` specifier to a `str`:
  - `struct Person { name: str(8)(""), age: u8(0) }`

## Sized types

There's a conflict between "must specify the size of a(n) array/string value"
and "can't possibly specify every length for a(n) array/string parameter".
We're smoothing this over with interfaces.

## Language

### `str`

- Add an `element_count` specifier:
  - `struct Person { name: str(8)(""), age: u8(0) }`

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
