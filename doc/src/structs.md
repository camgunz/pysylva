# Structs

Structs work as you'd expect:

```sylva
struct Person {
  name: str
  age: u8
}
```

Fields must be specified when creating a struct:

```sylva
struct Person {
  name: str
  age: u8
}

fn main() {
  var joe_biden: Person{"Joe Biden", age: 78u8}
  var charlie_gunyon: Person{name: "Charlie Gunyon", age: 38u8}
}
```

Structs can have default values, which allows us to skip specifying them:

```sylva
struct Person {
  name: str("")
  age: u8(0)
}

fn main() {
  var person: Person{}
}
```

## Parameterized structs (generic data types)

Type parameters can be passed to struct and variant declarations:

```sylva
struct Person(age_type) {
  name: str
  age: age_type
}

struct Result(ok_type, failure_type) {
  variant OK: ok_type
  variant Failure: failure_type
}
```
