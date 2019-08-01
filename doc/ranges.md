# Ranges

A range is a bounded numeric type:

```sylva
range piano_key(0u8, 87u8)
```

They're usable as types:

```sylva
fn play_key(key: piano_key) {
  midi.play_note(key) # Let's just say this is how it works.
}

fn main() {
  play_key(piano_key(3))
}
```

They also allow the programmer to avoid catching indexing errors:

```sylva
fn main() {
  val keys: [piano_key * piano_key.max]
  echo("18th key: {keys[piano_key(17)]}")
}
```
