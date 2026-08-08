# cantonese-rs

Cantonese language parser and Python-targeting compiler, implemented in Rust with PyO3 bindings.

## Build

```bash
maturin develop
```

## Usage

```python
import cantonese_rs
from cantonese_rs.libs import get_globals

py_code = cantonese_rs.to_python("介紹返 x 係 5\n", "test.cantonese")
exec(py_code, get_globals())
```
