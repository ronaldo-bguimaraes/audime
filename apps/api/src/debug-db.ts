import "dotenv/config"

console.log("DATABASE_URL:", process.env.DATABASE_URL ?? "NOT SET")
console.log("NODE_ENV:", process.env.NODE_ENV ?? "not set")
