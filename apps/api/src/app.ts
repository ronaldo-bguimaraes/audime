import Fastify from "fastify";
import cors from "@fastify/cors";

import authPlugin from "./modules/auth";

export const app = Fastify({
  logger: true,
});

await app.register(cors, { origin: true });

app.register(authPlugin);

app.get("/health", async () => {
  return { ok: true };
});

app.get("/envs", async () => {
  return { loadEnv: process.env.LOAD_ENV ?? "not set" };
});
