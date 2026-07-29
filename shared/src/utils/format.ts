const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

export function formatBRL(value: number): string {
  return currencyFormatter.format(value);
}

export function maskChave(chave: string): string {
  if (chave.length <= 8) return chave;
  return `${chave.slice(0, 4)}...${chave.slice(-4)}`;
}

export function formatDate(dateStr: string): string {
  const [year, month, day] = dateStr.split("-");
  return `${day}/${month}/${year}`;
}
