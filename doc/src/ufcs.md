# Uniform Function Call Syntax

Sylva supports uniform function call syntax (UFCS):

```sylva
requirement sys

struct Person {
  name: str
}

fn say_hey(person: &Person) {
  sys.echo("Hey!")
}

fn main() {
  var person: Person{name: "Charlie"}
  say_hey(&person)
  person.say_hey()
}
```
