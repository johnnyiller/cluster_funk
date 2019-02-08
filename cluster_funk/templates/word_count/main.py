import sys

from lib.word_count import word_count

if len(sys.argv) != 2:
    print("Usage: sort <file>", file=sys.stderr)
    sys.exit(-1)

word_count(sys.argv[1])
