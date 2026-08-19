"""Lesson 02 — strings & regex.

Fill in each function. Delete the `raise NotImplementedError` line as you go.
Don't change the signatures or the docstrings.
"""
import re
from collections import Counter

UNITS = {"h": 3600, "m": 60, "s": 1}
SECRET_KEYS = ("password", "token", "secret", "api_key")


def normalize_ws(s):
    """Collapse whitespace and strip the ends.

    Every run of whitespace (spaces, tabs, newlines, any mix) becomes a single
    space, and leading/trailing whitespace is removed.

    >>> normalize_ws("  web-01\\t\\tis   down\\n")
    'web-01 is down'
    >>> normalize_ws("   ")
    ''
    """
    raise NotImplementedError


def parse_duration(text):
    """Parse a duration string into a whole number of seconds.

    A duration is one or more `<number><unit>` parts, where unit is h, m, or s
    (see UNITS). Parts may repeat, may appear in any order, and may be
    separated by whitespace. Matching is case-insensitive. Surrounding
    whitespace is ignored.

    Raises ValueError on anything else — an empty string, a number with no
    unit, a unit with no number, or any leftover junk.

    >>> parse_duration("1h30m")
    5400
    >>> parse_duration("45s")
    45
    >>> parse_duration("2H 15M")
    8100
    """
    raise NotImplementedError


def extract_ips(text):
    """Find the IPv4 addresses in a blob of text.

    An address is four dot-separated groups of 1-3 digits, each 0-255.
    Returns them in the order they first appear, with duplicates removed.
    Anything with an out-of-range group (999.1.1.1) or the wrong number of
    groups (1.2.3) is not an address.

    >>> extract_ips("from 10.0.0.1 to 10.0.0.2, retry 10.0.0.1")
    ['10.0.0.1', '10.0.0.2']
    """
    raise NotImplementedError


def parse_nginx_line(line):
    """Parse one nginx combined-format access log line into a dict.

    Format:

        <ip> <ident> <user> [<ts>] "<method> <path> <proto>" <status> <bytes>

    e.g.

        10.0.0.1 - - [18/Aug/2026:04:12:03 +0000] "GET /healthz HTTP/1.1" 200 42

    Returns a dict with keys "ip", "ts", "method", "path", "status", "bytes".
    "status" and "bytes" are ints; a "-" in the bytes field means 0. The ident
    and user fields are matched but thrown away. Returns None if the line
    doesn't match.

    >>> parse_nginx_line('10.0.0.1 - - [18/Aug/2026:04:12:03 +0000] "GET /healthz HTTP/1.1" 200 42')
    {'ip': '10.0.0.1', 'ts': '18/Aug/2026:04:12:03 +0000', 'method': 'GET', 'path': '/healthz', 'status': 200, 'bytes': 42}
    """
    raise NotImplementedError


def redact_secrets(text):
    """Mask the values of sensitive key=value pairs.

    For every key in SECRET_KEYS, replace the value with "***", keeping the key
    and the "=" exactly as written. Key matching is case-insensitive; the
    original spelling of the key is preserved. A value runs to the next
    whitespace. Text with no matches comes back unchanged.

    >>> redact_secrets("user=bob password=hunter2 host=web-01")
    'user=bob password=*** host=web-01'
    """
    raise NotImplementedError


def status_class_counts(lines):
    """Tally log lines by status class.

    Parse each line with parse_nginx_line and count them by the first digit of
    the status: 200 and 204 are both "2xx", 503 is "5xx". Lines that don't
    parse are skipped. Returns a dict mapping class -> count.

    >>> status_class_counts(['10.0.0.1 - - [t] "GET / HTTP/1.1" 200 1'])
    {'2xx': 1}
    """
    raise NotImplementedError


def top_paths(lines, n=3):
    """Return the `n` most-requested paths as (path, count) pairs.

    Parse each line with parse_nginx_line, skipping lines that don't parse.
    Most requests first; ties broken by path ascending. If fewer than `n`
    distinct paths appear, return all of them. No lines gives [].

    >>> top_paths(['10.0.0.1 - - [t] "GET /a HTTP/1.1" 200 1'], 3)
    [('/a', 1)]
    """
    raise NotImplementedError
