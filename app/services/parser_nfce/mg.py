"""Minas Gerais NFC-e parser.

MG uses a JSF + PrimeFaces + Bootstrap layout with plain
Bootstrap tables (no PrimeFaces data-table widgets).

Key characteristics:
  - Company name in the header table (``.text-center``, row 1)
  - Items in ``table.table-striped`` (4 cols, NO header row)
  - Chave in first 1-row ``.table-hover``
  - Nota info in ``.table-hover`` containing "Modelo"
"""

import re

from bs4 import BeautifulSoup

from app.services.parser_nfce.base import (
    BaseParser,
    NotaExtraida,
    br_to_float,
)


class MgParser(BaseParser):
    """Parser for Minas Gerais NFC-e layout (JSF + PrimeFaces + Bootstrap)."""

    def parse_nfce(self, html_bytes: bytes) -> NotaExtraida:
        soup = BeautifulSoup(html_bytes, "html.parser")

        items = self._extract_items(soup)
        empresa = self._extract_empresa(soup)
        cnpj = self._extract_cnpj(soup)
        endereco = self._extract_endereco(soup)
        chave = self._extract_chave(soup)
        numero, serie, emissao = self._extract_nota_info(soup)
        valor_total, qtd_total_itens = self._extract_totals(soup, items)
        formas_pagamento = self._extract_pagamento(soup)
        consumidor = self._extract_consumidor(soup)

        return NotaExtraida(
            empresa=empresa or "",
            chave=chave,
            numero=numero or "0",
            serie=serie or "0",
            emissao=emissao,
            items=items,
            valor_total=valor_total or 0,
            qtd_total_itens=qtd_total_itens,
            extra={
                "emitente": {"cnpj": cnpj, **endereco},
                "protocolo_autorizacao": None,
                "formas_pagamento": [{"tipo": formas_pagamento, "valor": None}] if formas_pagamento else [],
                "consumidor": consumidor,
                "ambiente": self._extract_ambiente(soup),
                "informacoes_interesse": {},
                "troco": None,
            },
        )

    # ── Extraction methods ──────────────────────────────────────────

    @staticmethod
    def _extract_empresa(soup) -> str:
        header = soup.select_one(".text-center")
        if not header:
            return ""
        rows = header.find_all("tr")
        if len(rows) >= 2:
            return rows[1].get_text(strip=True)
        return ""

    @staticmethod
    def _extract_cnpj(soup) -> str | None:
        m = re.search(r"CNPJ:\s*([\d./-]+)", soup.get_text())
        return m.group(1) if m else None

    @staticmethod
    def _extract_endereco(soup) -> dict:
        header = soup.select_one(".text-center")
        if header:
            rows = header.find_all("tr")
            if len(rows) >= 4:
                addr_raw = rows[3].get_text(strip=True)
                from app.services.parser_nfce.base import parse_address
                return parse_address(addr_raw)
        return {"logradouro": "", "numero": "", "complemento": "", "bairro": "", "cidade": "", "uf": ""}

    @staticmethod
    def _extract_items(soup) -> list:
        items = []
        table = soup.select_one(".table-striped")
        if not table:
            return items
        for row in table.find_all("tr"):
            tds = row.find_all("td")
            if len(tds) < 4:
                continue
            desc = re.sub(r"\s*\(Código:\s*\d+\)", "", tds[0].get_text(strip=True)).strip()
            if not desc:
                continue
            qtd = br_to_float(re.search(r"[\d.,]+", tds[1].get_text()).group(0)) if re.search(r"[\d.,]+", tds[1].get_text()) else 1.0
            un = re.search(r"UN:\s*(\S+)", tds[2].get_text())
            vl = br_to_float(re.sub(r"[^\d,.]", "", tds[3].get_text())) or 0.0
            items.append({
                "item_codigo": None,
                "item_descricao": desc,
                "item_quantidade": qtd,
                "item_tipo_unidade": un.group(1) if un else "UN",
                "item_valor_unidade": None,
                "item_valor_total": round(vl, 2),
            })
        return items

    @staticmethod
    def _extract_totals(soup, items) -> tuple:
        text = soup.get_text()
        m = re.search(r"Valor total do servic[oç].*?R\$\s*([\d.,]+)", text, re.DOTALL)
        if not m:
            m = re.search(r"Valor total R\$\s*R?\$?\s*([\d.,]+)", text)
        valor = br_to_float(m.group(1)) if m else None
        return valor or round(sum(i["item_valor_total"] for i in items), 2), len(items) or None

    @staticmethod
    def _extract_nota_info(soup) -> tuple:
        for table in soup.select(".table-hover"):
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue
            labels = [td.get_text(strip=True) for td in rows[0].find_all(["td", "th"])]
            values = [td.get_text(strip=True) for td in rows[1].find_all("td")]
            if "Número" in " ".join(labels) or "Numero" in " ".join(labels):
                numero = serie = emissao = None
                for i, label in enumerate(labels):
                    if i < len(values):
                        if "Número" in label or "Numero" in label:
                            numero = values[i]
                        elif "Série" in label or "Serie" in label:
                            serie = values[i]
                        elif "Emissão" in label or "Emissao" in label or "Data Emissão" in label:
                            emissao = values[i]
                return numero, serie, emissao
        return None, None, None

    @staticmethod
    def _extract_chave(soup) -> str | None:
        for table in soup.select(".table-hover"):
            clean = re.sub(r"[^\d]", "", table.get_text())
            if len(clean) >= 44:
                m = re.search(r"(\d{44})", clean)
                if m:
                    return m.group(1)
        clean = re.sub(r"[^\d]", "", soup.get_text())
        m = re.search(r"(\d{44})", clean)
        return m.group(1) if m else None

    @staticmethod
    def _extract_pagamento(soup) -> str | None:
        m = re.search(r"Forma de Pagamento\s*\n+\s*(.+?)(?:\n|$)", soup.get_text())
        return m.group(1).strip() if m else None

    @staticmethod
    def _extract_consumidor(soup) -> str | None:
        for table in soup.select(".table-hover"):
            rows = table.find_all("tr")
            for row in rows:
                tds = row.find_all("td")
                if len(tds) >= 2 and "Nome" in tds[0].get_text():
                    return tds[1].get_text(strip=True)
        return None

    @staticmethod
    def _extract_ambiente(soup) -> str | None:
        text = soup.get_text()
        if "Homologação" in text or "homologacao" in text.lower():
            return "Homologação"
        if "Produção" in text or "producao" in text.lower():
            return "Produção"
        return None
