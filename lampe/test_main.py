# Run on a PC with: python lampe/test_main.py
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from main import parse, texts  # noqa: E402

assert parse('{"p":"focus","left":720,"free":"14:35"}') == ("focus", 720, "14:35")
assert parse('{"p":"break","left":300,"free":"9:05"}') == ("break", 300, "9:05")
assert parse('{"p":"paused","left":61}') == ("paused", 61, "")
assert parse('{"p":"idle"}') == ("idle", 0, "")
for bad in ['', 'garbage', '[]', '{"p":"party"}', '{"p":"focus"}', '{"p":"focus","left":-1}',
            '{"p":"focus","left":true}', '{"p":"focus","left":1.5}', '{"p":"focus","left":99999}',
            '{"p":"focus","left":60,"free":"25:00"}', '{"p":"focus","left":60,"free":"<b>"}',
            '{"p":"focus","left":60,"free":7}', '{"p":"idle","x":"' + 'a' * 300 + '"}']:
    assert parse(bad) is None, bad

assert texts("idle", 0, "") == ["LEDIG"]
assert texts("focus", 720, "14:35") == ["FOKUS", "12 min", "til 14:35"]
assert texts("focus", 61, "") == ["FOKUS", "2 min"]
assert texts("break", 45, "") == ["PAUSE", "45 s"]
print("ok")
