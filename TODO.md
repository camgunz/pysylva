# To Do

## General

- Pointer types need to pass Attribute/Reflection calls to their
  `referenced_type`
- Unclear what to do about ::type and ::bytes for interfaces
  - I think it's fair that these are mostly not useful. ::type will give you
    the interface and ::bytes will give you the bytes of the pointer.
    - It won't always be a pointer though, will it?
  - This means `String` needs something like a `to_bytes` function so `sys`
    funcs using `String` can use it
- Add an "interned string" type.
  - Consider double quotes for interned strings and backquotes for everything
    else (templates, etc.)

## Generics, Functions, Interfaces, Structs, Variants, etc.

- Really don't like `<>`; it makes parsing expressions pretty hard, and it's
  hard to read.
  - But, it's what most people will be familiar with.
- When definining new functions/structs/variants as literals, we'll sometimes
  have to explicitly parameterize. Right now that's done with `()`, but
  double-parens in function call expressions aren't wonderful.
  - This is actually pretty common: `Result` and function pointers for two.
- When defining new functions/structs/variants not as literals:
  - We currently use `()` after the binding name.
  - We _could_ use `@` at the params instead.
    - Ideally this would be consistent with literals, but this wouldn't be,
      and I haven't figured out a way to do that without implicitly
      monomorphizing everywhere (which might be OK).
    - This actually saves a lot of space

OK, I think this means:
- Definitions and literals use `@` for type parameters
- Type parameterization uses `()`
  - You only need this in type-land, i.e. `Result(i32)`
- Expressions use inference
- We will not monomorphize functions based on interfaces as an optimization
  - Weird property access and reflection (e.g. unclear what `::bytes` returns,
    etc.)

## Interfaces

OK thinking about:

```sylva
iface String {
  fn get_bytes(): *[u8...]
  fn get_length(): uint
}

impl String(str) {
  fn get_bytes(self: &str): *[u8...] {
    let dynbytes = *[u8...]

    dynbytes.read_array(self::bytes) # [TODO]

    return dynbytes
  }

  fn get_length(self: &str): uint {
    return self.element_count
  }
}

fn print(s: &String) {
  libc.write(libc.STDOUT_FILENO, cptr(cvoid(s.get_bytes())), s.get_length())
}
```

What if it were:

```sylva
impl str {
  fn get_bytes(self: &str): *[u8...] {
    let dynbytes = *[u8...]

    dynbytes.read_array(self::bytes) # [TODO]

    return dynbytes
  }

  fn get_length(self: &str): uint {
    return self.element_count
  }
}

fn print(str_type)(s: str_type) {
  libc.write(libc.STDOUT_FILENO, cptr(cvoid(s.get_bytes())), msg.get_length())
}
```

As planned right now, there isn't a difference to the compiler. That it, these
are two ways of expressing the same thing.

So what are interfaces good for? Or thinking about it the other way, why do we
need generic functions when we have interfaces?

Interfaces are nice as contracts. Here we definitely know what a `String` is,
and the compiler can use that as the constraints on anything calling `print`:
gotta implement `String`. Otherwise we have to read `print` and know that
anything calling it has to implement `get_bytes(): &[u8...]` and `get_length():
uint`.

I guess this is a nominal vs. structural problem? Not really though, as we
require an `impl` in either case. The only extra work is definining the
`iface`, which is probably 50/50 on "nice as documentation" vs. "annoying to
name everything".

Editing things post hoc also feels the same: if you change a signature you
gotta think deep about everything around it, whether that's an interface or
not.

Organizing things in your mind is a little odd though.

Another tradeoff is that the double paren thing isn't wonderful, but conversely
having to name everything isn't wonderful either.

OK. My feelings are:

- `impl` is still useful, and we won't be able to remove it by removing `iface`
- would be _very_ nice to remove double parens in function calls
- removing `iface` would be a win
- function type parameters _might_ be parameterizable using a different sigil,
  perhaps `@`
- it's a little unclear what the implementation difficulties are for either,
  but I think they're the same
- there's a question of facilitating dynamic dispatch if you really want it
  (size considerations)
- I can't shake the idea that having to name everything is kind of a pain
- Big downside of interfaces is that you don't get property access
- Big upside of interfaces are heterogeneous collections
  - Do we actually support this though? Can we have `&[*String * 10]`?
    - This works if the "vtable" is attached to the "object"

Wins:
- (if) heterogeneous collections
  - What's the difference here between an interface and a variant?
    - a variant can't be extended
- (if) (potentially) facilitating dynamic dispatch
  - This feels like a compile-time option, not a program logic option
- (fp) not naming everything
- (fp) facilitating property access
  - This is barely a win, most of the time it won't work

So, it looks like this is mostly all in favor of parameteric polymorphization
in functions, and trying to make `<>` work.

Combined with inference though, I think the only place you'd need `<>` in code
is when you're assigning things statically.

There's never any reason to use parameterized struct/variant literals: you have
to use them immediately (can't bind new struct/variant types) so you know what
you're binding within them.

There _is_ a reason to support parameterized function literals: you're
assigning function pointers. You can bind new function types.

## Sized types

There's a conflict between "must specify the size of a(n) array/string value"
and "can't possibly specify every length for a(n) array/string parameter".
We're smoothing this over with interfaces.

## Language

### `str`

- Add an `element_count` specifier in the docs:
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
