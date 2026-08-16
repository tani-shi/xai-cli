import os

import pytest

from xai_cli.client.responses import build_x_search_request
from xai_cli.client.transport import ApiClient
from xai_cli.config import DEFAULT_MODEL

pytestmark = pytest.mark.live


@pytest.mark.skipif(
    os.environ.get("XAI_LIVE_TEST") != "1" or not os.environ.get("XAI_API_KEY"),
    reason="Set XAI_LIVE_TEST=1 and XAI_API_KEY to run live API tests.",
)
def test_live_x_search_response():
    request = build_x_search_request(
        "In one sentence, what is the xAI API? Cite a current xAI source.",
        DEFAULT_MODEL,
        stream=False,
        allowed_handles=["xai"],
    )
    with ApiClient(os.environ["XAI_API_KEY"]) as client:
        response = client.create_response(request)
    assert response.text
