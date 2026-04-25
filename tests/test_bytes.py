"""Tests for hexstr.encode_bytes / decode_bytes."""

from __future__ import annotations

import pytest

from hexstr import HexStrError, decode_bytes, encode_bytes


class TestEncodeBytes:
    def test_encode_bytes_basic(self) -> None:
        assert encode_bytes(b"\x00\x01\xff") == "0001ff"

    def test_encode_bytes_empty(self) -> None:
        assert encode_bytes(b"") == ""

    def test_encode_bytes_uppercase(self) -> None:
        assert encode_bytes(b"\xde\xad", uppercase=True) == "DEAD"

    def test_encode_bytes_bytearray(self) -> None:
        assert encode_bytes(bytearray(b"\xab\xcd")) == "abcd"

    def test_encode_bytes_memoryview(self) -> None:
        assert encode_bytes(memoryview(b"\xab\xcd")) == "abcd"

    def test_encode_bytes_with_separator(self) -> None:
        assert (
            encode_bytes(b"\xde\xad\xbe\xef", sep=" ", groupsize=2)
            == "de ad be ef"
        )

    def test_encode_bytes_colon_separator(self) -> None:
        assert encode_bytes(bytes(6), sep=":", groupsize=2) == "00:00:00:00:00:00"

    def test_encode_bytes_groupsize_four(self) -> None:
        assert (
            encode_bytes(b"\x12\x34\x56\x78\x9a\xbc", sep="_", groupsize=4)
            == "1234_5678_9abc"
        )

    def test_encode_bytes_sep_requires_groupsize(self) -> None:
        with pytest.raises(HexStrError, match="sep requires groupsize"):
            encode_bytes(b"\xff", sep=":")

    def test_encode_bytes_groupsize_requires_sep(self) -> None:
        with pytest.raises(HexStrError, match="groupsize requires"):
            encode_bytes(b"\xff", groupsize=2)

    def test_encode_bytes_rejects_string(self) -> None:
        with pytest.raises(HexStrError, match="bytes-like"):
            encode_bytes("abc")

    def test_encode_bytes_rejects_bad_groupsize(self) -> None:
        with pytest.raises(HexStrError, match="groupsize must be positive"):
            encode_bytes(b"\xff", sep=" ", groupsize=0)

    def test_encode_bytes_rejects_non_int_groupsize(self) -> None:
        with pytest.raises(HexStrError, match="groupsize must be an int"):
            encode_bytes(b"\xff", sep=" ", groupsize="2")


class TestDecodeBytes:
    def test_decode_bytes_basic(self) -> None:
        assert decode_bytes("0001ff") == b"\x00\x01\xff"

    def test_decode_bytes_empty(self) -> None:
        assert decode_bytes("") == b""
        assert decode_bytes("   ") == b""

    def test_decode_bytes_with_0x_prefix(self) -> None:
        assert decode_bytes("0xdeadbeef") == b"\xde\xad\xbe\xef"

    def test_decode_bytes_colon_separated(self) -> None:
        assert decode_bytes("de:ad:be:ef") == b"\xde\xad\xbe\xef"

    def test_decode_bytes_whitespace_separated(self) -> None:
        assert decode_bytes("de ad\tbe\nef") == b"\xde\xad\xbe\xef"

    def test_decode_bytes_mixed_separators(self) -> None:
        assert decode_bytes("de-ad_be ef") == b"\xde\xad\xbe\xef"

    def test_decode_bytes_odd_digits_rejected(self) -> None:
        with pytest.raises(HexStrError, match="even digit count"):
            decode_bytes("abc")

    def test_decode_bytes_invalid_rejected(self) -> None:
        with pytest.raises(HexStrError, match="invalid hex digit"):
            decode_bytes("zz")

    def test_decode_bytes_rejects_non_str(self) -> None:
        with pytest.raises(HexStrError, match="text must be a str"):
            decode_bytes(b"abcd")


class TestBytesRoundTrip:
    @pytest.mark.parametrize(
        "data",
        [b"", b"\x00", b"\xff", b"\x00\x01\x02\x03", bytes(range(256))],
    )
    def test_round_trip_default(self, data: bytes) -> None:
        assert decode_bytes(encode_bytes(data)) == data

    @pytest.mark.parametrize(
        "data,sep,groupsize",
        [
            (b"\xde\xad\xbe\xef", ":", 2),
            (b"\x00" * 6, "-", 2),
            (b"\x12\x34\x56\x78", " ", 4),
        ],
    )
    def test_round_trip_with_separator(
        self, data: bytes, sep: str, groupsize: int
    ) -> None:
        text = encode_bytes(data, sep=sep, groupsize=groupsize)
        assert decode_bytes(text) == data
