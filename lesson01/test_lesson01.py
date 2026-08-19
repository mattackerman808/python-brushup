import pytest

from exercises import (
    count_by,
    error_hosts,
    format_report,
    group_ms_by_path,
    parse_line,
    percentile,
    slowest,
)

LOG = """
2026-08-18T04:12:03Z INFO  web-01 status=200 path=/api/v1/users ms=42
2026-08-18T04:12:04Z INFO  web-02 status=200 path=/api/v1/users ms=91
2026-08-18T04:12:05Z ERROR web-01 status=500 path=/api/v1/orders ms=1503
2026-08-18T04:12:06Z WARN  web-03 status=429 path=/api/v1/users ms=7
2026-08-18T04:12:07Z FATAL web-04 status=503 path=/healthz ms=1
2026-08-18T04:12:08Z INFO  web-02 status=200 path=/api/v1/orders ms=250
"""


@pytest.fixture
def records():
    return [r for line in LOG.splitlines() if (r := parse_line(line)) is not None]


class TestParseLine:
    def test_basic(self):
        line = "2026-08-18T04:12:03Z INFO web-01 status=200 path=/api/v1/users ms=42"
        assert parse_line(line) == {
            "ts": "2026-08-18T04:12:03Z",
            "level": "INFO",
            "host": "web-01",
            "status": 200,
            "path": "/api/v1/users",
            "ms": 42,
        }

    def test_ints_are_ints(self):
        r = parse_line("t I h status=200 ms=42")
        assert r["status"] == 200 and isinstance(r["status"], int)
        assert r["ms"] == 42 and isinstance(r["ms"], int)

    def test_ragged_whitespace(self):
        assert parse_line("  t   I    h   ms=3  ") == {
            "ts": "t", "level": "I", "host": "h", "ms": 3,
        }

    def test_no_kv_pairs(self):
        assert parse_line("t I h") == {"ts": "t", "level": "I", "host": "h"}

    def test_bare_tokens_ignored(self):
        assert parse_line("t I h oops path=/x") == {
            "ts": "t", "level": "I", "host": "h", "path": "/x",
        }

    def test_value_containing_equals(self):
        r = parse_line("t I h path=/search?q=a=b")
        assert r["path"] == "/search?q=a=b"

    @pytest.mark.parametrize("line", ["", "   ", "\n", "t", "t I"])
    def test_junk_returns_none(self, line):
        assert parse_line(line) is None


class TestCountBy:
    def test_levels(self, records):
        assert count_by(records, "level") == {
            "INFO": 3, "ERROR": 1, "WARN": 1, "FATAL": 1,
        }

    def test_missing_key_skipped(self):
        assert count_by([{"level": "INFO"}, {"host": "a"}], "level") == {"INFO": 1}

    def test_empty(self):
        assert count_by([], "level") == {}

    def test_counts_non_string_values(self, records):
        assert count_by(records, "status")[200] == 3


class TestErrorHosts:
    def test_finds_error_and_fatal(self, records):
        assert error_hosts(records) == {"web-01", "web-04"}

    def test_empty(self):
        assert error_hosts([]) == set()

    def test_missing_fields_skipped(self):
        assert error_hosts([{"level": "ERROR"}, {"host": "a"}]) == set()


class TestSlowest:
    def test_top_three(self, records):
        assert [r["ms"] for r in slowest(records)] == [1503, 250, 91]

    def test_n_larger_than_input(self, records):
        assert len(slowest(records, 100)) == 6

    def test_returns_whole_records(self, records):
        assert slowest(records, 1)[0]["path"] == "/api/v1/orders"

    def test_ties_are_stable(self):
        rs = [{"id": "a", "ms": 5}, {"id": "b", "ms": 9}, {"id": "c", "ms": 5}]
        assert [r["id"] for r in slowest(rs, 3)] == ["b", "a", "c"]

    def test_skips_records_without_ms(self):
        assert slowest([{"ms": 1}, {"host": "x"}], 5) == [{"ms": 1}]


class TestGroupMsByPath:
    def test_grouping(self, records):
        assert group_ms_by_path(records) == {
            "/api/v1/users": [42, 91, 7],
            "/api/v1/orders": [1503, 250],
            "/healthz": [1],
        }

    def test_first_seen_order(self, records):
        assert list(group_ms_by_path(records)) == [
            "/api/v1/users", "/api/v1/orders", "/healthz",
        ]

    def test_empty(self):
        assert group_ms_by_path([]) == {}


class TestPercentile:
    @pytest.mark.parametrize(
        "values,p,expected",
        [
            ([1, 2, 3, 4], 50, 2),
            ([1, 2, 3, 4], 100, 4),
            ([1, 2, 3, 4], 1, 1),
            ([1, 2, 3, 4], 0, 1),
            ([42], 95, 42),
            ([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], 95, 100),
            ([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], 90, 90),
        ],
    )
    def test_nearest_rank(self, values, p, expected):
        assert percentile(values, p) == expected

    def test_unsorted_input(self):
        assert percentile([4, 1, 3, 2], 50) == 2

    def test_does_not_mutate(self):
        values = [3, 1, 2]
        percentile(values, 50)
        assert values == [3, 1, 2]

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            percentile([], 50)


class TestFormatReport:
    def test_layout(self, records):
        assert format_report(records) == (
            "/api/v1/users            3     91\n"
            "/api/v1/orders           2   1503\n"
            "/healthz                 1      1"
        )

    def test_empty(self):
        assert format_report([]) == ""

    def test_ties_sort_by_path(self):
        rs = [{"path": "/b", "ms": 1}, {"path": "/a", "ms": 1}]
        assert format_report(rs).splitlines()[0].startswith("/a")
