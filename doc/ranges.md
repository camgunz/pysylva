# Ranges

The core numeric type in Sylva is the `range`, which is a bounded numeric type.
Ranges are far preferable to raw numbers for a number of reasons:
- they can be thought of as numbers with **units**
- finite ranges make dealing with arrays much easier: if an array is defined
  in terms of a finite range, bounds checks are unnecessary when indexing using
  a value from that range

Ranges inherit the properties from their boundaries.

```sylva
range HealthRange(0crn, 100crn)
```

This defines a range from 0-100, which will clamp at 0 and 100, and round to
the nearest number in cases of insufficient precision.

Ranges can help you avoid prodigious error handling and wrapping:

```sylva
range HealthRange(0crn, 100crn)

variant Monster {
  struct Irukakun {
    health: HealthRange(100)
  }
  struct Sirotan {
    health: HealthRange(1000)
  }
}

fn damage_monster(monster: &Monster!) {
  var damage: random.random_range(HealthRange)

  match(monster) {
    case(Monster.Irukakun) {
      damage *= 2crn # Softie
    }
    case(Monster.Sirotan) {
      damage /= 2crn # Tough stuff
    }
  }

  monster.health -= damage
}
```

Without ranges, you'd have a lot more work to do:

```sylva
variant Monster {
  struct Irukakun {
    health: 100crn
  }
  struct Sirotan {
    health: 1000crn
  }
}

fn damage_monster(monster: &Monster!) {
  var damage: random.random_between(0crn, 100crn)

  match(monster) {
    case(Monster.Irukakun) {
      damage *= 2crn
      if(damage > 100) {
        damage = 100
      }
    }
    case(Monster.Sirotan) {
      with(half_damage: damage /= 2crn) {
        damage = half_damage
      }
    }
  }

  monster.health -= damage

  if(monster.health < 0) {
    monster.health = 0
  }
}
```

They also allow the programmer to avoid catching indexing errors:

```sylva
requirement sys
requirement midi

range PianoKey(1u8, 88u8)

fn play_key(key: PianoKey) {
  midi.play_note(key)
}

fn main() {
  val pressed_keys: [bool * PianoKey.max]
  sys.echo("18th key pressed: {pressed_keys[piano_key(18)]}")
  play_key(piano_key(3))
}
```
