# To Do

## Language

### Iteration

[TODO] haha

### Returning a reference

Returning a reference violates memscopes. References are pinned to the function
in which they're created.

This seems wrong though? They should actually be pinned to the memscope of what
they reference. But functions don't know the memscope of their arguments, they
only set requirements (param a's memscope > param b's memscope because I write
a to b). So a function couldn't say "oh I know the memscope of `self`,
therefore my requirement is that the reference I return has the same memscope
as `self`.

But can't this still be defined? At the call site, we know the memscope of what
we're calling a function with. So the function can set scope requirements on
the return value as well as its parameters.

But this is pretty different, because there might be other information. Like if
I'm returning a reference from a deeply-embedded value in a struct:

```sylva
struct Person {
  name: str(""),
  age: u8(0),
}

struct HouseHold {
  people: [*Person * 3], # [TODO] Something about pointers to incomplete arrays
}

# This function looks into a household and returns a reference to one of its
# people.
# ...is there any way that a returned reference's value's memscope would ever
# be above its parameters? I think not right? So basically Sylva guarantees
# that no ref returned by a function will ever be higher in memscope than its
# parameters.
#
# But that's different than saying the ref won't be higher than a _specific_
# parameter. In this case, the return value can't be higher than `hh`, and
# the only we know about that restriction is the `return` line.
fn get_person_ref(hh: &HouseHold, p: &Person): &Person {
  # Here, Sylva has to see that `&hh.people[0]` is the return value
  return &hh.people[0]
}

fn populate_household_and_get_person_ref(hh: &HouseHold!): &Person {
  let p: *Person{}
  let p2: Person{}

  hh.people.append(*p)

  # (true) Requires that p3 is <= hh and p2
  let p3: get_person_ref(hh, &p2)

  return p3
}

fn main() {
  let hh: HouseHold{}
  # (true) requires that `p` is <= hh
  let p: populate_household_and_get_person_ref(&hh!)
}
```

### Allocation

I'm having a little trouble w/ doing things in `sys.alloc` and
`sys.alloc_with_values` for a couple reasons:

- Feels like allocation is part of the language.
  - the syntax sugar (`*`) for allocation in particular
-

OK some nice things about `sys.alloc` and friends:
- No need for runtime support
- Can just not `req libc`
- Means you can easily and clearly not allocate
  - You can't move a ref or a stack value, so how useful is this really?
- No need for some kind of `--no-alloc` flag or w/e
- Option to use different allocators

Some downsides:

- The compiler still depends on `libc` if you ever heap allocate. How do we
  manage this? I guess it could be as simple as "It looks like you're trying to
  heap allocate w/o `req libc`. Whoops!"
- Means Sylva can't have any features requiring allocation
  - Template strings are the biggies here.
- `cptr(void)::as` is some magic that blasts a hole in safety, and making it
  available to everyone is probably a bad idea

  Some nice things about building it into the language solely with `*`:
  - Get template strings back
  - `*` is way simpler than a few type param'd functions.
  - Requires less reflection support
    - These are... a good idea mostly anyway though, well it's just `::bytes`,
      `::as` is pretty bad.

  Some downsides:
  - magic is bad
  - ensuring zero allocations requires some kind of tooling
    - This isn't _not_ true for `sys.alloc`, but if you're just not pulling in
      `libc` then that's basically as good as a `--no-alloc` flag. There are
      some gray areas like you're using `libc` but just not `malloc`, etc., but
      w/e.
  - defaults to a runtime, so would require some kind of automatic "oh you
    didn't allocate, we won't link libc" or a manual `--no-alloc` flag
  - Custom allocators need to be configured on a per-project basis and can't be
    mixed in a project.

---

OK well, the "magic is bad" argument doesn't super hold because we're keeping
`*` as syntax sugar no matter what. As for the next two, we're probably
providing some kind of tooling/switch in any case. Finally, I don't care about
mixing multiple allocators. Seems like a good simplification to require
separate projects at that point.

OK it's decided. `*` isn't syntax sugar, it's the `new` operator in assignment.

#### Syntax sugar

How do we know the difference between `Person{}` and `Person{"Charlie", 38}`?

Mainly, the problem is that a struct might not have fields, so it's like, do we
use `alloc` or `alloc_with_values` here?

Well, if it doesn't have fields you can't allocate it. That's easy. So `{}` and
`{.+}` are the determinants of `_with_fields` and the identifier prefix is the
type argument.

Operator-wise though, how does `*` work? If it's a unary operator meaning
"move", idk the whole thing is tricky. Is there an element of "assignment"
here? Not entirely because `*` happens inside of function calls too. I suppose
in some way you're assigning arguments to parameters.

Broadly, `*<thing>` isn't a valid expression. So what does it mean?

- Allocate on the heap (`let`)
  - "Movable"
- Move into this memscope (function call, any kind of assignment)
  - "Move"
- Ownership required (function parameter type)
  - "Moved"

So `*` is more like an annotation.

---

Mainly the problem is initializing without doing any unnecessary copying. You
want to be able to say:

```sylva
fn main() {
  let p: *Person{"Charlie", 38}
}
```

...without having to first make a `Person` on the stack.

Is this sometimes unavoidable (say if `Person` also contains a `struct` or an
owned pointer)?

It seems like if the rvalue is a constant expression, then the values to be
written into the allocated memory can live as constants in the binary. If it
isn't, then evaluation on the stack has to occur.

This is an odd thing to abstract; it feels a little spooky like, oh I added
some addition and now I'm blowing the stack or something.

But this feels like some kind of optimization anyway, where we can look to see
that the rvalue is constant. I guess skipping stack evaluation in this case
isn't a totaly innocent change; in some very niche cases I can see caring about
it... not that we're definining behavior here but still.

So, maybe this is an argument for something like `const_alloc` or whatever?

Could do something like C++'s placement `new`. It's a pretty good analog
because it separates the writing/type definition part from the allocation part,
which it seems like we have to do here.

Speaking of that delineation:

- allocate new memory
  - Might fail to allocate
- write default/specified values
  - might not be enough space
  - what about a `::bytes` read-only reflection attribute on instances?
- define type
  - Need some kind of "trust me, this is a <type>" affordance

Maybe it helps if `cptr(cvoid)` becomes `cptr(i8)`? Not if we just use memcpy I
guess.

### Strings

- `&str`:   `const char *`
- `&str!`:  `char *` (ref)
- `*str`:   `char *` (owned)
- `String`: `StringBuffer`

OK, always use the `&` prefix, because `str` is a aggregate type.

### Add `cnull` type

n.b.

### Deprecate `dec`

Decimals require allocation, and having raw number literals not be integers is
pretty confusing.

### Type params

- Type params should use `<` and `>`. Adheres to the "you already know this"
  principle.
- Ensure it's possible to alias a type-parameterized struct, variant, function,
  and function type

### Create an interface for `sys.print`.

It's super handy to have some kind of default function to pass something to
`sys.print`. It's not super clear what this should be called:
- Stringable
- Printable
- Displayable

I think `Stringable` and `to_string` win here. OK.

Is `Stringable` better than `::string`?
- Yes, because you can override the behavior of a `Stringable`

### String coercion

String coercion feels like a big important thing to figure out. Can we just
define it like Go does? (for ints, and some predefined template for structs,
etc.)

OK we're solving this with interfaces, and since they don't require a deref,
it's very OK.

### UFCS

UFCS doesn't work with modules. You have something like:

```sylva
mod person

struct Person {name: str age: u8}

fn have_birthday(person: &Person!) {
  person.age++
}

mod main

req person

fn main() {
  let p: person.Person{"Charlie", 38}

  person.have_birthday(&p!)
}
```

How would this look with UFCS? How would we know `p.have_birthday` should look
in the `person` module?

#### Fix

I think breaking down and replacing UFCS with some kind of method definition
thing fixes a lot of problems? I like the idea of extending the `impl` block to
not require a type parameter I think. Also, multiple `impl` blocks (w/o type
parameter) are OK as long as they don't dupe fields.

### Error handling

`on_failure` is too painful. You need to know the type of failure you're
dealing with to provide a handler, which can result in a lot of reflection, and
you need some pretty specific knowledge (indexing failures yield an
<array>::IndexFailure or whatever). Plus it's pretty verbose, for basically no
reason, and without string coercion you need a lot of custom error handling
code even just to die.

### Type depth

_Obviated by fixing interfaces_

Sometimes we want to know an aggregate type's internals, like "you're an array
of ints" or "you're an enum of strings". For example, if we could do a partial
type of a `Result`, e.g.:

```sylva
enum ErrorMessages {
  Whoops: "whoops",
  Yikes: "yikes",
}

alias StrErrorResult: Result<?, str | enum(str)>
```

Some shit like this, because you basically want to say "I can get a string out
of this using this one method". This is interfaces, but....

### Interfaces

- It would be cool if interfaces didn't require a deref. I think they don't?

#### Fixes

Replacing UFCS with `impl` solves the scoping problem.

## A potential resolution

I think breaking down and replacing UFCS with some kind of method definition
thing fixes a lot of problems? I like the idea of extending the `impl` block to
not require a type parameter I think. Also, multiple `impl` blocks (w/o type
parameter) are OK as long as they don't dupe fields.

This gets us most of the way to `Result` being able to stringify its error, and
if we don't even allow the error type to be parameterized, i.e.:

```sylva
variant Result<ok_type> {
  OK: ok_type,
  Failure: Stringable
}
```

Yeah see, here this kind of lays bare the semantic problem with using `Result`
for every error: it's super generic. 90% of the time you want `<ok_type,
Stringable>` for your basic "I failed" situation.

But, all that said, if we define string coercion for **everything**, then I
guess I don't really care, and we can continue to answer the type depth
question with "solve it with variants and interfaces".

OK so action items (lol):
- Replace UFCS with "Allow `impl` without a type param to define methods"
  - No "self" (it's not that useful) but error on 1st type not being the main
    type
- Define string coercion for everything

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
