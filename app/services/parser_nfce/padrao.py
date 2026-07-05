import re

from bs4 import BeautifulSoup

from app.services.parser_nfce.base import (
    BaseParser,
    NotaExtraida,
    br_to_float,
    extract_text_by_label,
    parse_address,
    safe_text,
)


class PadraoParser(BaseParser):
    """Parser for the standard MT-style NFC-e layout (jQuery Mobile).

    Used by Mato Grosso and other states that follow the same template.
    """

    def parse_nfce(self, html_bytes: bytes) -> NotaExtraida:
        soup = BeautifulSoup(html_bytes, "html.parser")

        # ── Dados do emitente ───────────────────────────────────────────
        empresa = safe_text(soup, "#conteudo .txtCenter .txtTopo") or safe_text(
            soup, ".txtTopo"
        )

        cnpj = None
        cnpj_elem = soup.select_one(".txtCenter .text")
        if cnpj_elem:
            cnpj_text = cnpj_elem.get_text(strip=True)
            cnpj_match = re.search(r"CNPJ:\s*([\d./-]+)", cnpj_text)
            if cnpj_match:
                cnpj = cnpj_match.group(1)

        endereco_text = None
        addr_elems = soup.select(".txtCenter .text")
        if len(addr_elems) >= 2:
            endereco_text = addr_elems[1].get_text(strip=True)
        elif addr_elems:
            full_text = addr_elems[0].get_text(strip=True)
            endereco_text = re.sub(r"CNPJ:\s*[\d./-]+", "", full_text).strip()

        endereco = parse_address(endereco_text) if endereco_text else {}

        # ── Items ───────────────────────────────────────────────────────
        items = []
        for row in soup.select("#tabResult tr"):
            txt_tit = row.select_one(".txtTit")
            if not txt_tit:
                continue

            descricao = txt_tit.get_text(strip=True)

            codigo = None
            cod_elem = row.select_one(".RCod")
            if cod_elem:
                cod_match = re.search(r"(\d+)", cod_elem.get_text(strip=True))
                if cod_match:
                    codigo = cod_match.group(1)

            quantidade = 1.0
            qtd_elem = row.select_one(".Rqtd")
            if qtd_elem:
                qtd_text = qtd_elem.get_text(strip=True)
                qtd_match = re.search(r"Qtde\.?:?\s*([\d,]+)", qtd_text)
                if qtd_match:
                    qtd_val = br_to_float(qtd_match.group(1))
                    if qtd_val is not None:
                        quantidade = qtd_val

            unidade = "UN"
            un_elem = row.select_one(".RUN")
            if un_elem:
                un_text = un_elem.get_text(strip=True)
                un_match = re.search(r"UN:\s*(\S+)", un_text)
                if un_match:
                    unidade = un_match.group(1)

            valor_unidade = 0.0
            vl_un_elem = row.select_one(".RvlUnit")
            if vl_un_elem:
                vl_un_text = vl_un_elem.get_text(strip=True)
                vl_un_match = re.search(r"Vl\.\s*Unit\.?:?\s*([\d.,]+)", vl_un_text)
                if vl_un_match:
                    vl_val = br_to_float(vl_un_match.group(1))
                    if vl_val is not None:
                        valor_unidade = vl_val

            valor_total_item = 0.0
            vl_total_elem = row.select_one(".valor")
            if vl_total_elem:
                vl_total_text = vl_total_elem.get_text(strip=True)
                vl_val = br_to_float(vl_total_text)
                if vl_val is not None:
                    valor_total_item = vl_val

            items.append(
                {
                    "item_codigo": codigo,
                    "item_descricao": descricao,
                    "item_quantidade": quantidade,
                    "item_tipo_unidade": unidade,
                    "item_valor_unidade": round(valor_unidade, 2),
                    "item_valor_total": round(valor_total_item, 2),
                }
            )

        # ── Totais ──────────────────────────────────────────────────────
        qtd_total_itens = None
        valor_total = None

        total_div = soup.select_one("#totalNota")
        if total_div:
            qtd_el = total_div.select_one("#linhaTotal .totalNumb")
            if qtd_el:
                qtd_val = br_to_float(qtd_el.get_text(strip=True))
                if qtd_val is not None:
                    qtd_total_itens = int(qtd_val)

            valor_el = total_div.select_one(".txtMax")
            if valor_el:
                valor_total = br_to_float(valor_el.get_text(strip=True))

        if valor_total is None:
            valor_total = round(sum(i["item_valor_total"] for i in items), 2)

        # ── Formas de pagamento ─────────────────────────────────────────
        formas_pagamento = []
        if total_div:
            linha_forma_div = total_div.select_one("#linhaForma")
            if linha_forma_div:
                for lt in linha_forma_div.find_next_siblings("div", id="linhaTotal"):
                    label_el = lt.select_one("label.tx")
                    if not label_el:
                        continue
                    label_text = label_el.get_text(strip=True)
                    if "troco" in label_text.lower():
                        continue
                    value_el = lt.select_one(".totalNumb")
                    valor = br_to_float(value_el.get_text(strip=True)) if value_el else None
                    formas_pagamento.append(
                        {"tipo": label_text, "valor": valor}
                    )

        troco = None
        if total_div:
            all_linha_total = total_div.select("#linhaTotal")
            for lt in all_linha_total:
                label_el = lt.select_one("label.tx")
                if label_el and "troco" in label_el.get_text(strip=True).lower():
                    value_el = lt.select_one(".totalNumb")
                    if value_el:
                        troco_val = br_to_float(value_el.get_text(strip=True))
                        troco = troco_val

        # ── Infos gerais ────────────────────────────────────────────────
        infos_div = soup.select_one("#infos")
        infos_text = infos_div.get_text("\n", strip=True) if infos_div else ""

        numero = re.search(r"N.mero\D+(\d+)", infos_text)
        numero = numero.group(1) if numero else None

        serie = re.search(r"S.rie\D+(\d+)", infos_text)
        serie = serie.group(1) if serie else None

        emissao = re.search(r"Emiss.o\D+(.+)", infos_text)
        emissao = emissao.group(1) if emissao else None

        protocolo = None
        protocolo_data = None
        prot_match = re.search(
            r"Protocolo de Autoriza..o:\s*(\d+)\s+(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})",
            infos_text,
        )
        if prot_match:
            protocolo = {"numero": prot_match.group(1), "data_hora": prot_match.group(2)}

        ambiente = None
        amb_match = re.search(r"Ambiente de (Produ..o|Homologa..o)", infos_text)
        if amb_match:
            raw = amb_match.group(1)
            ambiente = "Produção" if "Produ" in raw else "Homologação"

        consumidor = None
        consumidor_section = infos_div.find("h4", string=re.compile(r"Consumidor")) if infos_div else None
        if consumidor_section:
            parent_li = consumidor_section.find_next("li")
            if parent_li:
                consumidor = parent_li.get_text(strip=True)
        if not consumidor:
            cons_match = re.search(
                r"Consumidor\s*\n*\s*[\:]*\s*(.+?)(?:\n|$)", infos_text
            )
            if cons_match:
                consumidor = cons_match.group(1).strip()

        informacoes_interesse = {}
        interesse_section = (
            infos_div.find("h4", string=re.compile(r"Informa..es de interesse"))
            if infos_div
            else None
        )
        interesse_text = None
        if interesse_section:
            parent_li = interesse_section.find_next("li")
            if parent_li:
                interesse_text = parent_li.get_text(strip=True)
        if not interesse_text:
            int_match = re.search(
                r"Informa..es de interesse do contribuinte.+?(?:\[##(.+?)\]|$)",
                infos_text,
                re.DOTALL,
            )
            if int_match:
                interesse_text = int_match.group(1)

        if interesse_text:
            trib_fed = re.search(r"FEDERAL\s*R\$\s*([\d.,]+)", interesse_text, re.IGNORECASE)
            trib_est = re.search(r"ESTADUAL\s*R\$\s*([\d.,]+)", interesse_text, re.IGNORECASE)
            trib_mun = re.search(r"MUNICIPAL\s*R\$\s*([\d.,]+)", interesse_text, re.IGNORECASE)
            informacoes_interesse["tributos_federal"] = (
                br_to_float(trib_fed.group(1)) if trib_fed else None
            )
            informacoes_interesse["tributos_estadual"] = (
                br_to_float(trib_est.group(1)) if trib_est else None
            )
            informacoes_interesse["tributos_municipal"] = (
                br_to_float(trib_mun.group(1)) if trib_mun else None
            )

            coo_match = re.search(r"COO:\s*(\d+)", interesse_text)
            pdv_match = re.search(r"PDV:\s*(\d+)", interesse_text)
            informacoes_interesse["coo"] = int(coo_match.group(1)) if coo_match else None
            informacoes_interesse["pdv"] = int(pdv_match.group(1)) if pdv_match else None

        # ── Chave ───────────────────────────────────────────────────────
        chave_raw = safe_text(soup, "span.chave")
        chave = re.sub(r"\s+", "", chave_raw) if chave_raw else None

        # ── Montar extra ────────────────────────────────────────────────
        extra = {
            "emitente": {
                "cnpj": cnpj,
                **endereco,
            },
            "protocolo_autorizacao": protocolo,
            "formas_pagamento": formas_pagamento,
            "consumidor": consumidor,
            "ambiente": ambiente,
            "informacoes_interesse": informacoes_interesse,
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
