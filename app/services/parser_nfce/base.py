import re
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup


def safe_text(parent, selector, strip=True):
    """Get text from a CSS selector, returning None if not found."""
    el = parent.select_one(selector) if isinstance(selector, str) else selector
    if el is None:
        return None
    return el.get_text(strip=strip)


def br_to_float(text: str):
    """Convert Brazilian decimal string to float.

    Handles:
      - "17,9"  -> 17.9   (no trailing zero)
      - "2,39"  -> 2.39   (standard decimal)
      - "0,304" -> 0.304  (quantity with 3 decimals)
      - "1.234,56" -> 1234.56 (thousands sep)
      - "9.000"  -> 9.0   (point as thousands sep, no comma)
      - "269,00" -> 269.0
      - "NaN", "", None -> None
    """
    if text is None:
        return None
    text = text.strip()
    if not text or text.upper() in ("NAN", "NA", ""):
        return None
    text = re.sub(r"[^\d,.-]", "", text)
    if not text:
        return None
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    else:
        # No comma → last dot is the decimal separator
        parts = text.split(".")
        if len(parts) > 1:
            text = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return float(text)
    except ValueError:
        return None


def extract_br_number(text: str) -> float:
    """Alias for br_to_float for backward compatibility."""
    return br_to_float(text)


def parse_address(address_text: str) -> dict:
    """Parse endereço string into components.

    Formato esperado: "Logradouro, Número, Complemento, Bairro, Cidade, UF"
    """
    parts = [p.strip() for p in address_text.split(",")]
    return {
        "logradouro": parts[0] if len(parts) > 0 else "",
        "numero": parts[1] if len(parts) > 1 else "",
        "complemento": parts[2] if len(parts) > 2 else "",
        "bairro": parts[3] if len(parts) > 3 else "",
        "cidade": parts[4] if len(parts) > 4 else "",
        "uf": parts[5] if len(parts) > 5 else "",
    }


def extract_text_by_label(infos_text: str, label: str) -> str:
    """Extract text after a label in the infos text block."""
    pattern = re.compile(re.escape(label) + r"\s*[:]\s*(.+?)(?:\n|$)", re.DOTALL)
    match = pattern.search(infos_text)
    if match:
        return match.group(1).strip()
    pattern2 = re.compile(re.escape(label) + r"\s+(.+?)(?:\n|$)", re.DOTALL)
    match2 = pattern2.search(infos_text)
    if match2:
        return match2.group(1).strip()
    return None


class NotaExtraida:
    def __init__(
        self,
        empresa: str,
        chave: str,
        numero: str,
        serie: str,
        emissao: str,
        items: list,
        valor_total: float,
        qtd_total_itens: int = None,
        extra: dict = None,
    ):
        self.empresa = empresa
        self.chave = chave
        self.numero = numero
        self.serie = serie
        self.emissao = emissao
        self.items = items
        self._valor_total = valor_total
        self.qtd_total_itens = qtd_total_itens
        self.extra = extra or {}

    @property
    def valor_total(self) -> float:
        return self._valor_total


class BaseParser(ABC):
    """Abstract base parser for NFC-e HTML pages."""

    @abstractmethod
    def parse_nfce(self, html_bytes: bytes) -> NotaExtraida:
        """Parse NFC-e HTML into a structured result."""
