import Fastify from "fastify";
import { InvoiceItemSchema } from "@audime/schemas"

export const app = Fastify({
  logger: true,
});

app.get("/health", async () => {
  const data = JSON.stringify(InvoiceItemSchema);
  return { ok: true, data };
});
