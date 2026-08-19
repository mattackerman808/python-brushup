# Lesson 02 — Strings & regex

Scenario: the logs aren't tidy `key=value` pairs this time. You've got nginx
access logs, half-structured text, and secrets that must not reach a ticket.
Regex is the tool, and knowing when *not* to use it matters as much.

```
10.0.0.1 - - [18/Aug/2026:04:12:03 +0000] "GET /api/v1/users HTTP/1.1" 200 1234
<-- ip -> ^ ^ <------- timestamp -------> <----- request -----> <sts> <bytes>
          └─┴─ ident and user, almost always "-"
```

## Refresher

**Raw strings.** Always write patterns as `r"..."`. Regex uses `\` constantly
and so do normal Python strings, so without the `r` you end up escaping your
escapes:

```python
"\d"     # Python sees an unknown escape — works today, warns, may break
r"\d"    # a backslash and a d, which is what the regex engine wants
r"\\"    # a literal backslash in the pattern
```

**The pieces you need here.**

```
.          any character except newline
\d \w \s   digit, word char [a-zA-Z0-9_], whitespace
\D \W \S   the negation of each
[abc]      one of a, b, c        [^abc]  anything but
[A-Z]      a range
\b         word boundary — zero width, matches between \w and non-\w
^ $        start / end of string
```

**Quantifiers.** Attach to the thing before them:

```
a*         zero or more        a+     one or more
a?         zero or one         a{3}   exactly 3
a{1,3}     one to three
```

Quantifiers are **greedy** — they take as much as possible, then give back
only if the rest of the pattern fails. Add `?` to make one lazy:

```python
re.findall(r'".*"',  'say "a" and "b"')    # ['"a" and "b"']  greedy: one big match
re.findall(r'".*?"', 'say "a" and "b"')    # ['"a"', '"b"']   lazy: stops early
```

Often the better fix is neither: `[^"]*` says "anything but a quote," which
can't run past the closing quote in the first place. Being specific beats
being clever.

**The five functions.** They differ in *where* they look and *what* they give
back:

```python
re.search(p, s)     # first match anywhere      -> Match | None
re.match(p, s)      # must match at the START   -> Match | None
re.fullmatch(p, s)  # must match the WHOLE      -> Match | None
re.findall(p, s)    # every match               -> list of str (or tuples, see below)
re.sub(p, repl, s)  # replace every match       -> str
```

`match` and `fullmatch` are the validators; `search` is what you usually want
when scanning a line. All the Match-returning ones give `None` on no match, so
`if m is None: return None` is the standard opener.

**Groups.** Parentheses capture:

```python
m = re.search(r"(\d+)x(\d+)", "size 1920x1080")
m.group(0)    # '1920x1080'  the whole match
m.group(1)    # '1920'       first group
m.groups()    # ('1920', '1080')
```

`findall` changes shape depending on group count — 0 groups gives whole
matches, 1 group gives that group, 2+ gives tuples:

```python
re.findall(r"\d+[hms]",   "1h30m")   # ['1h', '30m']
re.findall(r"(\d+)([hms])", "1h30m")   # [('1', 'h'), ('30', 'm')]
```

That second form unpacks straight into a loop: `for amount, unit in ...`.

**Named groups** — `(?P<name>...)` — turn a match into a dict:

```python
m = re.match(r"(?P<host>\S+):(?P<port>\d+)", "web-01:8080")
m.group("host")   # 'web-01'
m.groupdict()     # {'host': 'web-01', 'port': '8080'}
```

`groupdict()` is how you get a whole record out in one step. Everything comes
back as **strings** — converting to int is your job, same as lesson 01.

Use `(?:...)` when you want grouping for a quantifier but don't want a capture:
`(?:\.\d+){3}` groups without cluttering `.groups()`.

**Substitution.** The replacement can reference groups with `\1`, `\2`, or
`\g<name>`:

```python
re.sub(r"(\w+)@(\w+)", r"\1@REDACTED", "bob@corp")   # 'bob@REDACTED'
```

Keep the replacement a raw string too, or `\1` becomes a control character.

**Flags.** `re.IGNORECASE` (`re.I`) is the one you want today. Pass it as
`flags=re.IGNORECASE`.

**Alternation** — `(a|b|c)` — matches any one branch. Building one from a
tuple is a common trick:

```python
"|".join(("cat", "dog"))          # 'cat|dog'
rf"\b({'|'.join(WORDS)})\b"       # an f-string AND a raw string
```

**Compiling.** `re.compile(p)` once at module level beats recompiling in a
loop, and gives the same methods: `PATTERN.search(s)`, `PATTERN.sub(r, s)`.
Python caches recent patterns, so it's about clarity as much as speed.

**When not to reach for regex.** Validating an IPv4 octet as 0-255 in pure
regex is `(25[0-5]|2[0-4]\d|[01]?\d?\d)` — write-only. Match the loose shape
with a regex, then check the range in Python. Regex is for *finding structure*;
Python is for *judging values*. You'll do exactly this in `extract_ips`.

Likewise, `str` methods beat regex when they fit: `.strip()`, `.startswith()`,
`.split("=", 1)`, `"x" in s`. Reach for `re` when the shape varies.

## Your task

Fill in the seven functions in `exercises.py`. Read the docstrings carefully —
the tests follow them literally. `parse_nginx_line` is the centrepiece; the
last two functions call it, so get it solid first.

```
cd ~/git/python-brushup
uv run --project lesson02 pytest lesson02 -q
```

`-k` filters: `NormalizeWs` `ParseDuration` `ExtractIps` `ParseNginxLine`
`RedactSecrets` `StatusClassCounts` `TopPaths`
