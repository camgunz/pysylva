# C FFI

Sylva includes a C foreign function interface. Bindings to C programs can be
generated using:

* `cfn`
* `cfntype`
* `cptr`
* `cstr`
* `cstruct`
* `cunion`
* `cvoid`

Note well that the C FFI offers none of Sylva's guarantees.

## Builtin types:

- `void`
- `char`
- `signed char`
- `unsigned char`
- `short`
- `unsigned short`
- `int`
- `unsigned int`
- `long`
- `unsigned long`
- `__int128`
- `unsigned __int128`
- `float`
- `double`
- `long double`

## `libc`

We generate bindings to a platform's libc implementations, which generally are
necessary or at least the most convenient ways to interact with the operating
system.
