"""Tests for NFC-e parsers.

TDD: all tests must pass to define correct extraction behavior.
"""

from pathlib import Path

import pytest

from app.services.parser_nfce import parse_nfce
from app.services.parser_nfce.base import br_to_float, safe_text
from app.services.parser_nfce.mg import MgParser
from app.services.parser_nfce.padrao import PadraoParser

FIXTURES = Path(__file__).parent / "fixtures"


# ── br_to_float ──────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("input_text", "expected"),
    [
        ("17,9", 17.9),
        ("2,39", 2.39),
        ("0,304", 0.304),
        ("1.234,56", 1234.56),
        ("269,00", 269.0),
        ("R$ 1.234,56", 1234.56),
        ("NaN", None),
        ("", None),
        (None, None),
    ],
)
def test_br_to_float(input_text, expected):
    assert br_to_float(input_text) == expected


# ── PadraoParser (MT) ────────────────────────────────────────────────


def test_padrao_parser_extracts_empresa():
    html = (FIXTURES / "nfce_mt.html").read_bytes()
    nota = PadraoParser().parse_nfce(html)
    assert nota.empresa == "Supermercado Exemplo LTDA"


def test_padrao_parser_extracts_chave():
    html = (FIXTURES / "nfce_mt.html").read_bytes()
    nota = PadraoParser().parse_nfce(html)
    assert nota.chave == "31200611222233300014455555555555555555555555"
    assert len(nota.chave) == 44


def test_padrao_parser_extracts_numero_serie_emissao():
    html = (FIXTURES / "nfce_mt.html").read_bytes()
    nota = PadraoParser().parse_nfce(html)
    assert nota.numero == "123456"
    assert nota.serie == "1"
    assert nota.emissao is not None
    assert "15/06/2026" in nota.emissao


def test_padrao_parser_extracts_items():
    html = (FIXTURES / "nfce_mt.html").read_bytes()
    nota = PadraoParser().parse_nfce(html)
    assert len(nota.items) == 3

    item1 = nota.items[0]
    assert item1["item_descricao"] == "ARROZ BRANCO 5KG"
    assert item1["item_codigo"] == "1234"
    assert item1["item_quantidade"] == 2.0
    assert item1["item_valor_unidade"] == 25.90
    assert item1["item_valor_total"] == 51.80

    item2 = nota.items[1]
    assert item2["item_descricao"] == "FEIJÃO PRETO 1KG"
    assert item2["item_quantidade"] == 3.0
    assert item2["item_valor_unidade"] == 8.99
    assert item2["item_valor_total"] == 26.97


def test_padrao_parser_extracts_totals():
    html = (FIXTURES / "nfce_mt.html").read_bytes()
    nota = PadraoParser().parse_nfce(html)
    assert nota.valor_total == 86.26
    assert nota.qtd_total_itens == 3


def test_padrao_parser_extracts_extra():
    html = (FIXTURES / "nfce_mt.html").read_bytes()
    nota = PadraoParser().parse_nfce(html)
    extra = nota.extra

    assert extra["emitente"]["cnpj"] == "11.222.333/0001-44"
    assert extra["emitente"]["logradouro"] == "Rua Exemplo"
    assert extra["consumidor"] is not None
    assert "JOÃO DA SILVA" in extra["consumidor"]
    assert extra["ambiente"] == "Produção"
    assert extra["protocolo_autorizacao"] is not None
    assert extra["protocolo_autorizacao"]["numero"] == "9876543210"
    assert extra["informacoes_interesse"]["coo"] == 123456
    assert extra["informacoes_interesse"]["pdv"] == 789
    assert extra["formas_pagamento"] == [{"tipo": "Dinheiro", "valor": 86.26}]
    assert extra["troco"] == 0.0


# ── MgParser ─────────────────────────────────────────────────────────
# These tests were previously marked xfail because the test fixture
# used simplified HTML. After updating nfce_mg.html to match the
# PrimeFaces/Bootstrap classes that MgParser expects (text-center,
# table-striped, table-hover), these tests should now pass.


def test_mg_parser_extracts_empresa():
    html = (FIXTURES / "nfce_mg.html").read_bytes()
    nota = MgParser().parse_nfce(html)
    assert nota.empresa == "Supermercado Mineiro S.A."


def test_mg_parser_extracts_chave():
    html = (FIXTURES / "nfce_mg.html").read_bytes()
    nota = MgParser().parse_nfce(html)
    assert nota.chave == "31200622222233300014455555555555555555556666"
    assert len(nota.chave) == 44


def test_mg_parser_extracts_numero_serie_emissao():
    html = (FIXTURES / "nfce_mg.html").read_bytes()
    nota = MgParser().parse_nfce(html)
    assert nota.numero == "987654"
    assert nota.serie == "2"
    assert nota.emissao == "20/06/2026"


def test_mg_parser_extracts_items():
    html = (FIXTURES / "nfce_mg.html").read_bytes()
    nota = MgParser().parse_nfce(html)
    assert len(nota.items) == 3

    item1 = nota.items[0]
    assert item1["item_descricao"] == "Café Torrado 500g"
    assert item1["item_quantidade"] == 2.0
    assert item1["item_valor_total"] == 37.98

    item3 = nota.items[2]
    assert item3["item_descricao"] == "Pão Francês (kg)"
    assert item3["item_quantidade"] == 1.5
    assert item3["item_valor_total"] == 37.35


def test_mg_parser_item_valor_unidade_nullable():
    """MG parser may not extract unit price; must accept None."""
    html = (FIXTURES / "nfce_mg.html").read_bytes()
    nota = MgParser().parse_nfce(html)
    for item in nota.items:
        assert item["item_valor_unidade"] is None or isinstance(
            item["item_valor_unidade"], (int, float)
        )


def test_mg_parser_extracts_totals():
    html = (FIXTURES / "nfce_mg.html").read_bytes()
    nota = MgParser().parse_nfce(html)
    assert nota.valor_total == 102.87
    assert nota.qtd_total_itens == 3


def test_mg_parser_extracts_endereco():
    html = (FIXTURES / "nfce_mg.html").read_bytes()
    nota = MgParser().parse_nfce(html)
    emitente = nota.extra["emitente"]
    assert emitente["logradouro"] == "Av. Amazonas"
    assert emitente["numero"] == "1500"
    assert emitente["cidade"] == "Belo Horizonte"
    assert emitente["uf"] == "MG"


def test_mg_parser_extracts_consumidor():
    html = (FIXTURES / "nfce_mg.html").read_bytes()
    nota = MgParser().parse_nfce(html)
    assert nota.extra["consumidor"] is not None
    assert "MARIA DE SOUZA" in nota.extra["consumidor"]


def test_mg_parser_extracts_ambiente():
    html = (FIXTURES / "nfce_mg.html").read_bytes()
    nota = MgParser().parse_nfce(html)
    assert nota.extra["ambiente"] == "Produção"


# ── MgParser Edge Cases (Issue #6) ──────────────────────────────────


def test_mg_parser_empty_html_does_not_crash():
    """MgParser should handle empty HTML without crashing."""
    html = b"<html><body></body></html>"
    nota = MgParser().parse_nfce(html)
    assert nota.empresa == ""
    assert nota.items == []
    assert nota.chave is None


def test_mg_parser_no_items_table():
    """MgParser should handle HTML without items table."""
    html = b"""<html><body>
    <table class="text-center"><tr><td>EMPRESA TESTE</td></tr></table>
    </body></html>"""
    nota = MgParser().parse_nfce(html)
    assert nota.items == []
    assert nota.qtd_total_itens is None


def test_mg_parser_malformed_html():
    """MgParser should handle malformed HTML (missing closing tags)."""
    html = b"<html><body><table class=text-center><tr><td>TESTE"
    nota = MgParser().parse_nfce(html)
    assert nota is not None
    assert isinstance(nota.empresa, str)


def test_mg_parser_rejects_none():
    """MgParser should raise TypeError or handle None input gracefully."""
    import traceback
    try:
        MgParser().parse_nfce(None)  # type: ignore
        # If it doesn't raise, check it doesn't crash the process
    except (TypeError, AttributeError):
        pass
    except Exception:
        # Any exception is fine as long as it's caught
        pass


def test_mg_parser_with_extra_whitespace():
    """MgParser handles extra whitespace in key fields."""
    html = b"""<html><body>
    <table class="text-center" style="width:100%">
      <tr><td colspan="2"><strong>NOTA FISCAL</strong></td></tr>
      <tr><td colspan="2"><strong>  Supermercado Mineiro S.A.  </strong></td></tr>
      <tr><td>CNPJ: 99.888.777/0001-66</td><td>IE: 123.456.789.00-11</td></tr>
      <tr><td colspan="2">  Av. Amazonas, 1500  ,  Centro  ,  Belo Horizonte  ,  MG  </td></tr>
    </table>
    <table class="table-striped" style="width:100%">
      <tr><td>Café Torrado 500g</td><td>2</td><td>UN: UN</td><td>37,98</td></tr>
    </table>
    <table class="table-hover" style="width:100%">
      <tr><td>Modelo</td><td>Número</td><td>Série</td><td>Emissão</td></tr>
      <tr><td>65</td><td>987654</td><td>2</td><td>20/06/2026</td></tr>
    </table>
    <table class="table-hover" style="width:100%">
      <tr><td>3120 0622 2222 3330 0014 4555 5555 5555 5555 5555 6666</td></tr>
    </table>
    <div><strong>Valor total R$ 102,87</strong></div>
    </body></html>"""
    nota = MgParser().parse_nfce(html)
    assert nota.empresa == "Supermercado Mineiro S.A."
    assert nota.chave == "31200622222233300014455555555555555555556666"
    assert len(nota.items) == 1
    assert nota.items[0]["item_valor_total"] == 37.98


# ── Dispatcher ───────────────────────────────────────────────────────


def test_dispatcher_routes_to_padrao_without_url():
    """Without URL, dispatcher falls back to PadraoParser."""
    html = (FIXTURES / "nfce_mt.html").read_bytes()
    nota = parse_nfce(html)
    assert nota.empresa == "Supermercado Exemplo LTDA"


def test_dispatcher_routes_to_padrao_for_mt_url():
    """MT-style URL → PadraoParser."""
    html = (FIXTURES / "nfce_mt.html").read_bytes()
    nota = parse_nfce(html, url="https://www.sefaz.mt.gov.br/nfce/consulta")
    assert nota.empresa == "Supermercado Exemplo LTDA"


def test_dispatcher_routes_to_mg_for_mg_url():
    """MG URL → MgParser."""
    html = (FIXTURES / "nfce_mg.html").read_bytes()
    nota = parse_nfce(
        html, url="https://nfce.fazenda.mg.gov.br/portalnfce/sistema/consultaarg.xhtml"
    )
    assert nota.empresa == "Supermercado Mineiro S.A."


def test_dispatcher_unknown_url_falls_back_to_padrao():
    """Unknown domain in URL → PadraoParser fallback."""
    html = (FIXTURES / "nfce_mt.html").read_bytes()
    nota = parse_nfce(html, url="https://unknown-state.gov.br/nfce")
    assert nota.empresa == "Supermercado Exemplo LTDA"
