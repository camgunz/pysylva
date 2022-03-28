# Allocation

Allocation is platform-dependent, and requires platform-level support. However,
as it's so common Sylva provides `*` as shorthand:

```sylva
req sys

struct Person {
  name: str,
  age: u8,
}

fn long_way() {
  var barack: sys.alloc(Person::size)
    .succeed_or_die()
    .init(Person)(
      Person{name: "Barack", age: 57}
    ).succeed_or_die()
  var obamas: sys.alloc_array(Person::size, 2)
    .succeed_or_die()
    .init([Person * 2])(
      [Person * 2][
        Person{name: "Barack", age: 57},
        Person{name: "Michelle", age: 56},
      ]
    ).succeed_or_die()
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
