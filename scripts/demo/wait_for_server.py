#!/usr/bin/env python3
"""Simple server readiness checker used by the demo script."""
import sys
import time
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


def wait_for(url: str, timeout: int = 10) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = urlopen(url)
            # consider any successful HTTP response as readiness
            return True
        except HTTPError:
            # HTTP errors (e.g., 404) mean the server responded — consider ready
            return True
        except URLError:
            # connection refused / no response yet
            pass
        time.sleep(0.5)
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: wait_for_server.py <url> [timeout]")
        sys.exit(2)
    url = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    ok = wait_for(url, timeout)
    if not ok:
        print(f"Server at {url} did not become ready within {timeout}s", file=sys.stderr)
        sys.exit(1)
    print(f"Server at {url} is ready")


if __name__ == '__main__':
    main()
