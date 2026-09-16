"""Discarding unfinished streams must stop their native worker threads."""

import subprocess
import sys

import pytest

pytest.importorskip("psutil")


@pytest.mark.parametrize("kind", ["compressobj", "decompressobj_blast", "decompressobj_pklib"])
def test_discard_unfinished_stream(kind, tmp_path):
    # Isolate native crashes and count OS threads, which threading.enumerate misses.
    script = """
import sys
import dclimplode
import psutil

process = psutil.Process()
initial_threads = process.num_threads()
for _ in range(16):
    stream = getattr(dclimplode, sys.argv[1])()
    if sys.argv[1] == "compressobj":
        stream.compress(b"unfinished input")
    else:
        stream.decompress(b"\\x00\\x06" + bytes(32))
        assert not stream.eof
    del stream
assert process.num_threads() <= initial_threads
"""
    subprocess.run([sys.executable, "-c", script, kind], cwd=str(tmp_path), check=True, timeout=30)
