import Fastify from "fastify";
import cors from "@fastify/cors";

import authPlugin from "./modules/auth";

import { getEnvsStatus } from "./debug-db";

export const app = Fastify({
  logger: true,
});

await app.register(cors, { origin: true });

app.register(authPlugin);

app.get("/health", async () => {
  return { ok: true };
});

app.get("/", async () => {
  return { online: true };
});

app.get("/envs", async () => {
  return getEnvsStatus();
});
