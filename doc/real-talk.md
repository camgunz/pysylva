# Real Talk

Making Sylva fully consistent and homoiconic is becoming a real pain in the
ass.  And in truth, these aren't really things I care about.  Essentially I
want:

- A C that's not a forest of traps and includes a (small) stdlib
- A Swift without mandatory GC
- A Rust without all the cuteness
- A Go without GC or the opinion
- An Ada without the verbosity

But notably, I do want strong safety guarantees, and I want contracts (pre/post
conditions)

So I think I'm moving away from non-macro Sylva, homoiconicity, and macros in
general.

I do still thing components are useful, if only to get us away from variants.
But in the interest of not being cute, I'm calling them interfaces because
that's what they are.

Aliases will be important.
