# Parallelism

*Requirement: must have ownership over its parameters, unless they're scalars*

Some ideas:

- Specifically parallel functions
- Keyword (thread, go, run)
- Data structure (`thrd_t` in C11)

```sylva
mod main

struct Thread(data_type) {
  data: *data_type,
  func: fn (d: &data_type!)
}

impl Thread(data_type) {
  fn run(self: &Thread(data_type)!) {
    self.func(&self.data!)
  }

  fn join() {
  }
}

fn main() {
  let p: *Person{"Charlie", 38}
  let t: *Thread(Person){
    data: *p, # p is gone
    func: (p: &Person!) { sys.echo("${p.name}") }
  }

  t.run() # Auto exclusive reference
  t.join()
}
```

TBH I think a thin shim over C11 threading is fine.
