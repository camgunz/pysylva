# Notes

## Decisions

- `$Dynarray` is a builtin type, but not a base type.

## Objects and Schemas

Everything is an "object", insofar as "object" means "thing".  Objects have
schemas that define their structure, and there are 16 basic varieties:

- `$Void`
- `$Token`
- `$Expression`
- `$Value`
- `$Boolean`
- `$Rune`
- `$String`
- `$Decimal`
- `$Float`
- `$Integer`
- `$Array`
- `$Tuple`
- `$Struct`
- `$Map`
- `$Code`
- `$Function`

## Void

`$Void`'s schema is `()`.  It has no fields and no size.  In some ways it is
atomic, but lacks a value.  It can be constructed using either `$Void()`.

## Atomics

`$Value`, `$Boolean`, `$Rune`, `$String`, `$Decimal`, `$Float`, and `$Integer`
are **atomics**: they cannot be further divided.  Other languages refer to them
as scalars -- but strings don't always qualify as scalars depending upon their
implementation, so "atomic" (in the Lisp tradition) is perhaps more apt.

It might be helpful to think of atomics as objects that are their own schema.

### Creating Atomic Objects

This is straightforward:

```sylva
true
$Boolean(true)
```

The first (`true`) is a boolean literal expression.  This always evaluates to
that object.  The second is a call expression, which fully expands to:

```sylva
$Call(
    function: $Lookup(
        variable_name: "$Boolean"
    ),
    arguments: (
        value: true
    )
)
```

Of course, `value` in the above expression remains `true`.  Because these
definitions are circular, we need a break rule.  That rule is "literal
expressions always evaluate to their ultimate value", that is, they don't
require the full instantiation process with the `$Call` and so on.

The full set of atomic literals is:

- `$Value`: `person`
- `$Boolean`: `true`
- `$Rune`: `'a'`
- `$String`: `"Hello, World!"`
- `$Decimal`: `35`
- `$Float`: `35f32`
- `$Integer`: `35u8`

## Higher-Order Types

`$Array`, `$Tuple`, `$Struct`, `$Map`, `$Code`, and `$Function` are
higher-order types -- types comprising other types as it were.

`$Array` is a list type: a list of elements which are other objects, and the
element types are homogeneous.

`$Tuple` is also a list type, but its element types can be heterogeneous.

`$Struct` is a composite type: it maps field names to field values.  `$Struct`
accepts only `$Value` as its field name type

`$Map` is also a composite type.  Its field names as well as values can be of
any type, but they must be homogenous (i.e. all the names must have the same
type, and all the values must have the same type, but the name and value type
may differ).

### Constructors

- `$Array`: `$Array(element_type: $Rune, element_count: 5)`
- `$Tuple`: `$Tuple(element_types: [$Object])`
- `$Struct`: `$Struct(fields: [(name, $String), (age, $Integer)])`
- `$Map`: `$Map(field_name_type: $String, field_value_type: $Integer)`

These are literal constructors:

- `$Array`: `['a', 'e', 'i', 'o', 'u']`
- `$Tuple`: `("Charlie", 35)`
- `$Struct`: `(name: "Charlie", age: 35)`
- `$Map`: `["moons": 173, "planets": 8, "stars": 1]`

### Schemas

We generally refer to these higher order types as "schemas", because their
constructors yield new types.  That is, the literal `[$Rune * 5]` creates a new
type of `$Array` where its `element_type` is `$Rune` and its `element_count` is
`5`.  These new types can be used anywhere types are normally accepted:
function signatures, struct definitions, etc.

Ex:

```sylva
$Def(
    name: "$3DPoint",
    value: `(x: $Decimal, y: $Decimal, z: $Decimal)`
)

$Def(
    name: "$Origin",
    value: "$3DPoint(0, 0, 0)"
)
```

The type of `$Origin` is `$3DPoint`; the type of `$3DPoint` is
`($Decimal, $Decimal, $Decimal)`, also expressable as
`$Struct(field_names: [$Value(x), $Value(y), $Value(z)], field_types: [$Decimal, $Decimal, $Decimal])`,
whose type is `$Struct`.

The literals construct new anonymous types, and then instantiate them with the
specified values.

### Value Types

But indeed schemas aren't limited to types comprising types.  While not very
practical, here's an example:

```sylva
def arr: 'r'
def too: '2'
def dee: 'd'

def print_anything_as_long_as_its_arr: fn(anything: arr) {
    print(arr)
}
```

Values are themselves types.

## Functions vs. Types

So I want types to be callable, so that `$Boolean(<expr>)` yields a value whose type is `$Boolean`.  But this doesn't seem reasonable.  How would you define a
function named after a type that returns that type?

Maybe it's a semantic problem.  There are... callables.  Type is callable.

## Extending The Type System

```
$Def(
    name: "$PersonStruct",
    value: $Struct(name: $String, age: $Number),
)
```

## Working...

Struct options:
  - A struct is an array of unknown size, where the elements are each 2-tuples
    of schema `($Value, $Object)`
    - but we don't have tuples
    - don't have "array of unknown size"
  - A struct is a struct with two arrays: one for field names and one for field
    values
    - Arrays cannot contain elements of disparate types, which is a problem for
      field values

```
> ['a', 'b', 'c']::schema
(element_type: $Rune, element_count: $Integer::range(min: 0)) # $Struct

> ['a', 'b', 'c']::schema::schema
[[$Object * 2]]

> true::schema
$Boolean

> true::schema::schema
$Boolean

> (name: "Charlie", age: 35)::schema
(field_names: [$Value * 2], field_values: [

```

### Schemas in the C structs

The definition of an Object is:

```c
typedef struct ObjectStruct {
  Location location;
  BaseSchema base_schema;
  struct ObjectStruct *schema;
  union {
    gchar *value;
    gboolean boolean;
    gunichar rune;
    gchar *string;
    Number number;
    Array array;
    Tuple tuple;
    Struct structt;
    Module module;
    Function function;
  } as;
} Object;
```

But what does it mean to have a `schema`?  Well, it depends.

If you're a scalar, then your schema can be an instance of you with a value.
This is how we would represent, for example, a schema that is always the number
14.

If you're not a scalar, then the `schema` field sets up dependent types (in a
kind of inverse way).  You could create a "NumberArray" by creating an `$Array`
whose schema is `(element_type: $Number)`.  Or, you can create a pair by
creating a `$Tuple` whose schema is `(element_types: [$Object, $Object])`.

### Types and Components

A type is also a schema.  A type associates together:
  - a schema
  - constructors
  - components
  - methods

A component is also a schema.  A component defines:
  - required schema attribute names and types (as a struct)
  - methods

The thing about both of these is that they won't have access to the overall
type.  In the type's case, it's not done being defined.  I suppose we could add
some semantics, something like "incremental definition", but that feels too
impure.  On the other hand, we essentially _need_ that for macros... so maybe
that is in fact the thing here.

What if `self` always refers to the top-level thing being built, and `this`
always refers to the immediate scope.  So if you're in an `if` block, `self`
refers to the function, type, or component you're building, and `this` would
refer to the `if` block itself.

That works OK, but taking the explicit `self` out of function signatures, we no
longer know if we need a mutable reference to `self`.

OK say we nix `self` and use `::<thing>` instead.  So this is what a method
would look like:

```sylva
$Def(Person, $Type(
  schema: (name: str(""), age: uint(0)),
  methods: (
    have_birthday: fn(self: &::schema!, name: str) {
      self.age++
    }
  )
))
```

I can live with that, providing macros fix it.

Components:

```sylva
$Def(Greeter, $Component(
  schema: (name: str),
  methods: (
    greet: fn(self: &::schema, name: str) {
      echo("Hello {{name}}, I'm {{self.name}}")
    }
  )
))
```

Same deal re: macros.  And let's punt on `this` for now; not sure if it'd be
good for anything.

### Optional commas

This would be really nice for types/components/etc, and I think the only issue
is arithmetic expressions.  Needs investigation though.

### Iteration

A little unclear on how to define them.

```sylva
deftype Iterator: (
  schema: (schema: object, element_schema: object, state: object),
  methods: (
    __next: fntype(self: &::schema) ::element_schema
  )
)

def HandIterator: Iterator(Hand, &Card, fn(self: 

deftype HandIterator: (
  # HandIterator has a .next() method
  schema: ()
  methods: (
    __next: fn(self: &selftype) selftype.element_schema {
    }
  )
)
```

