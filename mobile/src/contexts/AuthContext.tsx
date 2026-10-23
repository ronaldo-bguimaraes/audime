import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from "react"
import * as SecureStore from "expo-secure-store"
import { createApiClient, type ApiClient } from "shared"

const TOKEN_KEY = "audime_token"
const USER_ID_KEY = "audime_user_id"
const USER_NAME_KEY = "audime_user_name"
const USER_EMAIL_KEY = "audime_user_email"
const API_BASE = process.env.EXPO_PUBLIC_API_BASE_URL ?? ""

type AuthContextType = {
  token: string | null
  userId: string | null
  userName: string | null
  userEmail: string | null
  isLoading: boolean
  api: ApiClient
  signIn: (token: string, userId: string, name?: string, email?: string) => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [userId, setUserId] = useState<string | null>(null)
  const [userName, setUserName] = useState<string | null>(null)
  const [userEmail, setUserEmail] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const api = createApiClient(API_BASE, {
    getToken: () => token,
    onUnauthorized: () => {
      setToken(null)
      setUserId(null)
      setUserName(null)
      setUserEmail(null)
      SecureStore.deleteItemAsync(TOKEN_KEY)
      SecureStore.deleteItemAsync(USER_ID_KEY)
      SecureStore.deleteItemAsync(USER_NAME_KEY)
      SecureStore.deleteItemAsync(USER_EMAIL_KEY)
    },
  })

  useEffect(() => {
    (async () => {
      const storedToken = await SecureStore.getItemAsync(TOKEN_KEY)
      if (storedToken) {
        setToken(storedToken)
        const [storedUserId, storedName, storedEmail] = await Promise.all([
          SecureStore.getItemAsync(USER_ID_KEY),
          SecureStore.getItemAsync(USER_NAME_KEY),
          SecureStore.getItemAsync(USER_EMAIL_KEY),
        ])
        if (storedUserId) setUserId(storedUserId)
        if (storedName) setUserName(storedName)
        if (storedEmail) setUserEmail(storedEmail)

        try {
          const me = await api.get<{ id_usuario: number; nome: string; email: string }>("/v1/auth/me")
          setUserId(String(me.id_usuario))
          setUserName(me.nome)
          setUserEmail(me.email)
          await SecureStore.setItemAsync(USER_ID_KEY, String(me.id_usuario))
          await SecureStore.setItemAsync(USER_NAME_KEY, me.nome)
          await SecureStore.setItemAsync(USER_EMAIL_KEY, me.email)
        } catch {
          // token expired or network error — keep cached values
        }
      }
      setIsLoading(false)
    })()
  }, [])

  const signIn = useCallback(async (newToken: string, newUserId: string, name?: string, email?: string) => {
    await SecureStore.setItemAsync(TOKEN_KEY, newToken)
    await SecureStore.setItemAsync(USER_ID_KEY, newUserId)
    if (name) await SecureStore.setItemAsync(USER_NAME_KEY, name)
    if (email) await SecureStore.setItemAsync(USER_EMAIL_KEY, email)
    setToken(newToken)
    setUserId(newUserId)
    if (name) setUserName(name)
    if (email) setUserEmail(email)
  }, [])

  const signOut = useCallback(async () => {
    await Promise.all([
      SecureStore.deleteItemAsync(TOKEN_KEY),
      SecureStore.deleteItemAsync(USER_ID_KEY),
      SecureStore.deleteItemAsync(USER_NAME_KEY),
      SecureStore.deleteItemAsync(USER_EMAIL_KEY),
    ])
    setToken(null)
    setUserId(null)
    setUserName(null)
    setUserEmail(null)
  }, [])

  return (
    <AuthContext.Provider value={{ token, userId, userName, userEmail, isLoading, api, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
