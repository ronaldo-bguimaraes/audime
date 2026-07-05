"""Minas Gerais NFC-e parser.

MG uses a JSF + PrimeFaces + Bootstrap layout that is structurally
different from the MT-style jQuery Mobile template.

Key differences from MT:
  - Company name in ``.nome-empresa`` or a header span
  - Items in a PrimeFaces ``.ui-datatable-data`` table
  - Each row has ``<td>`` elements with description, qty, unit, total
  - Total values in a footer section
  - No unit price per item (only total per item)
  - Chave (access key) in a distinct ``.chave`` or ``#chave`` element
"""

import re

from bs4 import BeautifulSoup

from app.services.parser_nfce.base import (
    BaseParser,
    NotaExtraida,
    br_to_float,
    safe_text,
)


class MgParser(BaseParser):
    """Parser for Minas Gerais NFC-e layout (JSF + PrimeFaces + Bootstrap)."""

    def parse_nfce(self, html_bytes: bytes) -> NotaExtraida:
        soup = BeautifulSoup(html_bytes, "html.parser")

        # ── Dados do emitente ───────────────────────────────────────────
        empresa = (
            safe_text(soup, ".nome-empresa")
            or safe_text(soup, ".emitente")
            or safe_text(soup, "span.empresa")
            or self._fallback_empresa(soup)
        )

        cnpj = self._extract_cnpj(soup)

        endereco = self._extract_endereco(soup)

        # ── Items ───────────────────────────────────────────────────────
        items = []
        for row in soup.select(".ui-datatable-data tr:not(.ui-datatable-empty)"):
            tds = row.find_all("td")
            if len(tds) < 4:
                # Try another common PrimeFaces pattern
                items = self._extract_items_alt(soup)
                if items:
                    break
                continue

            descricao = self._cell_text(tds[0])
            quantidade = br_to_float(self._cell_text(tds[1])) or 1.0
            # In MG, unit price is often not shown; try to extract or leave None
            valor_unidade_input = br_to_float(self._cell_text(tds[2]))
            valor_total_item = br_to_float(self._cell_text(tds[3])) or 0.0

            # Some MG layouts swap qty/unit columns
            if (
                valor_unidade_input is None
                and quantidade <= 1.0
                and valor_total_item > 0
            ):
                # If qty=1 and no unit price, assume col 2 is also qty-like
                # and col 1 might be unit price (less common)
                pass

            items.append(
                {
                    "item_codigo": None,
                    "item_descricao": descricao,
                    "item_quantidade": quantidade,
                    "item_tipo_unidade": "UN",
                    "item_valor_unidade": valor_unidade_input,
                    "item_valor_total": round(valor_total_item, 2),
                }
            )

        if not items:
            items = self._extract_items_alt(soup)

        if not items:
            items = self._extract_items_table(soup)

        # ── Totais ──────────────────────────────────────────────────────
        valor_total, qtd_total_itens = self._extract_totals(soup, items)

        # ── Número, Série, Emissão ──────────────────────────────────────
        numero, serie, emissao = self._extract_nota_info(soup)

        # ── Chave ───────────────────────────────────────────────────────
        chave = self._extract_chave(soup)

        # ── Consumidor ──────────────────────────────────────────────────
        consumidor = self._extract_consumidor(soup)

        # ── Formas de pagamento ─────────────────────────────────────────
        formas_pagamento, troco = self._extract_pagamento(soup)

        # ── Extra ───────────────────────────────────────────────────────
        extra = {
            "emitente": {
                "cnpj": cnpj,
                **endereco,
            },
            "protocolo_autorizacao": None,
            "formas_pagamento": formas_pagamento,
            "consumidor": consumidor,
            "ambiente": self._extract_ambiente(soup),
            "informacoes_interesse": {},
            "troco": troco,
        }

        return NotaExtraida(
            empresa=empresa,
            chave=chave,
            numero=numero,
            serie=serie,
            emissao=emissao,
            items=items,
            valor_total=valor_total,
            qtd_total_itens=qtd_total_itens,
            extra=extra,
        )

    # ── Helper methods ─────────────────────────────────────────────────

    @staticmethod
    def _cell_text(td) -> str:
        """Get clean text from a table cell."""
        if td is None:
            return ""
        return td.get_text(strip=True)

    @staticmethod
    def _fallback_empresa(soup) -> str:
        """Last-resort company name extraction."""
        # Try first header or bold text in the top section
        for selector in [".topo h1", ".cabecalho h1", "header h1", ".header span"]:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(strip=True)
                if text:
                    return text
        return ""

    @staticmethod
    def _extract_cnpj(soup) -> str | None:
        cnpj_patterns = [
            r"CNPJ[:\s]*([\d./-]+)",
            r"CPF[:\s]*([\d./-]+)",
            r"CNPJ/CPF[:\s]*([\d./-]+)",
        ]
        for selector in [".cnpj", ".cpf", ".text-info", ".infos", "body"]:
            el = soup.select_one(selector)
            if el:
                text = el.get_text()
                for pat in cnpj_patterns:
                    m = re.search(pat, text)
                    if m:
                        return m.group(1)
        return None

    @staticmethod
    def _extract_endereco(soup) -> dict:
        endereco = {"logradouro": "", "numero": "", "complemento": "", "bairro": "", "cidade": "", "uf": ""}
        addr_el = soup.select_one(".endereco") or soup.select_one(".address")
        if addr_el:
            text = addr_el.get_text(strip=True)
            from app.services.parser_nfce.base import parse_address
            return parse_address(text)
        return endereco

    def _extract_items_alt(self, soup) -> list:
        """Fallback: try alternative item table layouts."""
        items = []
        for table in soup.select("table:has(.item-descricao)"):
            for row in table.select("tr")[1:]:  # skip header
                tds = row.find_all("td")
                if len(tds) >= 2:
                    descricao = self._cell_text(tds[0])
                    valor_text = self._cell_text(tds[-1])
                    valor_total_item = br_to_float(valor_text) or 0.0
                    items.append({
                        "item_codigo": None,
                        "item_descricao": descricao,
                        "item_quantidade": 1.0,
                        "item_tipo_unidade": "UN",
                        "item_valor_unidade": None,
                        "item_valor_total": round(valor_total_item, 2),
                    })
        return items

    def _extract_items_table(self, soup) -> list:
        """Last-resort: any table with multiple rows in the main content."""
        items = []
        main = soup.select_one("#conteudo, .conteudo, main, body")
        if not main:
            main = soup
        for table in main.find_all("table"):
            rows = table.find_all("tr")
            if len(rows) <= 2:
                continue
            for row in rows[1:]:
                tds = row.find_all("td")
                if len(tds) >= 2:
                    descricao = self._cell_text(tds[0])
                    valor_text = self._cell_text(tds[-1])
                    valor_total_item = br_to_float(valor_text) or 0.0
                    if descricao and valor_total_item > 0:
                        items.append({
                            "item_codigo": None,
                            "item_descricao": descricao,
                            "item_quantidade": 1.0,
                            "item_tipo_unidade": "UN",
                            "item_valor_unidade": None,
                            "item_valor_total": round(valor_total_item, 2),
                        })
        return items

    @staticmethod
    def _extract_totals(soup, items) -> tuple:
        valor_total = None
        qtd_total_itens = None

        for selector in [".valor-total", ".total", "#total", ".total-nota"]:
            el = soup.select_one(selector)
            if el:
                val = br_to_float(el.get_text(strip=True))
                if val is not None:
                    valor_total = val
                    break

        if valor_total is None:
            valor_total = round(sum(i["item_valor_total"] for i in items), 2)
        qtd_total_itens = len(items) if items else None

        return valor_total, qtd_total_itens

    @staticmethod
    def _extract_nota_info(soup) -> tuple:
        numero = None
        serie = None
        emissao = None

        infos_el = soup.select_one(".infos-nota, .infos, #infos, .dados-nota")
        if infos_el:
            text = infos_el.get_text()
            num_match = re.search(r"N[º°]\.?:?\s*(\d+)", text)
            if num_match:
                numero = num_match.group(1)
            serie_match = re.search(r"S[ée]rie:?\s*(\d+)", text)
            if serie_match:
                serie = serie_match.group(1)
            em_match = re.search(r"Emiss[ãa]o[:\s]*(\d{2}/\d{2}/\d{4})", text)
            if em_match:
                emissao = em_match.group(1)

        return numero, serie, emissao

    @staticmethod
    def _extract_chave(soup) -> str | None:
        for selector in [".chave-acesso", ".chave", "#chave", "span.chave"]:
            el = soup.select_one(selector)
            if el:
                raw = el.get_text(strip=True)
                # Strip common label prefixes like "Chave de acesso:"
                raw = re.sub(r"^[^0-9]*", "", raw)
                cleaned = re.sub(r"\s+", "", raw)
                if cleaned:
                    return cleaned
        # Fallback: regex in page text
        text = soup.get_text()
        m = re.search(r"(\d{44})", text)
        if m:
            return m.group(1)
        return None

    @staticmethod
    def _extract_consumidor(soup) -> str | None:
        for selector in [".consumidor", "#consumidor", ".destinatario"]:
            el = soup.select_one(selector)
            if el:
                return el.get_text(strip=True)
        text = soup.get_text()
        m = re.search(r"Consumidor[:\s]*(.+?)(?:\n|$)", text)
        if m:
            return m.group(1).strip()
        return None

    @staticmethod
    def _extract_pagamento(soup) -> tuple:
        return [], None

    @staticmethod
    def _extract_ambiente(soup) -> str | None:
        text = soup.get_text()
        if "Homologação" in text or "homologacao" in text.lower():
            return "Homologação"
        if "Produção" in text or "producao" in text.lower():
            return "Produção"
        return None
