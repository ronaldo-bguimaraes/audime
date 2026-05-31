const envs = [
  "API_URL",
  "DATABASE_URL",
  "FRONTEND_URL",
  "GOOGLE_CLIENT_ID",
  "GOOGLE_CLIENT_SECRET",
  "JWT_SECRET",
  "PORT",
];

export function getEnvsStatus() {
  const result: Record<string, string> = {};

  for (const env of envs) {
    const val = process.env[env];
    if (val == undefined || val == null) {
      result[env] = "NOT SET";
      continue;
    }
    if (val.trim() == "") {
      result[env] = "EMPTY";
      continue;
    }
    result[env] = "CONFIGURED";
  }

  return result;
}
