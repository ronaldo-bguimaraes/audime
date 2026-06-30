# URL de Consulta NFC-e via QR Code

## Formato do Parâmetro `p`

A URL de consulta direta da NFC-e usa o parâmetro `p` com valores separados por pipe (`|`). Esse é o mesmo link embutido no QR Code impresso no DANFE.

### Versão 2.00 (leiaute atual)

```
https://<base_url>?p=<chave>|<versao>|<tpAmb>|<idCSC>|<hash>
```

| # | Parâmetro | Tam. | Descrição | Exemplo |
|---|---|---|---|---|
| 1 | `chave` | 44 | Chave de acesso da NFCe | `51260509477652008413651230002620731725445443` |
| 2 | `versao` | 1 | Versão do QR Code (`2`) | `2` |
| 3 | `tpAmb` | 1 | Ambiente: `1`=produção, `2`=homologação | `1` |
| 4 | `idCSC` | 1-6 | Identificador do CSC do contribuinte | `1` |
| 5 | `hash` | 40 | Código hash (SHA-1 hexadecimal) | `8D8C7A538544E4EF09D4749A4D5E4C70DA94863C` |

**Exemplo real (MT):**
```
http://www.sefaz.mt.gov.br/nfce/consultanfce?p=51260509477652008413651230002620731725445443|2|1|1|8D8C7A538544E4EF09D4749A4D5E4C70DA94863C
```

### Versão 3.00 (NT 2025.001 — futura)

Elimina o CSC. Para emissão normal (online):

```
https://<base_url>?p=<chave>|3|<tpAmb>
```

Para contingência (offline):

```
https://<base_url>?p=<chave>|3|<tpAmb>|<dhEmi>|<vNF>|<tpIdDest>|<idDest>|<assinatura>
```

**Nota:** MT ainda não migrou para v3. Verificar status no [Portal NFC-e ENCAT](http://nfce.encat.org).

## Base URLs por Estado

### Produção

| UF | Base URL |
|---|---|
| AC | `http://www.sefaznet.ac.gov.br/nfce/qrcode` |
| AL | `http://nfce.sefaz.al.gov.br/QRCode/consultarNFCe.jsp` |
| AM | `https://sistemas.sefaz.am.gov.br/nfceweb/consultarNFCe.jsp` |
| AP | `https://www.sefaz.ap.gov.br/nfce/nfcep.php` |
| BA | `http://nfe.sefaz.ba.gov.br/servicos/nfce/qrcode.aspx` |
| CE | `http://nfce.sefaz.ce.gov.br/pages/ShowNFCe.html` |
| DF | `http://www.fazenda.df.gov.br/nfce/qrcode` |
| ES | `http://app.sefaz.es.gov.br/ConsultaNFCe` |
| GO | `https://nfeweb.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe` |
| MA | `http://nfce.sefaz.ma.gov.br/portal/consultarNFCe.jsp` |
| **MT** | **`http://www.sefaz.mt.gov.br/nfce/consultanfce`** |
| MS | `http://www.dfe.ms.gov.br/nfce/qrcode` |
| MG | `https://portalsped.fazenda.mg.gov.br/portalnfce/sistema/qrcode.xhtml` |
| PA | `https://appnfc.sefa.pa.gov.br/portal/view/consultas/nfce/nfceForm.seam` |
| PB | `http://www.sefaz.pb.gov.br/nfce` |
| PR | `http://www.fazenda.pr.gov.br/nfce/qrcode` |
| PE | `http://nfce.sefaz.pe.gov.br/nfce/consulta` |
| PI | `http://www.sefaz.pi.gov.br/nfce/qrcode` |
| RJ | `https://consultadfe.fazenda.rj.gov.br/consultaNFCe/QRCode` |
| RN | `https://nfce.sefaz.rn.gov.br/consultarNFCe.aspx` |
| RS | `https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx` |
| RO | `http://www.nfce.sefin.ro.gov.br/consultanfce/consulta.jsp` |
| RR | `https://www.sefaz.rr.gov.br/nfce/servlet/qrcode` |
| SC | `https://sat.sef.sc.gov.br/nfce/consulta` |
| SP | `https://www.nfce.fazenda.sp.gov.br/qrcode` |
| SE | `http://www.nfce.se.gov.br/nfce/qrcode` |
| TO | `http://www.sefaz.to.gov.br/nfce/qrcode` |

### Homologação

| UF | Base URL |
|---|---|
| AC | `http://www.hml.sefaznet.ac.gov.br/nfce/qrcode` |
| AL | `http://nfce.sefaz.al.gov.br/QRCode/consultarNFCe.jsp` |
| AM | `https://homnfce.sefaz.am.gov.br/nfceweb/consultarNFCe.jsp` |
| AP | `https://www.sefaz.ap.gov.br/nfcehml/nfce.php` |
| BA | `http://hnfe.sefaz.ba.gov.br/servicos/nfce/qrcode.aspx` |
| CE | `http://nfceh.sefaz.ce.gov.br/pages/ShowNFCe.html` |
| DF | `http://www.fazenda.df.gov.br/nfce/qrcode` |
| ES | `http://homologacao.sefaz.es.gov.br/ConsultaNFCe` |
| GO | `https://nfewebhomolog.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe` |
| MA | `http://homologacao.sefaz.ma.gov.br/portal/consultarNFCe.jsp` |
| **MT** | **`http://homologacao.sefaz.mt.gov.br/nfce/consultanfce`** |
| MS | `http://www.dfe.ms.gov.br/nfce/qrcode` |
| MG | `https://portalsped.fazenda.mg.gov.br/portalnfce/sistema/qrcode.xhtml` |
| PA | `https://appnfc.sefa.pa.gov.br/portal-homologacao/view/consultas/nfce/nfceForm.seam` |
| PB | `http://www.sefaz.pb.gov.br/nfcehom` |
| PR | `http://www.fazenda.pr.gov.br/nfce/qrcode` |
| PE | `http://nfcehomolog.sefaz.pe.gov.br/nfce/consulta` |
| PI | `http://www.sefaz.pi.gov.br/nfce/qrcode` |
| RJ | `https://consultadfe.fazenda.rj.gov.br/consultaNFCe/QRCode` |
| RN | `https://hom.nfce.sefaz.rn.gov.br/consultarNFCe.aspx` |
| RS | `https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx` |
| RO | `http://www.nfce.sefin.ro.gov.br/consultanfce/consulta.jsp` |
| RR | `http://200.174.88.103:8080/nfce/servlet/qrcode` |
| SC | `https://hom.sat.sef.sc.gov.br/nfce/consulta` |
| SP | `https://www.homologacao.nfce.fazenda.sp.gov.br/qrcode` |
| SE | `http://www.hom.nfe.se.gov.br/nfce/qrcode` |
| TO | `http://homologacao.sefaz.to.gov.br/nfce/qrcode` |

**Fonte:** [ENCAT — URL por UF utilizada QR code](http://nfce.encat.org/desenvolvedor/qrcode/)

## Cálculo do Hash (CSC)

O código hash do parâmetro `p` (v2) é calculado com SHA-1:

```
dados = chave + versao + tpAmb + idCSC
hash = SHA1(dados + CSC)
```

Onde `CSC` é o Código de Segurança do Contribuinte, obtido junto à SEFAZ de cada estado.

**Exemplo (AM, homologação):**
- CSC fixo: `0123456789`
- idCSC: `000001`

## Por que essa URL funciona sem autenticação?

Diferente da consulta por chave de acesso (que exige captcha), a URL de QR Code já contém todos os dados de validação embutidos no hash. A SEFAZ apenas confere o hash com o CSC armazenado — se bater, exibe a nota. Isso é proposital: o QR Code foi desenhado para ser lido por qualquer aplicativo leitor, sem exigir login.

## Limitações

- A URL é **temporária** — se a NFC-e for cancelada, a consulta reflete o cancelamento
- Cada estado tem seu próprio **formato de HTML** — o parser precisa ser específico por UF
- O hash depende do **CSC do emitente** — sem ele não é possível gerar uma URL válida para uma nota nova
- Para consumo programático, algumas SEFAZs podem aplicar rate limiting por IP

## Diagrama

```
DANFE NFC-e
  ┌──────────┐
  │ QR Code  │ → https://...?p=44dig|2|1|1|hash
  └──────────┘
       │
       ▼
  GET /consultanfce?p=...
       │
       ▼
  SEFAZ valida hash (CSC)
       │
       ├── Hash OK  → retorna HTML da nota
       └── Hash NOK → retorna "Não encontrada"
```
