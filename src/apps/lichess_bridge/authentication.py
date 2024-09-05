# Packages such as django-allauth or AuthLib do provide turnkey Django integrations
# for OAuth2 - or even with Lichess specifically, for the former.
# However, in my case I don't want to use Django's "auth" machinery to manage Lichess
# users: all I want is to store in an HTTP-only cookie that they have attached
# a Lichess account, alongside with the token we'll need to communicate with Lichess.
# Hence, the following low level code, written after the Flask example given by Lichess:
# https://github.com/lakinwecker/lichess-oauth-flask/blob/master/app.py
# Authlib "vanilla Python" usage:
# https://docs.authlib.org/en/latest/client/oauth2.html

import functools
from typing import TYPE_CHECKING, Literal

import msgspec
from authlib.common.security import generate_token
from authlib.integrations.requests_client import OAuth2Session
from django.conf import settings
from django.urls import reverse

if TYPE_CHECKING:
    from typing import Self

LICHESS_OAUTH2_SCOPES = ("board:play",)


class LichessTokenRetrievalProcessContext(
    msgspec.Struct,
    kw_only=True,  # type: ignore[call-arg]
):
    """
    Short-lived data required to complete the retrieval of an API token
    from Lichess' OAuth2 process.
    """

    csrf_state: str
    code_verifier: str
    zakuchess_redirect_url: str  # an absolute HTTP/HTTPS URL

    def to_cookie_content(self) -> str:
        cookie_content = {
            # We don't encode the redirect URL into the cookie, so let's customise
            # what we need by encoding a dict, rather than "self"
            "csrf": self.csrf_state,
            "verif": self.code_verifier,
        }
        return msgspec.json.encode(cookie_content).decode()

    @classmethod
    def from_cookie_content(
        cls,
        cookie_content: str,
        *,
        zakuchess_hostname: str,
        zakuchess_protocol: str = "https",
    ) -> "Self":
        cookie_content_dict = msgspec.json.decode(cookie_content)
        redirect_uri = _get_lichess_oauth2_zakuchess_redirect_uri(
            zakuchess_protocol,
            zakuchess_hostname,
        )

        return cls(
            csrf_state=cookie_content_dict["csrf"],
            code_verifier=cookie_content_dict["verif"],
            zakuchess_redirect_url=redirect_uri,
        )

    @classmethod
    def create_afresh(
        cls,
        *,
        zakuchess_hostname: str,
        zakuchess_protocol: str = "https",
    ) -> "Self":
        """
        Returns a context with randomly generated "CSRF state" and "code verifier".
        """
        redirect_uri = _get_lichess_oauth2_zakuchess_redirect_uri(
            zakuchess_protocol, zakuchess_hostname
        )

        csrf_state = generate_token()
        code_verifier = generate_token(48)

        return cls(
            csrf_state=csrf_state,
            code_verifier=code_verifier,
            zakuchess_redirect_url=redirect_uri,
        )


class LichessToken(msgspec.Struct):
    token_type: Literal["Bearer"]
    access_token: str
    expires_in: int  # number of seconds
    expires_at: int  # a Unix timestamp


def get_lichess_token_retrieval_via_oauth2_process_starting_url(
    *,
    context: LichessTokenRetrievalProcessContext,
) -> str:
    lichess_authorization_endpoint = f"{settings.LICHESS_HOST}/oauth"

    client = _get_lichess_client()
    uri, state = client.create_authorization_url(
        lichess_authorization_endpoint,
        response_type="code",
        state=context.csrf_state,
        redirect_uri=context.zakuchess_redirect_url,
        code_verifier=context.code_verifier,
    )
    assert state == context.csrf_state

    return uri


def extract_lichess_token_from_oauth2_callback_url(
    *,
    authorization_callback_response_url: str,
    context: LichessTokenRetrievalProcessContext,
) -> LichessToken:
    lichess_token_endpoint = f"{settings.LICHESS_HOST}/api/token"

    client = _get_lichess_client()
    token_as_dict = client.fetch_token(
        lichess_token_endpoint,
        authorization_response=authorization_callback_response_url,
        redirect_uri=context.zakuchess_redirect_url,
        code_verifier=context.code_verifier,
    )

    return LichessToken(
        **token_as_dict,
    )


@functools.lru_cache
def _get_lichess_oauth2_zakuchess_redirect_uri(
    zakuchess_protocol: str, zakuchess_hostname: str
) -> str:
    return f"{zakuchess_protocol}://{zakuchess_hostname}" + reverse(
        "lichess_bridge:oauth2_token_callback"
    )


def _get_lichess_client() -> OAuth2Session:
    return OAuth2Session(
        client_id=settings.LICHESS_CLIENT_ID,
        code_challenge_method="S256",
        scope=" ".join(LICHESS_OAUTH2_SCOPES),
    )
