from typing import TYPE_CHECKING

from dominate.tags import section
from dominate.util import raw

from apps.lichess_bridge.authentication import (
    get_lichess_token_retrieval_via_oauth2_process_starting_url,
)
from apps.webui.components.layout import page

if TYPE_CHECKING:
    from django.http import HttpRequest

    from apps.lichess_bridge.authentication import (
        LichessTokenRetrievalProcessContext,
    )


def lichess_no_account_linked_page(
    *,
    request: "HttpRequest",
    lichess_oauth2_process_context: "LichessTokenRetrievalProcessContext",
) -> str:
    target_url = get_lichess_token_retrieval_via_oauth2_process_starting_url(
        context=lichess_oauth2_process_context
    )

    return page(
        section(
            raw(f"""Click here: <a href="{target_url}">{target_url}</a>"""),
            cls="text-slate-50",
        ),
        request=request,
        title="Lichess - no account linked",
    )
