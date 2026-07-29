import { Redirect } from "expo-router"
import { useAuth } from "../src/contexts/AuthContext"
import { LoadingSpinner } from "../src/components/LoadingSpinner"

export default function Index() {
  const { token, isLoading } = useAuth()

  if (isLoading) return <LoadingSpinner message="Carregando..." />

  if (token) return <Redirect href="/(tabs)/dashboard" />

  return <Redirect href="/login" />
}
