# Lesson 01 — Collections & comprehensions

Scenario: you're handed a pile of app log lines and asked "which host is
throwing errors and which endpoint got slow?" This is 80% of ad-hoc SRE Python.

Log line format:

```
2026-08-18T04:12:03Z INFO web-01 status=200 path=/api/v1/users ms=42
<-- ts -----------> <lvl> <host> <-------- key=value pairs -------->
```

## Refresher

**Comprehensions** — the default way to build a list/dict/set from another iterable:

```python
[r["ms"] for r in records if r["level"] == "ERROR"]   # list
{r["host"] for r in records}                          # set
{r["path"]: r["ms"] for r in records}                 # dict
```

**Splitting** — `line.split()` with no args splits on *runs* of whitespace and
drops empties; `line.split("=", 1)` caps the number of splits (important when
the value itself contains `=`). `str.partition("=")` returns a 3-tuple and
never raises.

**Dict access patterns**

```python
d["k"]                  # KeyError if missing
d.get("k")              # None if missing
d.get("k", 0)           # default
d.setdefault("k", []).append(x)   # get-or-create
"k" in d                # membership tests keys
for k, v in d.items(): ...
```

**`collections`** — `Counter` for tallies (`Counter(seq)`, `.most_common(n)`),
`defaultdict(list)` for group-by. Both are dict subclasses, so
`Counter(...) == {"a": 2}` is True.

**Sorting** — `sorted(xs, key=lambda r: r["ms"], reverse=True)`. Python's sort
is *stable*: equal keys keep their original relative order. For multi-key sorts,
return a tuple: `key=lambda r: (-r["count"], r["path"])`.

**Unpacking**

```python
ts, level, host, *rest = line.split()   # star-target soaks up the remainder
k, v = token.split("=", 1)
```

**f-strings and format specs** (used in the last exercise):

```python
f"{name:<20}"   # left-justify, width 20
f"{n:>5}"       # right-justify, width 5
f"{x:.2f}"      # 2 decimal places
```

**Truthiness** — `if not values:` is how you test for an empty list/str/dict.
Don't write `if len(values) == 0:`.

## Your task

Fill in the six functions in `exercises.py`. Read the docstrings carefully —
the tests follow them literally. Then:

```
cd ~/git/python-brushup && pytest lesson01 -q
```
