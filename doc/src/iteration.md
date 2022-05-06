# Iteration

```sylva
struct Unit {}

variant Iteration(return_type) {
  OK: &return_type
  Done: Unit({})
}

variant ExIteration(return_type) {
  OK: &return_type!
  Done: Unit({})
}

# This syntax, along with `impl` below, doesn't really work because it
# presupposes that whatever implements the interface will have the same number
# and meaning of type params.
iface Iterable(return_type) {
  fn get_next(self: &Iterable!): Iteration(return_type)

  fn get_next_ex(self: &Iterable!): ExIteration(return_type)

  fn each(self: &Iterable!, handle: fn (index: uint, val: &return_type): bool) {
    let index: 0u

    loop {
      match (self.get_next()) {
        case (next: OK) {
          let should_continue: handle(index, &next)

          index++

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

  fn each_ex(self: &Iterable!, handle: fn (index: uint, value: &return_type!): bool) {
    let index: 0u

    loop {
      match (self.get_next()) {
        case (next: OK) {
          let should_continue: handle(index, &next!)

          index++

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

struct Iterator(indexable_type) {
  values: &Indexable!,
  index: Indexable::indices(0),
}

impl Iterable(Iterator) {
  fn get_next(self: &Iterator!): Iteration(Iterator.type_params.get("return_type")) {
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

  agent_iter.each(fn(index: uint, value: &Person): bool {
    sys.echo("{value.name} is {value.age} years old")
    return true
  })
}
```
