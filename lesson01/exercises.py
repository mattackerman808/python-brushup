"""Lesson 01 — collections & comprehensions.

Fill in each function. Delete the `raise NotImplementedError` line as you go.
Don't change the signatures or the docstrings.
"""
from collections import Counter
import math

ERROR_LEVELS = ("ERROR", "FATAL")

def parse_line(line):
    """Parse one log line into a dict, or return None if it's not a log line.

    Format:  "<ts> <level> <host> [key=value ...]"

    - Fields are separated by whitespace (any amount).
    - Returns a dict with keys "ts", "level", "host", plus one entry per
      key=value token found after the host.
    - "status" and "ms" values are converted to int; everything else stays str.
    - Tokens after the host that contain no "=" are ignored.
    - A value may itself contain "=" (split on the FIRST one only).
    - Returns None for a blank line or a line with fewer than 3 fields.

    >>> parse_line("2026-08-18T04:12:03Z INFO web-01 status=200 ms=42")
    {'ts': '2026-08-18T04:12:03Z', 'level': 'INFO', 'host': 'web-01', 'status': 200, 'ms': 42}
    """
    fields = line.split()

    if len(fields) < 3:
        return None

    ts, level, host, *rest = fields

    d = {"ts": ts, "level": level, "host": host}

    for token in rest:
        key, sep, value = token.partition("=")
        if not sep:
            continue
        if key in ("ms", "status"):
            value = int(value)
        d[key] = value

    return d


def count_by(records, key):
    """Tally how many records have each value of `key`.

    Records that lack `key` are skipped. Returns a dict mapping value -> count.

    >>> count_by([{"level": "INFO"}, {"level": "INFO"}, {"host": "a"}], "level")
    {'INFO': 2}
    """
    return Counter(record[key] for record in records if key in record)

def error_hosts(records):
    """Return the set of hosts that logged at least one ERROR or FATAL line.

    Use the module-level ERROR_LEVELS. Records missing "level" or "host" are
    skipped.
    """

    hosts = []

    for record in records:
        if "host" not in record or "level" not in record:
            continue
        if record["level"] in ERROR_LEVELS:
            hosts.append(record["host"])

    return set(hosts)


def slowest(records, n=3):
    """Return the `n` records with the highest "ms", highest first.

    Records without an "ms" key are skipped. Ties keep their original relative
    order. If fewer than `n` records qualify, return all of them.
    """

    with_ms = [r for r in records if "ms" in r]
    return sorted(with_ms, key=lambda r: r["ms"], reverse=True)[:n]


def group_ms_by_path(records):
    """Group request durations by path.

    Returns dict mapping path -> list of "ms" values, in the order encountered.
    Paths appear in the order they were first seen. Records missing either
    "path" or "ms" are skipped.

    >>> group_ms_by_path([{"path": "/a", "ms": 1}, {"path": "/a", "ms": 5}])
    {'/a': [1, 5]}
    """
    by_path = {}

    for record in records:
        if "path" not in record or "ms" not in record:
            continue
        by_path.setdefault(record["path"], []).append(record["ms"])

    return by_path


def percentile(values, p):
    """Nearest-rank percentile of a list of numbers.

    Sort the values, then take index ceil(p / 100 * len(values)) - 1, clamped
    into range. Does not mutate the caller's list.

    Raises ValueError("no values") on an empty list.

    >>> percentile([1, 2, 3, 4], 50)
    2
    >>> percentile([1, 2, 3, 4], 100)
    4
    """
    if not values:
        raise ValueError("no values")

    input_sorted = sorted(values)
    position = max(0, math.ceil(p / 100 * len(values)) - 1)

    return input_sorted[position]


def format_report(records):
    """Build a per-path summary table as a single string.

    One line per path, columns:

        <path left-justified, width 20><space><count right-justified, width 5><space><p95 right-justified, width 6>

    i.e. f"{path:<20} {count:>5} {p95:>6}". p95 is percentile(durations, 95).
    Sort by count descending, then by path ascending. Lines are joined with
    "\\n" and there is no trailing newline. An empty input gives "".
    """
    output = []

    by_path = group_ms_by_path(records)

    for path, times in sorted(by_path.items(), key=lambda x: (-len(x[1]), x[0])):
        p95 = percentile(times, 95)
        output.append(f"{path:<20} {len(times):>5} {p95:>6}")

    return("\n".join(output))



