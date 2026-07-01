import re

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
      - "269,00" -> 269.0
      - "NaN", "", None -> None
    """
    if text is None:
        return None
    text = text.strip()
    if not text or text.upper() in ("NAN", "NA", ""):
        return None
    # Remove 'R$', espaços, e caracteres não numéricos exceto , e .
    text = re.sub(r"[^\d,.-]", "", text)
    if not text:
        return None
    # Trata separador de milhar (.) e decimal (,)
    # Se tiver vírgula, então o último ponto antes da vírgula é separador de milhar
    # Ex: "1.234,56" -> replace('.','') fica "1234,56" -> replace(',','.') fica "1234.56"
    # Ex: "17,9" -> replace('.','') nop -> replace(',','.') fica "17.9"
    # Ex: "269,00" -> mesma lógica
    cleaned = text.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
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
    addr = {
        "logradouro": parts[0] if len(parts) > 0 else "",
        "numero": parts[1] if len(parts) > 1 else "",
        "complemento": parts[2] if len(parts) > 2 else "",
        "bairro": parts[3] if len(parts) > 3 else "",
        "cidade": parts[4] if len(parts) > 4 else "",
        "uf": parts[5] if len(parts) > 5 else "",
    }
    return addr


def extract_text_by_label(infos_text: str, label: str) -> str:
    """Extract text after a label in the infos text block."""
    # Handle "Consumidor:\n  texto" and "Consumidor texto"
    pattern = re.compile(
        re.escape(label) + r"\s*[:]\s*(.+?)(?:\n|$)", re.DOTALL
    )
    match = pattern.search(infos_text)
    if match:
        return match.group(1).strip()
    # Alternative: label without colon
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


def parse_nfce(html_bytes: bytes) -> NotaExtraida:
    soup = BeautifulSoup(html_bytes, "html.parser")

    # ── Dados do emitente ───────────────────────────────────────────────
    empresa = safe_text(soup, "#conteudo .txtCenter .txtTopo") or safe_text(
        soup, ".txtTopo"
    )

    # CNPJ
    cnpj = None
    cnpj_elem = soup.select_one(".txtCenter .text")
    if cnpj_elem:
        cnpj_text = cnpj_elem.get_text(strip=True)
        cnpj_match = re.search(r"CNPJ:\s*([\d./-]+)", cnpj_text)
        if cnpj_match:
            cnpj = cnpj_match.group(1)

    # Endereço (segundo .txtCenter .text)
    endereco_text = None
    addr_elems = soup.select(".txtCenter .text")
    if len(addr_elems) >= 2:
        endereco_text = addr_elems[1].get_text(strip=True)
    elif addr_elems:
        # Pode estar no mesmo elemento do CNPJ, após "CNPJ: ..."
        full_text = addr_elems[0].get_text(strip=True)
        # Remove CNPJ part, keep the rest as address
        endereco_text = re.sub(r"CNPJ:\s*[\d./-]+", "", full_text).strip()

    endereco = parse_address(endereco_text) if endereco_text else {}

    # ── Items ───────────────────────────────────────────────────────────
    items = []
    for row in soup.select("#tabResult tr"):
        txt_tit = row.select_one(".txtTit")
        if not txt_tit:
            continue

        descricao = txt_tit.get_text(strip=True)

        # Código
        codigo = None
        cod_elem = row.select_one(".RCod")
        if cod_elem:
            cod_match = re.search(r"(\d+)", cod_elem.get_text(strip=True))
            if cod_match:
                codigo = cod_match.group(1)

        # Quantidade
        quantidade = 1.0
        qtd_elem = row.select_one(".Rqtd")
        if qtd_elem:
            qtd_text = qtd_elem.get_text(strip=True)  # "Qtde.:1" ou "Qtde.:0,304"
            qtd_match = re.search(r"Qtde\.?:?\s*([\d,]+)", qtd_text)
            if qtd_match:
                qtd_val = br_to_float(qtd_match.group(1))
                if qtd_val is not None:
                    quantidade = qtd_val

        # Unidade
        unidade = "UN"
        un_elem = row.select_one(".RUN")
        if un_elem:
            un_text = un_elem.get_text(strip=True)  # "UN: UN" ou "UN: KG"
            un_match = re.search(r"UN:\s*(\S+)", un_text)
            if un_match:
                unidade = un_match.group(1)

        # Valor unitário
        valor_unidade = 0.0
        vl_un_elem = row.select_one(".RvlUnit")
        if vl_un_elem:
            vl_un_text = vl_un_elem.get_text(strip=True)
            vl_un_match = re.search(r"Vl\.\s*Unit\.?:?\s*([\d.,]+)", vl_un_text)
            if vl_un_match:
                vl_val = br_to_float(vl_un_match.group(1))
                if vl_val is not None:
                    valor_unidade = vl_val

        # Valor total do item
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

    # ── Totais (#totalNota) ──────────────────────────────────────────────
    qtd_total_itens = None
    valor_total = None

    total_div = soup.select_one("#totalNota")
    if total_div:
        # Qtd. total de itens (primeiro #linhaTotal)
        qtd_el = total_div.select_one("#linhaTotal .totalNumb")
        if qtd_el:
            qtd_val = br_to_float(qtd_el.get_text(strip=True))
            if qtd_val is not None:
                qtd_total_itens = int(qtd_val)

        # Valor a pagar R$ (linha com .txtMax)
        valor_el = total_div.select_one(".txtMax")
        if valor_el:
            valor_total = br_to_float(valor_el.get_text(strip=True))

    # Fallback: se não conseguiu extrair valor_total do HTML, calcular por soma
    if valor_total is None:
        valor_total = round(sum(i["item_valor_total"] for i in items), 2)

    # ── Formas de pagamento ─────────────────────────────────────────────
    formas_pagamento = []
    if total_div:
        linha_forma_div = total_div.select_one("#linhaForma")
        if linha_forma_div:
            # Pegar todos #linhaTotal após #linhaForma
            all_linha_total = total_div.select("#linhaTotal")
            started = False
            for lt in all_linha_total:
                label_el = lt.select_one("label.tx")
                if not label_el:
                    continue
                label_text = label_el.get_text(strip=True)
                # Ignorar "Troco"
                if "troco" in label_text.lower():
                    continue
                value_el = lt.select_one(".totalNumb")
                valor = br_to_float(value_el.get_text(strip=True)) if value_el else None
                formas_pagamento.append(
                    {"tipo": label_text, "valor": valor}
                )

    # Troco (último #linhaTotal com label "Troco")
    troco = None
    if total_div:
        all_linha_total = total_div.select("#linhaTotal")
        for lt in all_linha_total:
            label_el = lt.select_one("label.tx")
            if label_el and "troco" in label_el.get_text(strip=True).lower():
                value_el = lt.select_one(".totalNumb")
                if value_el:
                    troco_val = br_to_float(value_el.get_text(strip=True))
                    troco = troco_val  # None se NaN

    # ── Infos gerais (#infos) ───────────────────────────────────────────
    infos_div = soup.select_one("#infos")
    infos_text = infos_div.get_text("\n", strip=True) if infos_div else ""

    # Número, Série, Emissão
    numero = re.search(r"N.mero\D+(\d+)", infos_text)
    numero = numero.group(1) if numero else None

    serie = re.search(r"S.rie\D+(\d+)", infos_text)
    serie = serie.group(1) if serie else None

    emissao = re.search(r"Emiss.o\D+(.+)", infos_text)
    emissao = emissao.group(1) if emissao else None

    # Protocolo de Autorização
    protocolo = None
    protocolo_data = None
    prot_match = re.search(
        r"Protocolo de Autoriza..o:\s*(\d+)\s+(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})",
        infos_text,
    )
    if prot_match:
        protocolo = {"numero": prot_match.group(1), "data_hora": prot_match.group(2)}

    # Ambiente
    ambiente = None
    amb_match = re.search(
        r"Ambiente de (Produ..o|Homologa..o)", infos_text
    )
    if amb_match:
        raw = amb_match.group(1)
        ambiente = "Produção" if "Produ" in raw else "Homologação"

    # Consumidor
    consumidor = None
    # Procura na seção de Consumidor do collapsible
    consumidor_section = infos_div.find("h4", string=re.compile(r"Consumidor")) if infos_div else None
    if consumidor_section:
        parent_li = consumidor_section.find_next("li")
        if parent_li:
            consumidor = parent_li.get_text(strip=True)
    if not consumidor:
        # Fallback: regex no texto geral
        cons_match = re.search(
            r"Consumidor\s*\n*\s*[\:]*\s*(.+?)(?:\n|$)", infos_text
        )
        if cons_match:
            consumidor = cons_match.group(1).strip()

    # Informações de interesse do contribuinte
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
        # Fallback: regex
        int_match = re.search(
            r"Informa..es de interesse do contribuinte.+?(?:\[##(.+?)\]|$)",
            infos_text,
            re.DOTALL,
        )
        if int_match:
            interesse_text = int_match.group(1)

    if interesse_text:
        # Tributos
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

        # COO e PDV
        coo_match = re.search(r"COO:\s*(\d+)", interesse_text)
        pdv_match = re.search(r"PDV:\s*(\d+)", interesse_text)
        informacoes_interesse["coo"] = int(coo_match.group(1)) if coo_match else None
        informacoes_interesse["pdv"] = int(pdv_match.group(1)) if pdv_match else None

    # ── Chave (remover espaços) ─────────────────────────────────────────
    chave_raw = safe_text(soup, "span.chave")
    chave = re.sub(r"\s+", "", chave_raw) if chave_raw else None

    # ── Montar extra JSON ───────────────────────────────────────────────
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

    # ── NotaExtraida ─────────────────────────────────────────────────────
    nota = NotaExtraida(
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

    return nota
