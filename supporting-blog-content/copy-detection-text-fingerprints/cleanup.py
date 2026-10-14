"""Delete the demo index."""

import sys

from es import get_client, index_name

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else index_name()
    get_client().indices.delete(index=name, ignore_unavailable=True)
    print(f"deleted index {name}")
