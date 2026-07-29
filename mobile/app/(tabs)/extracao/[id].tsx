import { useCallback } from "react"
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  StyleSheet,
  Platform,
} from "react-native"
import { useLocalSearchParams } from "expo-router"
import { useAuth } from "../../../src/contexts/AuthContext"
import { useFetch } from "../../../src/hooks/useFetch"
import { LoadingSpinner } from "../../../src/components/LoadingSpinner"
import { ErrorMessage } from "../../../src/components/ErrorMessage"
import { createExtracoesApi, createDashboardApi } from "shared"
import { formatDate } from "shared"

export default function ExtracaoDetail() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const { api } = useAuth()

  const fetchDetails = useCallback(async () => {
    const extr = createExtracoesApi(api)
    const dash = createDashboardApi(api)
    const [extracao, nota] = await Promise.all([
      extr.obter(Number(id)),
      dash.obterNota(Number(id)).catch(() => null),
    ])
    return { extracao, nota }
  }, [api, id])

  const { data, error, isLoading, refetch } = useFetch(fetchDetails)

  if (isLoading && !data) return <LoadingSpinner message="Carregando..." />
  if (error) return <ErrorMessage message={error} onRetry={refetch} />

  const { extracao, nota } = data ?? { extracao: null, nota: null }

  if (!extracao) {
    return <ErrorMessage message="Extração não encontrada" />
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={isLoading} onRefresh={refetch} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>Extração #{extracao.id_extracao}</Text>
        <Text style={styles.status}>{extracao.status}</Text>
        {extracao.url && (
          <Text style={styles.url}>{extracao.url}</Text>
        )}
        {extracao.created_at && (
          <Text style={styles.date}>{formatDate(extracao.created_at)}</Text>
        )}
      </View>

      {nota && (
        <View style={styles.notaCard}>
          <Text style={styles.notaTitle}>{nota.empresa}</Text>
          <Text style={styles.notaValor}>Valor total: R$ {Number(nota.valor_total).toFixed(2)}</Text>
          {nota.emissao && (
            <Text style={styles.notaDate}>{formatDate(nota.emissao)}</Text>
          )}
        </View>
      )}

      {extracao.steps && extracao.steps.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Pipeline</Text>
          {extracao.steps.map((step) => (
            <View key={step.ordem} style={styles.step}>
              <View
                style={[
                  styles.stepDot,
                  step.status === "CONCLUIDO" && styles.stepDone,
                  step.status === "ERRO" && styles.stepError,
                  step.status === "PROCESSANDO" && styles.stepRunning,
                ]}
              />
              <View style={styles.stepContent}>
                <Text style={styles.stepName}>{step.etapa}</Text>
                {step.mensagem && (
                  <Text style={styles.stepMsg}>{step.mensagem}</Text>
                )}
              </View>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F3F4F6",
    padding: 16,
  },
  header: {
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
  title: {
    fontSize: 20,
    fontWeight: "700",
    color: "#111827",
  },
  status: {
    fontSize: 14,
    color: "#6B7280",
    marginTop: 4,
  },
  url: {
    fontSize: 12,
    color: "#9CA3AF",
    marginTop: 8,
  },
  date: {
    fontSize: 12,
    color: "#9CA3AF",
    marginTop: 4,
  },
  notaCard: {
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
  notaTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#111827",
  },
  notaValor: {
    fontSize: 14,
    color: "#374151",
    marginTop: 4,
  },
  notaDate: {
    fontSize: 12,
    color: "#9CA3AF",
    marginTop: 2,
  },
  section: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#374151",
    marginBottom: 8,
  },
  step: {
    flexDirection: "row",
    alignItems: "flex-start",
    backgroundColor: "#FFF",
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 1,
  },
  stepDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: "#D1D5DB",
    marginTop: 4,
    marginRight: 12,
  },
  stepDone: {
    backgroundColor: "#10B981",
  },
  stepError: {
    backgroundColor: "#EF4444",
  },
  stepRunning: {
    backgroundColor: "#F59E0B",
  },
  stepContent: {
    flex: 1,
  },
  stepName: {
    fontSize: 14,
    fontWeight: "600",
    color: "#111827",
  },
  stepMsg: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 2,
  },
})
