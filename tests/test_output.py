import json

from xai_cli.output import print_json, print_text


def test_print_json(capsys):
    print_json({"key": "value"})
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data == {"key": "value"}


def test_print_text(capsys):
    print_text("hello world")
    captured = capsys.readouterr()
    assert "hello" in captured.out
