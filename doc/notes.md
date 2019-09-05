# Notes

## Interfaces and UFCS

Keeping interfaces around when we have variants and pattern matching feels
confused.  I think the answer to "how do you do polymorphism with
variants/pattern matching" is conversion functions.

## Variants

My current thinking on variant implementation is to keep a discriminant byte
around.  Few things about this:

- This _could_ be elided by the compiler via monomorphization, but that's
  exponential and can blow up pretty quick.
- Being specific about data layout is nice.  I wonder if there's a way to
  accomplish this in Sylva.

And I guess the type information can be elided by the compiler when it isn't
necessary.  Although maybe being specific about data layout can be nice--feels
like there should be... a different construct for that?

Like, because this is all typed, the compiler can monomorphize... but that is
exponential.

## Optional commas

This would be really nice for types/components/etc, and I think the only issue
is arithmetic expressions.

I think the option is comma or newline, and that means if you want multi-line
expressions you gotta use parens.

## Iteration

I think my opinion here is:

**Are you building a collection?**: Use that collection
**Are you processing elements of a collection?**: Use a pipeline

In other words, iteration feels like an anti-pattern.

Does... that mean we're getting rid of for/while/loop...?
