"""hexstr — pack/unpack integers into hex strings.

A small, zero-dependency library that turns ``int`` and ``bytes`` values
into their hexadecimal text representations (and back) with explicit
control over prefix, width, case, sign mode, and byte order.

Public API:

* :func:`encode`       — int → hex string.
* :func:`decode`       — hex string → int.
* :func:`encode_bytes` — bytes → hex string (with optional separator).
* :func:`decode_bytes` — hex string → bytes (tolerant of separators).
* :class:`HexStrError` — raised on invalid input (``ValueError`` subclass).
"""

from __future__ import annotations

from ._core import (
    HexStrError,
    __version__,
    decode,
    decode_bytes,
    encode,
    encode_bytes,
)

__all__ = [
    "HexStrError",
    "__version__",
    "decode",
    "decode_bytes",
    "encode",
    "encode_bytes",
]
