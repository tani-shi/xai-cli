from datetime import date

from xai_cli.client.responses import build_web_search_request, build_x_search_request


def dump(request):
    return request.model_dump(mode="json", exclude_none=True)


def test_minimal_x_search_payload_exact():
    request = build_x_search_request("query", "grok-4.6", stream=True)

    assert dump(request) == {
        "model": "grok-4.6",
        "input": [{"role": "user", "content": "query"}],
        "tools": [{"type": "x_search"}],
        "stream": True,
    }


def test_complete_x_search_payload_exact():
    request = build_x_search_request(
        "query",
        "grok-4.6",
        stream=False,
        allowed_handles=["@xai", "elonmusk"],
        from_date=date(2026, 1, 2),
        to_date=date(2026, 3, 4),
        enable_images=True,
        enable_video=True,
    )

    assert dump(request) == {
        "model": "grok-4.6",
        "input": [{"role": "user", "content": "query"}],
        "tools": [
            {
                "type": "x_search",
                "allowed_x_handles": ["xai", "elonmusk"],
                "from_date": "2026-01-02",
                "to_date": "2026-03-04",
                "enable_image_understanding": True,
                "enable_video_understanding": True,
            }
        ],
        "stream": False,
    }


def test_web_search_domains_are_nested_under_filters():
    request = build_web_search_request(
        "query",
        "grok-4.6",
        stream=False,
        allowed_domains=["Example.COM", "docs.x.ai"],
    )

    assert dump(request) == {
        "model": "grok-4.6",
        "input": [{"role": "user", "content": "query"}],
        "tools": [
            {
                "type": "web_search",
                "filters": {"allowed_domains": ["example.com", "docs.x.ai"]},
            }
        ],
        "stream": False,
    }


def test_web_search_excluded_domains_payload_exact():
    request = build_web_search_request(
        "query",
        "grok-4.6",
        stream=True,
        excluded_domains=["spam.example"],
    )

    assert dump(request)["tools"] == [
        {
            "type": "web_search",
            "filters": {"excluded_domains": ["spam.example"]},
        }
    ]
