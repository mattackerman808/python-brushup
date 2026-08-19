# Python Brush-Up — SRE / sysadmin / API track

Python 3.14, pytest. One lesson per directory.

## How each lesson works

1. Read `lessonNN/NOTES.md` — a short refresher on the idioms in play (5 min).
2. Fill in the stubs in `lessonNN/exercises.py`. Don't edit the tests.
3. Run them yourself until green:
   ```
   cd ~/git/python-brushup && pytest lessonNN -q
   ```
4. Tell me you're done. I run the tests, read your code, and grade it.
   Passing the tests is necessary but not sufficient — style and idiom count.

## Grading rubric (100 pts)

| Weight | Category | What I look at |
|---|---|---|
| 60 | Correctness | tests pass, spec followed |
| 25 | Idiom | comprehensions vs loops, right stdlib tool, no reinventing |
| 10 | Edge cases | empty input, missing keys, bad data |
| 5  | Clarity | naming, structure, no dead code |

Grades land in `GRADEBOOK.md` with per-exercise notes.

## Syllabus (flexible — we can reorder)

| # | Topic | SRE angle |
|---|---|---|
| 01 | Collections & comprehensions | parsing a log file |
| 02 | Strings & regex | messy text munging, extracting fields |
| 03 | Functions: `*args/**kwargs`, closures, decorators | a `@retry` and `@timed` decorator |
| 04 | pathlib, JSON, context managers | config files, atomic writes |
| 05 | Exceptions & the `logging` module | error hierarchies, structured logs |
| 06 | Iterators & generators, `itertools` | streaming a 10 GB log without eating RAM |
| 07 | Classes, `dataclasses`, `enum` | modeling hosts/incidents/alerts |
| 08 | Type hints & modern syntax (`match`, `\|`, walrus) | mypy-clean code |
| 09 | `subprocess`, `os.environ`, `argparse` | building a real CLI tool |
| 10 | HTTP & APIs (`httpx`/`requests`) | retries, pagination, rate limits |
| 11 | Concurrency: threads vs `asyncio` | fan-out health checks across 500 hosts |
| 12 | Testing & packaging | fixtures, `parametrize`, mocking, project layout |
