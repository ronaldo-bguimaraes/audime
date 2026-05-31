import "dotenv/config";

import { app } from "./app";

export const SERVER_PORT = Number.parseInt(process.env.PORT ?? "3333");

const start = async () => {
  try {
    await app.listen({ host: "0.0.0.0", port: SERVER_PORT });
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();
