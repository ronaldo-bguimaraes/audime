import { useCallback } from "react"
import {
  View,
  Text,
  FlatList,
  RefreshControl,
  StyleSheet,
} from "react-native"
import { useAuth } from "../../src/contexts/AuthContext"
import { useFetch } from "../../src/hooks/useFetch"
import { LoadingSpinner } from "../../src/components/LoadingSpinner"
import { ErrorMessage } from "../../src/components/ErrorMessage"
import { createDashboardApi, createExtracoesApi } from "shared"
import { formatBRL, formatDate } from "shared"

export default function Dashboard() {
  const { api } = useAuth()

  const fetchData = useCallback(async () => {
    const dash = createDashboardApi(api)
    const extr = createExtracoesApi(api)
    const [resumo, extracoes] = await Promise.all([
      dash.obterResumo(),
      extr.listar(10),
    ])
    return { resumo, extracoes }
  }, [api])

  const { data, error, isLoading, refetch } = useFetch(fetchData)

  if (isLoading && !data) return <LoadingSpinner message="Carregando..." />
  if (error) return <ErrorMessage message={error} onRetry={refetch} />

  const { resumo, extracoes } = data ?? { resumo: null, extracoes: [] }

  return (
    <FlatList
      style={styles.container}
      data={extracoes}
      keyExtractor={(item) => String(item.id_extracao)}
      refreshControl={
        <RefreshControl refreshing={isLoading} onRefresh={refetch} />
      }
      ListHeaderComponent={() => (
        <>
          {resumo && (
            <View style={styles.resumoCard}>
              <Text style={styles.resumoTitle}>Resumo</Text>
              <View style={styles.resumoRow}>
                <View style={styles.resumoItem}>
                  <Text style={styles.resumoValue}>
                    {formatBRL(resumo.valor_total ?? 0)}
                  </Text>
                  <Text style={styles.resumoLabel}>Valor total</Text>
                </View>
                <View style={styles.resumoItem}>
                  <Text style={styles.resumoValue}>{resumo.total_notas}</Text>
                  <Text style={styles.resumoLabel}>Notas</Text>
                </View>
              </View>
            </View>
          )}
          <Text style={styles.sectionTitle}>Extrações recentes</Text>
        </>
      )}
      renderItem={({ item }) => (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Extração #{item.id_extracao}</Text>
          <Text style={styles.cardStatus}>{item.status}</Text>
          <Text style={styles.cardDate}>
            {item.created_at ? formatDate(item.created_at) : ""}
          </Text>
        </View>
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
  resumoCard: {
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
  resumoTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#111827",
    marginBottom: 12,
  },
  resumoRow: {
    flexDirection: "row",
    gap: 16,
  },
  resumoItem: {
    flex: 1,
    backgroundColor: "#F9FAFB",
    borderRadius: 8,
    padding: 12,
    alignItems: "center",
  },
  resumoValue: {
    fontSize: 20,
    fontWeight: "700",
    color: "#2563EB",
  },
  resumoLabel: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 4,
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
