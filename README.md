# hexstr

Zero-dependency Python library for packing and unpacking integers and
byte sequences into hex strings with explicit control over prefix,
width, case, sign mode, and byte order.

## Install

```bash
pip install hexstr
```

Requires Python 3.8 or newer. No runtime dependencies.

## Why?

Python's stdlib has `hex()`, `int(s, 16)`, and `bytes.hex()`, but they
don't compose well:

- `hex(255)` returns `"0xff"` with a fixed prefix you can't swap.
- `hex(-255)` returns `"-0xff"`, not a two's-complement encoding.
- There's no built-in way to pad to a fixed width with a custom prefix,
  or to emit little-endian hex, or to decode `"DE:AD:BE:EF"` back to
  bytes.

`hexstr` handles all of that from one tiny API.

## Usage

```python
from hexstr import encode, decode, encode_bytes, decode_bytes

encode(255)
encode(255, prefix="0x")
encode(0xAB, width=4, prefix="0x")
encode(-255, prefix="0x")
encode(-1, width=8, sign="twos-complement")
decode("ffffffff", width=8, sign="twos-complement")
encode_bytes(b"\xde\xad\xbe\xef")
encode_bytes(b"\xde\xad\xbe\xef", sep=":", groupsize=2)
decode_bytes("DE:AD:BE:EF")
decode_bytes("0x de ad be ef")
```

Accepts these prefixes on decode: `0x`, `0X`, `#`, `$`, `\x`, `\X`.

## API

### `encode(value, *, width=None, prefix="", uppercase=False, sign="default", byteorder="big")`

Encode an integer as a hex string.

### `decode(text, *, sign="default", width=None, byteorder="big")`

Decode a hex string to an integer.

### `encode_bytes(data, *, uppercase=False, sep="", groupsize=None)`

Encode bytes-like to hex; pass both `sep` and `groupsize` to insert separators.

### `decode_bytes(text)`

Tolerant of whitespace, `:`, `_`, `-` separators.

### `HexStrError`

Subclass of `ValueError`.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT © 2026 Nripanka Das
