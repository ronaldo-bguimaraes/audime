const envs = ["DATABASE_URL", "NODE_ENV", "PORT"];

const result: Record<string, string> = {};

for (const env of envs) {
  result[env] = process.env[env] ?? "";
}

console.log(JSON.stringify(result, null, 2));
