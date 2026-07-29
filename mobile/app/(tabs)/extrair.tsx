import { useState, useCallback } from "react"
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  RefreshControl,
  StyleSheet,
  Alert,
} from "react-native"
import { router } from "expo-router"
import { useAuth } from "../../src/contexts/AuthContext"
import { useFetch } from "../../src/hooks/useFetch"
import { LoadingSpinner } from "../../src/components/LoadingSpinner"
import { ErrorMessage } from "../../src/components/ErrorMessage"
import { createExtracoesApi, FetchError } from "shared"
import { formatDate } from "shared"

export default function Extrair() {
  const { api } = useAuth()
  const [url, setUrl] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const extracoesApi = createExtracoesApi(api)

  const fetchExtracoes = useCallback(
    () => extracoesApi.listar(10),
    [api],
  )

  const { data: extracoes, error, isLoading, refetch } = useFetch(fetchExtracoes)

  async function handleSubmit() {
    if (!url.trim()) return
    setIsSubmitting(true)
    try {
      const result = await extracoesApi.criar(url.trim())
      router.push(`/extracao/${result.id_extracao}`)
    } catch (err: unknown) {
      const msg = err instanceof FetchError ? err.message : "Erro ao criar extração"
      Alert.alert("Erro", msg)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <FlatList
      style={styles.container}
      data={extracoes ?? []}
      keyExtractor={(item) => String(item.id_extracao)}
      refreshControl={
        <RefreshControl refreshing={isLoading} onRefresh={refetch} />
      }
      ListHeaderComponent={() => (
        <>
          <View style={styles.form}>
            <Text style={styles.label}>URL da NFC-e</Text>
            <TextInput
              style={styles.input}
              placeholder="https://..."
              value={url}
              onChangeText={setUrl}
              autoCapitalize="none"
              autoCorrect={false}
              editable={!isSubmitting}
            />
            <TouchableOpacity
              style={[styles.button, isSubmitting && styles.buttonDisabled]}
              onPress={handleSubmit}
              disabled={isSubmitting}
            >
              <Text style={styles.buttonText}>
                {isSubmitting ? "Extraindo..." : "Extrair NFC-e"}
              </Text>
            </TouchableOpacity>
          </View>
          <Text style={styles.sectionTitle}>Extrações recentes</Text>
        </>
      )}
      renderItem={({ item }) => (
        <TouchableOpacity
          style={styles.card}
          onPress={() => router.push(`/extracao/${item.id_extracao}`)}
        >
          <Text style={styles.cardTitle}>Extração #{item.id_extracao}</Text>
          <Text style={styles.cardStatus}>{item.status}</Text>
          <Text style={styles.cardDate}>
            {item.created_at ? formatDate(item.created_at) : ""}
          </Text>
        </TouchableOpacity>
      )}
      ListEmptyComponent={() => (
        <Text style={styles.empty}>Nenhuma extração encontrada</Text>
      )}
    />
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F3F4F6",
    padding: 16,
  },
  form: {
    backgroundColor: "#FFF",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  label: {
    fontSize: 14,
    fontWeight: "600",
    color: "#374151",
    marginBottom: 8,
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
  sectionTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#374151",
    marginBottom: 12,
  },
  card: {
    backgroundColor: "#FFF",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#111827",
  },
  cardStatus: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 4,
  },
  cardDate: {
    fontSize: 12,
    color: "#9CA3AF",
    marginTop: 4,
  },
  empty: {
    textAlign: "center",
    color: "#9CA3AF",
    marginTop: 32,
    fontSize: 14,
  },
})
