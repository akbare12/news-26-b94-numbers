#!/usr/bin/env python3
"""Copy the pre-rendered entry.png into the grader output directory.

Stdlib only: the grader image has no third-party packages installed,
so this file must not import PIL, numpy or anything beyond the standard
library. The picture itself is rendered at build time by gen.py (PIL)
and committed to the repo as entry.png; this script only copies it.
"""
import hashlib
import os
import shutil
import sys


ENTRY_NAME = "entry.png"
MAX_BYTES = 1024 * 1024


def repo_root():
    """Directory that holds this file (the repo root when graded)."""
    return os.path.dirname(os.path.abspath(__file__))


def output_dir():
    """Grader output dir, or a local 'out' fallback for manual runs."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "out")


def destination():
    """Full path of the output file inside the output directory."""
    return os.path.join(output_dir(), ENTRY_NAME)


def source_path():
    """Full path of the committed entry.png next to this file."""
    return os.path.join(repo_root(), ENTRY_NAME)


def sha256_of(path):
    """Hex SHA-256 digest of a file, read in bounded chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def verify_source(path):
    """Check the committed entry exists and is within the size cap."""
    if not os.path.isfile(path):
        raise SystemExit("entry.png not found next to main.py: %s" % path)
    size = os.path.getsize(path)
    if size <= 0 or size > MAX_BYTES:
        raise SystemExit("entry.png size out of range: %d bytes" % size)
    return size


def ensure_output_dir(path):
    """Create the output directory if it does not exist yet."""
    os.makedirs(path, exist_ok=True)
    if not os.path.isdir(path):
        raise SystemExit("cannot create output directory: %s" % path)


def copy_entry():
    """Copy entry.png to the output directory and verify the copy."""
    src = source_path()
    size = verify_source(src)
    before = sha256_of(src)
    dst = destination()
    ensure_output_dir(output_dir())
    shutil.copyfile(src, dst)
    after = sha256_of(dst)
    if before != after:
        raise SystemExit("copy checksum mismatch: %s != %s" % (before, after))
    return dst, size, after


def main():
    """Entry point: copy the image and report where it landed."""
    dst, size, digest = copy_entry()
    print("wrote %s (%d bytes, sha256=%s)" % (dst, size, digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
