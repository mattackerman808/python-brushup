# Gradebook

| Lesson | Topic | Score | Grade | Date |
|---|---|---|---|---|
| 01 | Collections & comprehensions | 95 / 100 | A | completed 2026-08-19 |

## Lesson 01 — 39/39 tests passing

**Correctness — 60/60.** All seven functions match the spec, including the
fiddly bits: `partition` splitting on the first `=` only, non-mutating sort in
`percentile`, first-seen ordering in `group_ms_by_path`, and the two-direction
sort in `format_report`.

**Idiom — 21/25.**

- `count_by` — `Counter` over a generator expression with an `in` guard. Ideal.
- `slowest` — filter comprehension into `sorted(key=..., reverse=True)[:n]`.
  Correct use of `reverse=True` here, where every field sorts the same way.
- `group_ms_by_path` — `setdefault(k, []).append(v)`, plain dict, no sort
  needed. Exactly right.
- `format_report` — accumulate into a list, `"\n".join` at the end. Reuses both
  helpers rather than recomputing.
- −3: `error_hosts` is still a loop building a list that gets passed to `set()`.
  It's a one-line set comprehension. Flagged since day one, never revisited.
- −1: `return("\n".join(...))` — `return` is a keyword, the parens are noise.

**Edge cases — 10/10.** Guards on every function that needs one, `ValueError`
on empty input, and the `max(0, ...)` clamp so `p=0` doesn't wrap to the last
element via negative indexing. That clamp is the one most people ship broken.

**Clarity — 4/5.** `by_path`, `p95`, `times` all read well. −1 for `output`
holding a list of lines (`lines`), `input_sorted` (`ordered` / `ranked`), and
`lambda x:` where `item` would say what it is. File isn't `ruff format`ed —
missing blank lines between defs, trailing blank lines at EOF.

**Pattern to watch.** Three of the four bugs were the same shape: a value used
in place of the thing it describes — `record.items()` instead of the two keys
you wanted, `str(times)` instead of `len(times)`, `x[1]` (the list) instead of
its length. Reasoning was sound every time; the slip was reaching one level off
the thing you meant. When a column looks wrong, ask "am I holding the container
or what's in it?"
