# Reflection

Sylva implements a small set of reflection attributes and methods. These are
distinguished from normal attribute access by the use of `::` instead of `.`.


## (Runtime) values

* `type`: returns the type of the value
* `bytes`: returns a `&[i8 * value::type.size]`, the bytes of the value
