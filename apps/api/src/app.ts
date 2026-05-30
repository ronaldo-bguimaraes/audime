import Fastify from "fastify";
import cors from "@fastify/cors";
import { InvoiceItemSchema } from "@audime/schemas"
import authPlugin from "./modules/auth"

export const app = Fastify({
  logger: true,
});

await app.register(cors, { origin: true });
app.register(authPlugin);

app.get("/health", async () => {
  const data = JSON.stringify(InvoiceItemSchema);
  return { ok: true, data };
});
