# Ranges

While `dec` is Sylva's default numeric type, `range` is the **core** numeric
type, which is a bounded numeric type.  Ranges are far preferable to raw
numbers for a number of reasons:
- they can be thought of as numbers with *units*
- finite ranges make dealing with arrays much easier: if an array is defined
  in terms of a finite range, bounds checks are unnecessary when indexing using
  a value from that range

Ranges inherit the properties from their boundaries.

```sylva
range Health (0rz, 100rz)
```

This defines a range from 0-100, which includes such values as 0, 100, and
99.7849475493457234589345892342934.

which will clamp at 0 and 100, and round to the
nearest number in cases of insufficient precision.  These bounds, together with
rounding and handling of insufficient precision, will help us avoid prodigious
failure handling and wrapping.

```sylva
req random

range Health(0rz, 1000rz)

alias rand_health: random.random(Health)

variant Monster {
  Irukakun: {
    health: Health(100rz),
  },
  Sirotan: {
    health: Health(1000rz),
  },
}

fn get_random_health_value(): Health {
  return rand_health(HealthRange::min, HealthRange::max)
}

fn damage_monster(monster: &Monster!) {
  var base_damage: get_random_health_value()

  match (monster) {
    case (i: Irukakun) {
      # Softie
      i.health -= get_random_health_value() * HealthRange(2rz)
    }
    case (s: Sirotan) {
      # Tough stuff
      s.health -= get_random_health_value() / HealthRange(2rz)
    }
  }
}
```

Without ranges, we have to use `max` and `min` to keep our values within range:

```sylva
req math
req random

alias rand_dec: random.random(dec)

variant Monster {
  Irukakun: {
    health: 100rz,
  },
  Sirotan: {
    health: 1000rz,
  },
}

fn get_random_health_value(): dec {
  return rand_dec(0rz, 100rz)
}

fn damage_monster(monster: &Monster!) {
  var damage: random.random(dec)(0rz, 100rz)

  match (monster) {
    case (i: Irukakun) {
      i.health -= math.min(get_random_health_value() * 2rz, 100rz)
    }
    case (s: Sirotan) {
      s.health -= math.max(get_random_health_value() / 2rz, 100rz)
    }
  }
}
```

## Integer ranges

Integer ranges are particularly useful in that they are discrete. As a result
they may be iterated over, and the programmer can use them to avoid handling
indexing failures:

```sylva
req sys
req midi # Not a real stdlib module

range PianoKey (1u8, 88u8)

struct Keyboard {
  pressed_keys: [bool(false) * PianoKey::count]
}

fn press_key(keyboard: &Keyboard!, key: PianoKey) {
  if (!keyboard.pressed_keys[key]) {
    midi.play_note(key)
    keyboard.pressed_keys[key] = true
  }
}

fn release_key(keyboard: &Keyboard!, key: PianoKey) {
  if (keyboard.pressed_keys[key]) {
    midi.stop_note(key)
    keyboard.pressed_keys[key] = false
  }
}

fn get_key_status(keyboard: &Keyboard, key: PianoKey): str {
  switch (keyboard.pressed_keys[key]) {
    case (true) {
      return "pressed"
    }
    case (false) {
      return "not pressed"
    }
}

fn print_status(keyboard &Keyboard) {
  PianoKey::each(fn (key: PianoKey) {
    sys.echo("Key {key}: {keyboard.get_key_status(key)}")
    return true
  })
}

fn main() {
  var keyboard: Keyboard{}

  keyboard.press_key(PianoKey(3))
  keyboard.release_key(PianoKey(3))
  keyboard.print_status()
}
```

\*: _Note this only works for integer ranges._

Ranges can be segmented using variants:

```sylva
req sys

variant Age {
  Child: 0u8..17u8,
  Adult: 18u8..250u8,
}

fn print_age(age: Age) {
  sys.echo("Age: {age}")
}

fn print_child_age(age: Age.Child) {
  sys.echo("Child age: {age}")
}
```
