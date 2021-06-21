# Arrays

Arrays in Sylva have both an element type and count:

```sylva
array Names[str]
array SupremeCourtJustices[str * 9]

fn main() {
  var justices: SupremeCourtJustices[
    "John Roberts",
    "Clarence Thomas",
    "Ruth Bader Ginsburg",
    "Stephen Breyer",
    "Samuel Alito",
    "Sonia Sotomayor",
    "Elena Kagen",
    "Neil Gorsuch",
    "Brett Kavanaugh",
  ]
}
```
