# Strings


[TODO] Figure out how to reconcile format strings being super useful, but also
       requiring allocation and therefore being `string`s.
       ...Having thought about it, decomposition is what works here.

- `str`: statically compiled string that we know the length of at compile time
- `string`: struct with `size`, `alloc`, and `data` fields.
- `sslice`: is a struct with `start` and `data` fields

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
