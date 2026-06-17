import re

from bs4 import BeautifulSoup


class NotaExtraida:
    def __init__(self, empresa: str, chave: str, numero: str, serie: str, emissao: str, items: list):
        self.empresa = empresa
        self.chave = chave
        self.numero = numero
        self.serie = serie
        self.emissao = emissao
        self.items = items

    @property
    def valor_total(self) -> float:
        return sum(i["item_valor_total"] for i in self.items)


def extract_value(data: str) -> str:
    return re.search(r"(\d+(?:\.\d{3})*,\d{1,2})", data).group(1)


def parse_nfce(html_bytes: bytes) -> NotaExtraida:
    soup = BeautifulSoup(html_bytes, "html.parser")

    infos = soup.select_one("#infos").text

    items = []
    for row in soup.select("#tabResult tr"):
        codigo = re.search(r"\s+(\d+)\s", row.select_one(".RCod").text).group(1)
        descricao = row.select_one(".txtTit").text
        quantidade = row.select_one(".Rqtd").contents[1]
        unidade = row.select_one(".RUN").contents[1]
        valor_unidade = extract_value(row.select_one(".RvlUnit").contents[1])
        valor_total = extract_value(row.select_one(".valor").text)

        items.append({
            "item_codigo": codigo,
            "item_descricao": descricao,
            "item_quantidade": float(quantidade.replace(",", ".")),
            "item_tipo_unidade": unidade,
            "item_valor_unidade": float(valor_unidade.replace(".", "").replace(",", ".")),
            "item_valor_total": float(valor_total.replace(".", "").replace(",", ".")),
        })

    nota = NotaExtraida(
        empresa=soup.select_one("#conteudo .txtCenter .txtTopo").text,
        chave=soup.select_one("span.chave").text,
        numero=re.search(r"N.mero\D+(\d+)", infos).group(1),
        serie=re.search(r"S.rie\D+(\d+)", infos).group(1),
        emissao=re.search(r"Emiss.o\D+(.+)", infos).group(1),
        items=items,
    )

    return nota
