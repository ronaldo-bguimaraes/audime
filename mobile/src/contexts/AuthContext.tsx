import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from "react"
import * as SecureStore from "expo-secure-store"
import { createApiClient, FetchError, type ApiClient } from "shared"

const TOKEN_KEY = "audime_token"
const USER_ID_KEY = "audime_user_id"
const API_BASE = process.env.EXPO_PUBLIC_API_BASE_URL ?? ""

type AuthContextType = {
  token: string | null
  userId: string | null
  isLoading: boolean
  api: ApiClient
  signIn: (token: string, userId: string) => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [userId, setUserId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const api = createApiClient(API_BASE, {
    getToken: () => token,
    onUnauthorized: () => {
      setToken(null)
      setUserId(null)
      SecureStore.deleteItemAsync(TOKEN_KEY)
      SecureStore.deleteItemAsync(USER_ID_KEY)
    },
  })

  useEffect(() => {
    SecureStore.getItemAsync(TOKEN_KEY).then((storedToken) => {
      if (storedToken) {
        setToken(storedToken)
        SecureStore.getItemAsync(USER_ID_KEY).then((storedUserId) => {
          if (storedUserId) setUserId(storedUserId)
          setIsLoading(false)
        })
      } else {
        setIsLoading(false)
      }
    })
  }, [])

  const signIn = useCallback(async (newToken: string, newUserId: string) => {
    await SecureStore.setItemAsync(TOKEN_KEY, newToken)
    await SecureStore.setItemAsync(USER_ID_KEY, newUserId)
    setToken(newToken)
    setUserId(newUserId)
  }, [])

  const signOut = useCallback(async () => {
    await SecureStore.deleteItemAsync(TOKEN_KEY)
    await SecureStore.deleteItemAsync(USER_ID_KEY)
    setToken(null)
    setUserId(null)
  }, [])

  return (
    <AuthContext.Provider value={{ token, userId, isLoading, api, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
