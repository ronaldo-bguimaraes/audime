import { useCallback } from "react"
import {
  View,
  Text,
  FlatList,
  RefreshControl,
  TouchableOpacity,
  StyleSheet,
} from "react-native"
import { router } from "expo-router"
import { useAuth } from "../../src/contexts/AuthContext"
import { useFetch } from "../../src/hooks/useFetch"
import { LoadingSpinner } from "../../src/components/LoadingSpinner"
import { ErrorMessage } from "../../src/components/ErrorMessage"
import { createDashboardApi, createExtracoesApi } from "shared"
import { formatBRL, maskChave, formatDate } from "shared"

export default function Dashboard() {
  const { api } = useAuth()

  const fetchData = useCallback(async () => {
    const dash = createDashboardApi(api)
    const extr = createExtracoesApi(api)
    const [resumo, notas, extracoes] = await Promise.all([
      dash.obterResumo(),
      dash.listarNotas(),
      extr.listar(10),
    ])
    return { resumo, notas, extracoes }
  }, [api])

  const { data, error, isLoading, refetch } = useFetch(fetchData)

  if (isLoading && !data) return <LoadingSpinner message="Carregando..." />
  if (error) return <ErrorMessage message={error} onRetry={refetch} />

  const { resumo, notas, extracoes } = data ?? { resumo: null, notas: [], extracoes: [] }

  const sections: { key: string; type: "resumo" | "notas" | "extracoes" }[] = [
    ...(resumo ? [{ key: "resumo", type: "resumo" as const }] : []),
    ...(notas.length > 0 ? [{ key: "notas", type: "notas" as const }] : []),
    ...(extracoes.length > 0 ? [{ key: "extracoes-header", type: "extracoes" as const }] : []),
  ]

  return (
    <FlatList
      style={styles.container}
      data={notas}
      keyExtractor={(item) => String(item.id_nota_analytics)}
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
          {notas.length > 0 && (
            <Text style={styles.sectionTitle}>Notas</Text>
          )}
        </>
      )}
      renderItem={({ item }) => (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>{item.empresa ?? "Sem empresa"}</Text>
          {item.chave_acesso && (
            <Text style={styles.cardSub}>{maskChave(item.chave_acesso)}</Text>
          )}
          {item.emissao && (
            <Text style={styles.cardDate}>{formatDate(item.emissao)}</Text>
          )}
          <Text style={styles.cardValue}>
            {item.valor_total != null ? formatBRL(item.valor_total) : "—"}
          </Text>
        </View>
      )}
      ListFooterComponent={() => (
        <>
          {extracoes.length > 0 && (
            <>
              <Text style={styles.sectionTitle}>Extrações recentes</Text>
              {extracoes.map((item) => (
                <TouchableOpacity
                  key={item.id_extracao}
                  style={styles.card}
                  onPress={() => router.push(`/extracao/${item.id_extracao}`)}
                >
                  <Text style={styles.cardTitle}>Extração #{item.id_extracao}</Text>
                  <Text style={styles.cardStatus}>{item.status}</Text>
                  <Text style={styles.cardDate}>
                    {item.created_at ? formatDate(item.created_at) : ""}
                  </Text>
                </TouchableOpacity>
              ))}
            </>
          )}
        </>
      )}
      ListEmptyComponent={() => (
        <View style={styles.emptyContainer}>
          <Text style={styles.empty}>Nenhuma nota encontrada</Text>
          <TouchableOpacity
            style={styles.emptyButton}
            onPress={() => router.push("/(tabs)/extrair")}
          >
            <Text style={styles.emptyButtonText}>Nova Extração</Text>
          </TouchableOpacity>
        </View>
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
    marginTop: 8,
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
  cardSub: {
    fontSize: 12,
    color: "#9CA3AF",
    fontFamily: "monospace",
    marginTop: 4,
  },
  cardDate: {
    fontSize: 12,
    color: "#9CA3AF",
    marginTop: 4,
  },
  cardValue: {
    fontSize: 16,
    fontWeight: "700",
    color: "#2563EB",
    marginTop: 4,
  },
  emptyContainer: {
    alignItems: "center",
    paddingTop: 48,
  },
  empty: {
    textAlign: "center",
    color: "#9CA3AF",
    fontSize: 14,
    marginBottom: 16,
  },
  emptyButton: {
    backgroundColor: "#2563EB",
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  emptyButtonText: {
    color: "#FFF",
    fontSize: 14,
    fontWeight: "600",
  },
})
