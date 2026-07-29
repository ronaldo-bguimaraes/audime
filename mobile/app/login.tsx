import { useState } from "react"
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from "react-native"
import { router } from "expo-router"
import { useAuth } from "../src/contexts/AuthContext"
import { createApiClient } from "shared"

const API_BASE = process.env.EXPO_PUBLIC_API_BASE_URL ?? ""

export default function Login() {
  const { signIn } = useAuth()
  const [email, setEmail] = useState("")
  const [code, setCode] = useState("")
  const [step, setStep] = useState<"email" | "code">("email")
  const [isLoading, setIsLoading] = useState(false)

  const api = createApiClient(API_BASE)

  async function handleSendCode() {
    if (!email.trim()) return
    setIsLoading(true)
    try {
      await api.post("/v1/auth/login", { email: email.trim() })
      setStep("code")
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Erro ao enviar código"
      Alert.alert("Erro", msg)
    } finally {
      setIsLoading(false)
    }
  }

  async function handleVerifyCode() {
    if (!code.trim()) return
    setIsLoading(true)
    try {
      const result = await api.post<{ token: string; user_id: string }>(
        "/v1/auth/verify",
        { email: email.trim(), code: code.trim() },
      )
      await signIn(result.token, result.user_id)
      router.replace("/(tabs)/dashboard")
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Código inválido"
      Alert.alert("Erro", msg)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <View style={styles.card}>
        <Text style={styles.title}>Audime</Text>
        <Text style={styles.subtitle}>
          {step === "email"
            ? "Digite seu email para receber o código"
            : "Digite o código recebido no email"}
        </Text>

        {step === "email" ? (
          <>
            <TextInput
              style={styles.input}
              placeholder="seu@email.com"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              editable={!isLoading}
            />
            <TouchableOpacity
              style={[styles.button, isLoading && styles.buttonDisabled]}
              onPress={handleSendCode}
              disabled={isLoading}
            >
              <Text style={styles.buttonText}>Enviar código</Text>
            </TouchableOpacity>
          </>
        ) : (
          <>
            <TextInput
              style={styles.input}
              placeholder="000000"
              value={code}
              onChangeText={setCode}
              keyboardType="number-pad"
              maxLength={6}
              editable={!isLoading}
            />
            <TouchableOpacity
              style={[styles.button, isLoading && styles.buttonDisabled]}
              onPress={handleVerifyCode}
              disabled={isLoading}
            >
              <Text style={styles.buttonText}>Entrar</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => setStep("email")}>
              <Text style={styles.link}>Trocar email</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F3F4F6",
    justifyContent: "center",
    padding: 24,
  },
  card: {
    backgroundColor: "#FFF",
    borderRadius: 16,
    padding: 24,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  title: {
    fontSize: 28,
    fontWeight: "700",
    color: "#111827",
    textAlign: "center",
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: "#6B7280",
    textAlign: "center",
    marginBottom: 24,
  },
  input: {
    borderWidth: 1,
    borderColor: "#D1D5DB",
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 16,
    backgroundColor: "#F9FAFB",
  },
  button: {
    backgroundColor: "#2563EB",
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: "center",
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: "#FFF",
    fontSize: 16,
    fontWeight: "600",
  },
  link: {
    color: "#2563EB",
    textAlign: "center",
    marginTop: 16,
    fontSize: 14,
  },
})
