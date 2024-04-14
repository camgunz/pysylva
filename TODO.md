# To Do

## General

- Monomorphizations should be unique by params/return type
  - `StrType` does this, but basically the base types need to look up a type
    in the module before building a new one, and if they build a new one they
    need to register it in the module

## C Code Gen

- Emit `impl` functions
  - I think this is just walking `SylvaType`'s `impls` attribute

- Emit refs to `impl` functions as the C name


## Misc

- We will not monomorphize functions based on interfaces as an optimization
  - Weird property access and reflection (e.g. unclear what `::bytes` returns,
    etc.)

## Can we toss interfaces?

No. Interfaces:

- let the programmer extend anything (scalar, struct, variant, etc)
  - Doesn't a generic function also let you do this?
    - Nah, not really, because you don't really have the freedom to handle
      whatever weirdo type you might pass.
- don't require an internal tag, and therefore can be preferable to variants
  even though they (probably) require a deref,

---

Original thought process:

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

fn print(s: $str_type) {
  libc.write(libc.STDOUT_FILENO, cptr(cvoid(s.get_bytes())), msg.get_length())
}
```

What are interfaces good for?

Interfaces are nice as contracts. Here we definitely know what a `String` is,
and the compiler can use that as the constraints on anything calling `print`:
gotta implement `String`. Otherwise we have to read `print` and know that
anything calling it has to implement `get_bytes(): &[u8...]` and `get_length():
uint`. You can also avoid monomorphization if you specify an interface.

This is a nominal vs. structural question. The downside of interfaces is naming
and defining the `iface`; the downside of generic functions is you could
accidentally implement enough methods to safely pass something to a function
you didn't want to.
- The deciding factor is do you want to use interfaces to filter out what you
  can pass to a function, or do you want to use generic functions to widen what
  you can pass to a function. I think our aim here is the latter.
  - Also we could do something else for the former, like a union type specifier
    - Good use of `typedef`??

Editing things post hoc also feels the same: if you change a signature you
gotta think deep about everything around it, whether that's an interface or
not.

I guess you could remove a method from say `Person`, and it might be hard to
find everything that passes a `Person` to a function that expects that method
with string-y tools like `grep`.
- Nah, just look for `.have_birthday` or whatever. If your codebase is too big
  for this to really work you're using a language server anyway.

Organizing things in your mind is a little odd though.

Or thinking about it the other way, why do we need generic functions when we
have interfaces?
- generic functions use monomorphizations to avoid vtables and pointer derefs
  - I suppose this also means we can enable working on things in registers
- No need to name every abstracted bundle of behavior (structural

OK. My feelings are:

- `impl` is still useful, and we won't be able to remove it by removing `iface`
- removing `iface` would be a win
- it's a little unclear what the implementation difficulties are for either,
  but I think they're the same
- there's a question of facilitating dynamic dispatch with interfaces to avoid
  monomorphization size blow ups
- I can't shake the idea that having to name everything is kind of a pain
- Big downside of interfaces is that you don't get property access
- Seems like interfaces support heterogeneous collections, but in practice I
  think they're probably not useful because they have to use
  lowest-common-denominator methods as we don't have an unsafe cast or RTTI.

Wins:
- (if) heterogeneous collections
  - What's the difference here between an interface and a variant?
    - An interface requires a deref 
    - A variant requires a tag
    - Anything can implement an interface
      - scalar (int, rune)
      - struct
      - variant
- (if) facilitating dynamic dispatch
- (fp) not naming everything
- (fp) facilitating property access

So, it looks like this is mostly all in favor of parameteric polymorphization
in functions.

Combined with inference though, I think the only place you'd need `<>` in code
is when you're assigning things statically.

There's never any reason to use parameterized struct/variant literals: you have
to use them immediately (can't bind new struct/variant types) so you know what
you're binding within them.

There _is_ a reason to support parameterized function literals: you're
assigning function pointers. You can bind new function types.

## Explicitly monomorphize w/ `typedef`

```sylva
variant Result {
    OK: $ok,
    Fail: $fail
}

typedef StrErrResult: Result($ok, String)
```

```sylva
fn gen_add(x: $num_type, y: $num_type): $num_type {
    return x + y
}

typedef int_add: gen_add($num_type: int)
```

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
