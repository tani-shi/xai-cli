import json

from xai_cli.client.models import Answer
from xai_cli.output import write_answer, write_markdown, write_text


def test_print_json(capsys):
    answer = Answer(
        response_id="resp_1",
        model="grok-4.6",
        status="completed",
        text="hello",
        citations=["https://example.com"],
    )
    write_answer(answer)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data == {
        "schema_version": 1,
        "response_id": "resp_1",
        "model": "grok-4.6",
        "status": "completed",
        "text": "hello",
        "citations": ["https://example.com"],
    }
    assert captured.err == ""


def test_print_text(capsys):
    write_text("hello **world**")
    captured = capsys.readouterr()
    assert captured.out == "hello **world**\n"
    assert captured.err == ""


def test_markdown_is_preserved_when_piped(capsys):
    write_markdown("# Heading\n\n[Source](https://example.com)")
    captured = capsys.readouterr()
    assert captured.out == "# Heading\n\n[Source](https://example.com)\n"
