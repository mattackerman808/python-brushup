import pytest

from exercises import (
    extract_ips,
    normalize_ws,
    parse_duration,
    parse_nginx_line,
    redact_secrets,
    status_class_counts,
    top_paths,
)

LINE = '10.0.0.1 - - [18/Aug/2026:04:12:03 +0000] "GET /api/v1/users HTTP/1.1" 200 1234'

LOG = """
10.0.0.1 - - [18/Aug/2026:04:12:03 +0000] "GET /api/v1/users HTTP/1.1" 200 1234
10.0.0.2 - - [18/Aug/2026:04:12:04 +0000] "GET /api/v1/users HTTP/1.1" 200 980
10.0.0.1 - - [18/Aug/2026:04:12:05 +0000] "POST /api/v1/orders HTTP/1.1" 500 77
10.0.0.3 - - [18/Aug/2026:04:12:06 +0000] "GET /healthz HTTP/1.1" 200 2
this is not a log line at all
10.0.0.2 - - [18/Aug/2026:04:12:07 +0000] "GET /api/v1/orders HTTP/1.1" 404 -
10.0.0.4 - - [18/Aug/2026:04:12:08 +0000] "GET /api/v1/users HTTP/1.1" 301 512
"""


@pytest.fixture
def lines():
    return [line for line in LOG.splitlines() if line]


class TestNormalizeWs:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("  web-01\t\tis   down\n", "web-01 is down"),
            ("already clean", "already clean"),
            ("   ", ""),
            ("", ""),
            ("a\n\n\nb", "a b"),
            ("\tlead and trail\t", "lead and trail"),
            ("one", "one"),
        ],
    )
    def test_collapse(self, raw, expected):
        assert normalize_ws(raw) == expected

    def test_single_spaces_survive(self):
        assert normalize_ws("GET /a HTTP/1.1") == "GET /a HTTP/1.1"


class TestParseDuration:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("1h30m", 5400),
            ("45s", 45),
            ("2h", 7200),
            ("90m", 5400),
            ("1h 30m", 5400),
            ("2H 15M", 8100),
            ("1h2m3s", 3723),
            ("  30s  ", 30),
            ("0s", 0),
        ],
    )
    def test_parses(self, text, expected):
        assert parse_duration(text) == expected

    @pytest.mark.parametrize("text", ["", "   ", "abc", "30", "h", "30x", "1h junk"])
    def test_bad_input_raises(self, text):
        with pytest.raises(ValueError):
            parse_duration(text)


class TestExtractIps:
    def test_order_and_dedup(self):
        text = "from 10.0.0.1 to 10.0.0.2, retry 10.0.0.1"
        assert extract_ips(text) == ["10.0.0.1", "10.0.0.2"]

    def test_embedded_in_punctuation(self):
        assert extract_ips("host=192.168.1.10;port=443") == ["192.168.1.10"]

    def test_rejects_out_of_range(self):
        assert extract_ips("999.1.1.1 and 256.0.0.1 and 1.2.3.4") == ["1.2.3.4"]

    def test_rejects_too_few_groups(self):
        assert extract_ips("version 1.2.3 released") == []

    def test_no_ips(self):
        assert extract_ips("nothing to see here") == []

    def test_empty(self):
        assert extract_ips("") == []

    def test_boundary_values(self):
        assert extract_ips("0.0.0.0 255.255.255.255") == ["0.0.0.0", "255.255.255.255"]


class TestParseNginxLine:
    def test_basic(self):
        assert parse_nginx_line(LINE) == {
            "ip": "10.0.0.1",
            "ts": "18/Aug/2026:04:12:03 +0000",
            "method": "GET",
            "path": "/api/v1/users",
            "status": 200,
            "bytes": 1234,
        }

    def test_ints_are_ints(self):
        record = parse_nginx_line(LINE)
        assert record["status"] == 200 and isinstance(record["status"], int)
        assert record["bytes"] == 1234 and isinstance(record["bytes"], int)

    def test_dash_bytes_is_zero(self):
        line = '10.0.0.2 - - [t] "GET /a HTTP/1.1" 404 -'
        assert parse_nginx_line(line)["bytes"] == 0

    def test_post_method(self):
        line = '10.0.0.1 - - [t] "POST /api/v1/orders HTTP/1.1" 500 77'
        record = parse_nginx_line(line)
        assert record["method"] == "POST"
        assert record["path"] == "/api/v1/orders"

    def test_path_with_query_string(self):
        line = '10.0.0.1 - - [t] "GET /search?q=web-01&n=5 HTTP/1.1" 200 9'
        assert parse_nginx_line(line)["path"] == "/search?q=web-01&n=5"

    @pytest.mark.parametrize(
        "line",
        ["", "this is not a log line at all", "10.0.0.1 - - nope", "   "],
    )
    def test_garbage_returns_none(self, line):
        assert parse_nginx_line(line) is None


class TestRedactSecrets:
    def test_basic(self):
        assert (
            redact_secrets("user=bob password=hunter2 host=web-01")
            == "user=bob password=*** host=web-01"
        )

    def test_all_keys(self):
        text = "token=abc secret=def api_key=ghi password=jkl"
        assert redact_secrets(text) == "token=*** secret=*** api_key=*** password=***"

    def test_key_case_is_preserved(self):
        assert redact_secrets("PASSWORD=hunter2") == "PASSWORD=***"

    def test_case_insensitive_match(self):
        assert redact_secrets("Token=abc123") == "Token=***"

    def test_unrelated_keys_untouched(self):
        text = "user=bob host=web-01 status=200"
        assert redact_secrets(text) == text

    def test_no_matches_unchanged(self):
        assert redact_secrets("nothing secret here") == "nothing secret here"

    def test_value_with_punctuation(self):
        assert redact_secrets("token=a1b2-c3/d4+e5=") == "token=***"


class TestStatusClassCounts:
    def test_counts(self, lines):
        assert status_class_counts(lines) == {"2xx": 3, "5xx": 1, "4xx": 1, "3xx": 1}

    def test_skips_unparseable(self):
        assert status_class_counts(["garbage", ""]) == {}

    def test_empty(self):
        assert status_class_counts([]) == {}


class TestTopPaths:
    def test_ranking(self, lines):
        assert top_paths(lines, 3) == [
            ("/api/v1/users", 3),
            ("/api/v1/orders", 2),
            ("/healthz", 1),
        ]

    def test_respects_n(self, lines):
        assert top_paths(lines, 1) == [("/api/v1/users", 3)]

    def test_default_n_is_3(self, lines):
        assert len(top_paths(lines)) == 3

    def test_fewer_than_n(self):
        line = '10.0.0.1 - - [t] "GET /a HTTP/1.1" 200 1'
        assert top_paths([line], 5) == [("/a", 1)]

    def test_ties_sort_by_path(self):
        rs = [
            '10.0.0.1 - - [t] "GET /b HTTP/1.1" 200 1',
            '10.0.0.1 - - [t] "GET /a HTTP/1.1" 200 1',
        ]
        assert top_paths(rs, 2) == [("/a", 1), ("/b", 1)]

    def test_empty(self):
        assert top_paths([], 3) == []
