import os

import pytest

from tests.conftest import TEST_API_KEY
from xai_cli.api import create_answer

pytestmark = pytest.mark.live


@pytest.mark.skipif(
    os.environ.get("XAI_LIVE_TEST") != "1" or not os.environ.get("XAI_API_KEY"),
    reason="Set XAI_LIVE_TEST=1 and XAI_API_KEY to run live API tests.",
)
def test_live_x_search_returns_sources():
    assert os.environ["XAI_API_KEY"] != TEST_API_KEY
    answer = create_answer(
        "In one sentence, what did xAI announce recently?",
        {"type": "x_search", "allowed_x_handles": ["xai"]},
    )
    assert answer.text
    if answer.usage["server_side_tool_usage_details"].get("x_posts_fetched"):
        assert answer.sources
