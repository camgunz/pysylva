## Scalars

- `bool`
- `rune`: an unsigned 32-bit integer representing a Unicode code point
- `num`
  - `dec`: arbitrary-precision floating point -- Sylva's default numeric type
  - `integer`
    - `int`
      - `i8`, `i16`, `i32`, `i64`, `i128`, `i256`
    - `uint`
      - `u8`, `u16`, `u32`, `u64`, `u128`, `u256`
  - `float`
    - `f16`, `f32`, `f64`, `f128`, `f256`
  - `complex`
    - `c16`, `c32`, `c64`, `c128`, `c256`
- `str`: an immutable sequence of Unicode code points encoded using an encoding
         specified at compile-time.
