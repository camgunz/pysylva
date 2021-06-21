# Allocation

Allocation is platform-dependent, and requires platform-level support. However,
as it's so common, Sylva provides some shorthand syntax in the form of `*`:

```sylva
requirement sys

struct Person {
  name: str
  age: u8
}

array People[Person]

fn long_way() {
  var barack: sys.alloc(Person::size)
    .on_success(fn (mem: MemoryBlock) {
      mem.init(Person)(Person{name: "Barack", age: 57})
    })
    .on_failure(fn (f: Failure) {
      sys.die("Allocating memory failed: {f.message}")
    })
    .value

  var obamas: sys.alloc(Person::size)
    .on_success(fn (mem: MemoryBlock) {
      mem.init(Person[2])([
        Person{name: "Barack", age: 57},
        Person{name: "Michelle", age: 56},
      ])
    })
    .on_failure(fn (f: Failure) {
      sys.die("Allocating memory failed: {f.message}")
    })
    .value
}

fn short_way() {
  var barack: *Person{name: "Barack", age: 57}
  var obamas: *People[2][
    Person{name: "Barack", age: 57},
    Person{name: "Michelle", age: 56},
  ]
}
```

Conveniently, the `*` shorthand also corresponds with the signifier for an
owned pointer, which makes it even easier to separate the different reference
types.
