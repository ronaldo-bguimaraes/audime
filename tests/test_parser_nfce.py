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
