"""NFC-e parser package — dispatcher with UF-specific parsers."""

from app.services.parser_nfce.base import NotaExtraida, safe_text, br_to_float
from app.services.parser_nfce.padrao import PadraoParser
from app.services.parser_nfce.mg import MgParser


_PARSERS_BY_DOMAIN = {}


def register_parser(domain: str, parser_cls):
    _PARSERS_BY_DOMAIN[domain.lower()] = parser_cls


def _detect_parser(url: str | None = None):
    """Detect which parser to use based on URL domain.

    Falls back to PadraoParser (MT-style) when URL is None or unknown.
    """
    if url:
        from urllib.parse import urlparse

        hostname = urlparse(url).hostname or ""
        for domain, cls in _PARSERS_BY_DOMAIN.items():
            if domain in hostname.lower():
                return cls()
    return PadraoParser()


def parse_nfce(html_bytes: bytes, url: str | None = None) -> NotaExtraida:
    """Parse NFC-e HTML, dispatching to the correct UF parser.

    Parameters
    ----------
    html_bytes :
        Raw HTML content of the NFC-e page.
    url :
        Optional URL of the page used to detect the correct parser.
        When ``None`` or unknown, falls back to the padrão (MT-style)
        parser.

    Returns
    -------
    NotaExtraida
        Structured extraction result.
    """
    parser = _detect_parser(url)
    return parser.parse_nfce(html_bytes)


# ── Register known parsers ──────────────────────────────────────────
register_parser("mg.gov.br", MgParser)
