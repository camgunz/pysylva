# C FFI

Sylva includes a C foreign function interface. Bindings to C programs can be
generated using:

* `carray`
* `cbitfield`
* `cfn`
* `cfntype`
* `cblockfntype`
* `cptr`
* `cstr`
* `cstruct`
* `cunion`
* `cvoid`

C's scalar types (`int`, `complex`) map to Sylva's scalar types as you'd
expect.

Note well that the C FFI offers none of Sylva's safety guarantees.

## `libc`

We generate bindings to a platform's libc implementations, which generally are
necessary or at least the most convenient ways to interact with the operating
system.
