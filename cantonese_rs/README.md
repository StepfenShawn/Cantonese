# cantonese-rs

Cantonese language parser and Python-targeting compiler, implemented in Rust with PyO3 bindings.

## Build

```bash
maturin build
python -m pip install .\target\wheels\cantonese_rs-0.1.0-cp39-abi3-win_amd64.whl --force-reinstall
```

## Usage

```python
import cantonese_rs
from cantonese_rs.libs import get_globals

py_code = cantonese_rs.to_python("介紹返 x 係 5\n", "test.cantonese")
exec(py_code, get_globals())
```
