import dotenv from "dotenv"
import { resolve, dirname } from "path"
import { fileURLToPath } from "url"

const __dirname = dirname(fileURLToPath(import.meta.url))
dotenv.config({ path: resolve(__dirname, "../.env") })

const { app } = await import("./app")

const start = async () => {
  try {
    await app.listen({ port: 3333, host: "0.0.0.0" });
    console.log("Server running on http://localhost:3333");
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();
