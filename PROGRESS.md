# Where we left off — 2026-08-19

**Lesson 01 COMPLETE — 39/39 tests, 95/100 (A).** See GRADEBOOK.md for notes.

## Next: lesson 02 — strings & regex

Not written yet. Ask me to generate it: NOTES.md + exercises.py stubs +
test_lesson02.py, same shape as lesson 01, SRE angle (messy text munging,
extracting fields out of half-structured log lines).

## Optional cleanup on lesson 01

Nothing blocking, all cosmetic:

- `error_hosts` — rewrite the loop as a one-line set comprehension
- `format_report` — `return "\n".join(output)`, drop the parens; rename
  `output` to `lines`, `lambda x:` to `lambda item:`
- `percentile` — `input_sorted` reads awkwardly; `ordered` or `ranked`
- run `uvx ruff format lesson01/`

## Concepts covered in lesson 01

- `str.split()` / `str.partition()`, star-unpacking `a, b, *rest = ...`
- functions return `None` implicitly if you forget `return`
- immutability: `int(v)` returns a new object, it doesn't convert in place
- `d[k]` raises `KeyError`; `d.get(k, default)` doesn't
- accumulate idiom `d[k] = d.get(k, 0) + 1`, then `Counter` replaces it
- comprehensions: `[]` list, `{}` set, `{k: v}` dict, bare = generator
- a `continue` guard is the negation of a comprehension `if` filter
- `and`/`or` short-circuit, so a guard on the left protects the right
- sets are unordered and deduplicate; don't shadow builtins
- `d.items()` walks the whole record — grouping by field *name*, not value
- bare `path` is a variable lookup, `"path"` is the key; `record[key]` is right
  in `count_by` (caller passed a variable) and wrong where the key is literal
- `setdefault(k, [])` returns *the list*, which is what makes `.append()` chain
- dict insertion order is guaranteed in py3.7+, so "first-seen order" is free
- `sorted()` returns a new list; `.sort()` mutates in place and returns `None`
  (same pairing as `reversed()` / `.reverse()`)
- `raise ValueError(...)` exits the function like a guard clause;
  `pytest.raises` expects the explosion
- negative indices wrap to the end — `xs[-1]` is the last item, so an
  unclamped negative index fails *silently*
- clamping: `max(0, x)` floors, `min(100, x)` caps, nested = a real clamp
- nearest-rank percentile is sort-and-point, not arithmetic; p50/p95 beat the
  mean because one outlier can't drag them
- f-strings: `{x:<20}` `{x:>5}` `{x:^10}` align, `{x:,}` `{x:.2f}` `{x:.1%}`
  format numbers, `{x!r}` shows repr, width is a *minimum* (no truncation)
- `"\n".join(lines)` puts separators *between* items — no trailing newline,
  and `"".join([])` is `""` so empty input handles itself
- adjacent string literals concatenate: `"foo" "bar"` is `'foobar'`
- tuple keys sort left to right; negate a numeric field for descending while
  another stays ascending — `reverse=True` flips *everything* and can't mix
- lists compare elementwise, so sorting by a list sorts by its first differing
  element
- the walrus `(r := f(x))` assigns inside an expression — the only way to avoid
  calling `f` twice inside a comprehension (proper coverage in lesson 08)
- `@pytest.fixture` injects by parameter name; `@parametrize` takes a list of
  tuples, one per case, unpacked into the named params

## Syllabus ahead

02 strings & regex → 03 decorators → 04 pathlib/JSON → 05 exceptions & logging →
06 generators → 07 dataclasses → 08 type hints & `match` → 09 subprocess/argparse CLI →
10 HTTP & APIs → 11 threads vs asyncio → 12 pytest & packaging

## Running things

```
cd ~/git/python-brushup
uv run --project lesson01 pytest lesson01 -q            # all 39
uv run --project lesson01 pytest lesson01 -q -k Slowest # one group
```
