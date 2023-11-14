import sys

from ._codespell import _script_main

if __name__ == "__main__":
    try:
        sys.exit(_script_main())
    except KeyboardInterrupt:
        pass
