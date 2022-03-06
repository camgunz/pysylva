# Allocation

Allocation is platform-dependent, and requires platform-level support. However,
as it's so common Sylva provides `*` as shorthand:

```sylva
req sys

struct Person {
  name: str
  age: u8
}

fn long_way() {
  var barack: sys.alloc(Person::size)
    .on_success(fn (mem: sys.MemoryBlock) {
      mem.init(Person)(Person{name: "Barack", age: 57})
      .on_failure(fn (f: Failure) {
        sys.die("Initializing memory failed: {f.message}")
      })
    })
    .on_failure(fn (f: Failure) {
      sys.die("Allocating memory failed: {f.message}")
    })
    .value

  var obamas: sys.alloc_array(Person::size, 2)
    .on_success(fn (mem: MemoryBlock) {
      mem.init([Person * 2])([
        Person{name: "Barack", age: 57},
        Person{name: "Michelle", age: 56},
      ])
      .on_failure(fn (f: Failure) {
        sys.die("Initializing memory failed: {f.message}")
      })
    })
    .on_failure(fn (f: Failure) {
      sys.die("Allocating memory failed: {f.message}")
    })
    .value
}

fn short_way() {
  var barack: *Person{name: "Barack", age: 57}
  var obamas: *[
    Person{name: "Barack", age: 57},
    Person{name: "Michelle", age: 56},
  ]
}
```

The `*` shorthand also corresponds with the signifier for an owned pointer,
which makes it even easier to separate the different reference types.
