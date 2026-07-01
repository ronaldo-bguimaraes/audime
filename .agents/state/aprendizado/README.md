# Aprendizado

Este diretório armazena registros de aprendizado produzidos pelo agente **aprendiz**.

## Propósito

Diferente de `lessons.md` (que acumula lições transversais entre ciclos) e `memoria/` (que arquiva resumos de ciclos completos), este diretório contém **conhecimento temático e autônomo**: pesquisas sobre tecnologias, padrões, ferramentas, e conceitos relevantes para o projeto Audime.

Cada arquivo é um registro independente sobre um tópico específico, criado quando o agente `aprendiz` é invocado para aprender algo.

## Formato

Cada arquivo segue o formato:

```markdown
---
date: YYYY-MM-DD
topic: <tópico>
tags: [tag1, tag2]
sources:
  - title: <título da fonte>
    url: <url>
---

# <Tópico> — <data>

## O que é
...

## Para que usaríamos no Audime
...

## Por que não usar
...

## Alternativas
...

## Prós e contras
| Prós | Contras |
|------|---------|
| ...  | ...     |

## Conclusão
...
```

### Campos do frontmatter

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| `date` | Sim | Data do aprendizado no formato YYYY-MM-DD |
| `topic` | Sim | Nome do tópico (ex.: "Docker", "Pydantic", "WebSockets") |
| `tags` | Sim | Lista de tags para busca e correlação |
| `sources` | Sim | Lista de fontes consultadas com título e URL |

### Nomenclatura

Arquivos devem ser nomeados como `<topico>.md`, onde `<topico>` é uma versão simplificada do nome do tópico:
- Apenas letras minúsculas, números e hífens
- Sem espaços ou caracteres especiais
- Exemplos: `docker.md`, `pydantic-v2.md`, `python-asyncio.md`

## Uso

Para invocar o aprendiz e registrar aprendizado sobre um tópico:

```
@aprendiz aprenda docker
```

O aprendiz vai:
1. Pesquisar sobre Docker na internet
2. Questionar como aplicar no Audime
3. Explicar de forma estruturada
4. Explorar o codebase para contextualizar
5. Registrar em `<topico>.md`

## Diferenças de outros artefatos

| Artefato | Quem escreve | O que contém |
|----------|-------------|--------------|
| `lessons.md` | Loopback / todos | Lições transversais entre ciclos (falhas, decisões, aprendizados gerais) |
| `memoria/` | Especulador | Resumo de ciclos completos (o que foi feito, status dos critérios) |
| `aprendizado/` | **Aprendiz** | Conhecimento novo pesquisado (tópicos, tecnologias, padrões) |
