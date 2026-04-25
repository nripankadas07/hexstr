"""Core implementation for hexstr — pack/unpack ints + bytes as hex strings."""
from __future__ import annotations

from typing import Iterable, Literal, Optional, Tuple, Union

__version__ = "1.0.0"

_PREFIXES = ("0x", "0X", "#", "$", "\\x", "\\X")
_HEX = frozenset("0123456789abcdefABCDEF")
_SEPS = frozenset(" \t\n\r:_-")


class HexStrError(ValueError):
    """Raised on invalid hexstr input."""


def _validate_int(value, name):
    if isinstance(value, bool) or not isinstance(value, int):
        raise HexStrError(f"{name} must be an int, got {type(value).__name__}")
    return value


def _validate_width(width):
    if width is None:
        return None
    if isinstance(width, bool) or not isinstance(width, int) or width < 0:
        raise HexStrError("width must be a non-negative int or None")
    return width


def _validate_sign(sign):
    if sign not in ("default", "unsigned", "twos-complement"):
        raise HexStrError(f"sign must be 'default'/'unsigned'/'twos-complement', got {sign!r}")
    return sign


def _validate_byteorder(bo):
    if bo not in ("big", "little"):
        raise HexStrError(f"byteorder must be 'big' or 'little', got {bo!r}")
    return bo


def _reverse_byte_pairs(digits):
    if len(digits) % 2:
        digits = "0" + digits
    pairs = [digits[i:i+2] for i in range(0, len(digits), 2)]
    pairs.reverse()
    return "".join(pairs)


def encode(value, *, width=None, prefix="", uppercase=False, sign="default", byteorder="big"):
    """Encode an int as a hex string. See README for full options."""
    _validate_int(value, "value")
    width = _validate_width(width)
    sign = _validate_sign(sign)
    byteorder = _validate_byteorder(byteorder)
    if not isinstance(prefix, str):
        raise HexStrError("prefix must be a string")
    if sign == "unsigned" and value < 0:
        raise HexStrError(f"unsigned mode rejects negative value {value}")
    if sign == "twos-complement":
        if width is None or width <= 0 or width % 2:
            raise HexStrError("twos-complement requires positive even width")
        if value < 0:
            value = (1 << (width * 4)) + value
        digits = format(value, "x").rjust(width, "0")
        if byteorder == "little":
            digits = _reverse_byte_pairs(digits)
        return (prefix + (digits.upper() if uppercase else digits))
    sign_str = "-" if value < 0 else ""
    digits = format(abs(value), "x")
    if width is not None:
        digits = digits.rjust(width, "0")
    if byteorder == "little":
        digits = _reverse_byte_pairs(digits)
    if uppercase:
        digits = digits.upper()
    return sign_str + prefix + digits


def decode(text, *, sign="default", width=None, byteorder="big"):
    """Decode a hex string to an int."""
    if not isinstance(text, str):
        raise HexStrError("text must be a str")
    sign = _validate_sign(sign)
    width = _validate_width(width)
    byteorder = _validate_byteorder(byteorder)
    s = text.strip()
    sign_str = ""
    if s and s[0] in "+-":
        sign_str = s[0]
        s = s[1:]
    for p in _PREFIXES:
        if s.startswith(p):
            s = s[len(p):]
            break
    if not s or any(c not in _HEX for c in s):
        raise HexStrError(f"invalid hex digit in {text!r}")
    digits = s
    if byteorder == "little":
        digits = _reverse_byte_pairs(digits)
    if sign == "twos-complement":
        if width is None or width <= 0 or width % 2 or len(digits) != width:
            raise HexStrError("twos-complement decode requires width matching digit count")
        n = int(digits, 16)
        if n & (1 << (width * 4 - 1)):
            n -= (1 << (width * 4))
        return n
    n = int(digits, 16)
    if sign == "unsigned" and (sign_str == "-"):
        raise HexStrError("unsigned mode rejects negative input")
    return -n if sign_str == "-" else n


def encode_bytes(data, *, uppercase=False, sep="", groupsize=None):
    """Encode bytes-like to hex with optional separators."""
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise HexStrError("data must be bytes-like")
    if not isinstance(sep, str):
        raise HexStrError("sep must be a string")
    if (sep != "" and groupsize is None):
        raise HexStrError("sep requires groupsize")
    if (groupsize is not None and sep == ""):
        raise HexStrError("groupsize requires sep")
    if groupsize is not None:
        if isinstance(groupsize, bool) or not isinstance(groupsize, int):
            raise HexStrError("groupsize must be an int")
        if groupsize <= 0:
            raise HexStrError("groupsize must be positive")
    text = bytes(data).hex()
    if uppercase:
        text = text.upper()
    if sep and groupsize:
        gs = groupsize
        text = sep.join(text[i:i+gs] for i in range(0, len(text), gs))
    return text


def decode_bytes(text):
    """Decode hex back to bytes; tolerates whitespace, :, _, -, and prefixes."""
    if not isinstance(text, str):
        raise HexStrError("text must be a str")
    s = text.strip()
    for p in _PREFIXES:
        if s.startswith(p):
            s = s[len(p):]
            break
    cleaned = "".join(c for c in s if c not in _SEPS)
    if not cleaned:
        return b""
    if len(cleaned) % 2:
        raise HexStrError(f"hex byte string requires even digit count, got {len(cleaned)}")
    if any(c not in _HEX for c in cleaned):
        raise HexStrError(f"invalid hex digit in {text!r}")
    return bytes.fromhex(cleaned)
