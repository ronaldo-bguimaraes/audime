const TOKEN_KEY = "audime_token"

export const API = import.meta.env.VITE_API_URL ?? "http://localhost:3333"

export interface AuthUser {
  user: {
    id: string
    name: string | null
    email: string
    avatar: string | null
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export async function fetchUser(): Promise<AuthUser> {
  const token = getToken()
  if (!token) throw new Error("No token")
  const res = await fetch(`${API}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) {
    clearToken()
    throw new Error("Unauthorized")
  }
  return res.json()
}
