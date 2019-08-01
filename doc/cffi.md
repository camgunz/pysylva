# C FFI

## Builtin types:

- void
- char
- signed char
- unsigned char
- short
- unsigned short
- int
- unsigned int
- long
- unsigned long
- __int128
- unsigned __int128
- float
- double
- long double

## `libc`

We generate bindings to a platform's libc implementations, which generally are
necessary or at least the most convenient ways to interact with the operating
system.
