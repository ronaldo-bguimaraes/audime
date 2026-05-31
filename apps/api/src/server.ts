import "dotenv/config";

import { app } from "./app";

export const API_PORT = Number.parseInt(process.env.PORT ?? "3333");

const start = async () => {
  try {
    await app.listen({ port: API_PORT });
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();
