# Iteration

Should there be an "iterator protocol"? I mean, an iterator protocol that `for`
uses? I guess... yes? `range` could be understood as implementing it. I guess
what we want is something like:
- Iterate over all no matter what
- Iterate and maybe quit early
- All of those also with the index

The tension here is like, if you're gonna do all the implementation yourself,
what do you need a built-in statement for? Can't you just call like
`.get_iterator()` and `.get_next()` yourself inside of `loop` or w/e?

Yeah it looks good. OK I think we cracked it.

```sylva
struct Unit {}

variant IterationResult {
  OK: @return_type
  Done: Unit({})
}

iface Iterator(index_type, return_type) {
  fn get_next(self: &Iterator!): IterationResult(@return_type)

  fn all(self: &Iterator!, handle: fn (val: @return_type)) {
    loop {
      match (self.get_next()) {
        case (next: OK) {
          handle(&next)
        }
        case (done: Done) {
          break
        }
      }
    }
  }

  fn each(self: &Iterator!, handle: fn (val: @return_type): bool) {
    loop {
      match (self.get_next()) {
        case (next: OK) {
          let should_continue: handle(&next)

          if (!should_continue) {
            break
          }
        }
        case (done: Done) {
          break
        }
      }
    }
  }

  fn all_index(self: &Iterator!, handle: fn (index: @index_type, val: @return_type)) {
    loop {
      match (self.get_next()) {
        case (next: OK) {
          handle(self.get_current_index(), &next)
          self.increment_index()
        }
        case (done: Done) {
          break
        }
      }
    }
  }

  fn each_index(self: &Iterator!, handle: fn (index: @index_type, val: @return_type): bool) {
    loop {
      match (self.get_next()) {
        case (next: OK) {
          let should_continue: handle(self.get_current_index(), &next)

          self.increment_index()

          if (!should_continue) {
            break
          }
        }
        case (done: Done) {
          break
        }
      }
    }
  }

}

struct ArrayIterator(element_type, index_type) {
  data: &array[@element_type * @element_count]!,
  index: @index_type,
}

fn main() {
  let nums: [u8 * 4][0u8, 1u8, 2u8, 3u8]
  let num_iterator = ArrayIterator(nums::element_type, nums::indices)
}

impl Iterator(ArrayIterator) {
  fn get_next(self: &ArrayIterator!): IterationResult(@return_type) {
    if (self.index >= self.data::type.indices.max) {
      return IterationResult.Done()
    }

    let next_value: self.data[self.index]
    self.index++

    return IterationResult.OK(next_value)
  }
}

struct Iterator(indexable_type) {
  values: &Indexable!,
  index: Indexable::indices(0),
}

impl Iterable(Iterator) {
  fn get_next(self: &Iterator!): Iteration(Iterator.get_type_param("return_type")) {
    if (self.index == self.values::type.indices.max) {
      return Iteration(Iterator.type_params.get("return_type")).Done()
    }

    let value: &Iteration(Iterator.type_params.get("return_type")).OK(
      &self.values[self.index]
    )

    self.index++

    return value
  }

  fn get_next_ex(self: &Iterator!): ExIteration(Iterator.type_params.get("return_type")) {
    if (self.index == self.values::type.indices.max) {
      return ExIteration(Iterator.type_params.get("return_type")).Done()
    }

    let value: &ExIteration(Iterator.type_params.get("return_type")).OK(
      &self.values[self.index]!
    )

    self.index++

    return value
  }
}

struct ExIterator(indexable_type) {
  values: &Indexable!,
  index: uint(0),
}

impl Iterable(ExIterator) {
  fn get_next(self: &ExIterator!): Iteration(ExIterator.type_params.get("return_type")) {
    if (self.index == self.values::type.indices.max) {
      return Iteration(ExIterator.type_params.get("return_type")).Done()
    }

    let value: &Iteration(ExIterator.type_params.get("return_type")).OK(
      &self.values[self.index]
    )

    self.index++

    return value
  }

  fn get_next_ex(self: &ExIterator!): ExIteration(ExIterator.type_params.get("return_type")) {
    if (self.index == self.values::type.indices.max) {
      return ExIteration(ExIterator.type_params.get("return_type")).Done()
    }

    let value: &ExIteration(ExIterator.type_params.get("return_type")).OK(
      &self.values[self.index]!
    )

    self.index++

    return value
  }
}

struct Person {
  name: str,
  age: u8,
}

array Triumverate [Person * 3]
dynarray Agents [Person...]

fn main() {
  let dems: Triumverate[
    Person{name: "Barack Obama", age: 61u8},
    Person{name: "Hillary Clinton", age: 75u8},
    Person{name: "Joe Biden", age: 79u8},
  ]
  let agents: Agents[
    Person{name: "Smith", age: 0u8},
    Person{name: "Smith", age: 0u8},
    Person{name: "Smith", age: 0u8},
    Person{name: "Smith", age: 0u8},
    Person{name: "Smith", age: 0u8},
  ]
  let dem_iter: Iterator(Person){values: &dems}
  let agent_iter: ExIterator(Person){values: &agents!}

  dem_iter.each_ex(fn(index: uint, value: &Person): bool {
    value.age++
    sys.echo("{value.name} is {value.age} years old")
    return true
  })

  for (&person!: dems) {
    person.age++
    sys.echo("{person.name} is {person.age} years old")
  }

  agent_iter.each(fn(index: uint, value: &Person): bool {
    sys.echo("{value.name} is {value.age} years old")
    return true
  })

  for (&agent: agents) {
    sys.echo("{agent.name} is {agent.age} years old")
  }
}
```

---


How to let the programmer implement iteration:

- Operator overloading
  - Hard, because while we can use sigils in `for` to indicate what kind of
    return type we want, we can't do the same for `+` and such.

```sylva
fn make_person(name: str, age: u8): Person {
  return Person{name, age}
}

fn main() {
  let p: make_person("Charlie", 38u8) # On the stack
  let *p2: *make_person("Charlie", 38u8) # What
}
```

And here you can't apply the "sigils tell you what you get" rule like `case`
and what-not, because `make_person` might do something with that person it can
only do with a pointer. Though... what would that be?

- Interfaces
  - Hard, because we don't have `yield` and have to use functions
  - I guess... unless the iterator itself maintains some kind of state.
  - So `for (x: xarray)` gets an iterator from xarray. This means that xarray
    implements... ._iter that returns something that has a .get_next(_ex)
    method
    - Generally I think this sucks becuase you need some kind of allocation
    - Kind of feeling more and more like returning aggregate values is becoming
      real important--"allocate this on my stack" is pretty nice
    - Actually, I wonder if this is a useful pattern:
      - Undecorated: allocated on caller's stack
      - (Ex)Ref: return a ref
      - Pointer: return a pointer
      Then... you match them up? idk what if they don't match, some magical
      things happen?

Broadly, I'm starting to be unsatisfied with memory management infiltrating
every API. Suddenly you need value/(ex)ref/pointer versions of everything, but
it doesn't always apply, and it's annoying.

In C you get around this by carefully determind what might allocate, and then
using return parameters. So like, implementing operator overloading in C uses
return parameters--or other numeric libraries like MPFR and GMP.

But Sylva has this problem where sigils have to match or something. So:

You can't just say
