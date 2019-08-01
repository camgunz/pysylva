# Basics

Sylva should seem familiar to anyone experienced with mainstream programming
languages:

```sylva
fn main() {
  echo("Hello, world!");
}
```

Something a little more engineered:

```sylva
extern sys

interface Greeter(name: str) {
  fntype greet(self: &Greeter, name: str)

  fn get_greeter_name(self: &Greeter): str {
    return self.name
  }
}

struct Person {
  name: str("")
}

array People [Person * 2]

array Responses [str * 2]

implementation (Person: Greeter) {
  fn greet(self: &Person, name: str) {
    sys.echo("Hey {name}, I'm {self.name}.  Pleased to meet you!")
  }
}

fn print_usage() {
  echo("Usage: greet [ greeter_name ] [ greetee_name ]")
}

fn perform_greeting(greeter: &Greeter, greetee_name: str): str {
  greeter.greet(greetee_name)
  return "Greeter {greeter.get_name()} greeted successfully"
}

fn main() {
  with (greeter_name1: sys.argv[1],
        greeter_name2: sys.argv[2],
        greetee_name: sys.argv[3]) {
    val greeters: People[Person{greeter_name1}, Person{greeter_name2}]
    val responses: Responses[
        greeters[0].greet(greetee_name),
        greeters[1].greet(greetee_name)
    ]
    echo("Response1: {responses[0]}")
    echo("Response2: {responses[1]}")
  }
  else {
    print_usage()
  }
}
```
