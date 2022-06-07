# Strings

Sylva provides two basic string types, and an interface:

```sylva
mod main

req sys

struct Person {
  name: @str_type,
  age: u8(0),
}

fn print_person_name(name: String) {
  sys.echo("Hello, {name}")
}

fn main() {
  let str_person: Person{"Charlie", 39}
  let string_person: Person{string{}, 39}

  string_person.name.assign_str("Charlie")
}
```

Strings are arrays of bytes that represent a text encoding, configurable at
runtime (defaults to UTF-8).

[TODO] Figure out how to reconcile format strings being super useful, but also
       requiring allocation and therefore being `string`s.
       ...Having thought about it, decomposition is what works here.

- `str`: statically compiled string that we know the length of at compile time
- `string`: struct with `size`, `alloc`, and `data` fields.
- `sslice`: is a struct with `start` and `data` fields

---

Decomposition:
- Is this an interface? But then how does an interned string implement .get_length() and such?

---

Old section:

...or, can think of the strings as arrays but with element_type set to `i8`.

Sylva offers two string types: `str` and `String`.

`str` is similar to scalars in that it can be passed around easily (without
sigils) and indeed cannot be owned.  However, it also cannot be mutated.

`String` is an encoded byte buffer.  The default encoding is UTF-8, but this
can be configured at compile time.  `String` must be passed with sigils, can be
owned, and can be mutated.

Notably, format strings (``Hello {name}``) result in `String`.
- This isn't necessarily required, if `{name}` is constant.

Most of the time you can get away with `str`s.
