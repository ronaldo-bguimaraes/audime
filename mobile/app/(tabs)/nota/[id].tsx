import { useCallback } from "react"
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
} from "react-native"
import { useLocalSearchParams, router } from "expo-router"
import { useAuth } from "../../../src/contexts/AuthContext"
import { useFetch } from "../../../src/hooks/useFetch"
import { LoadingSpinner } from "../../../src/components/LoadingSpinner"
import { ErrorMessage } from "../../../src/components/ErrorMessage"
import { createNotasApi, type Nota } from "shared"
import { formatBRL, formatDate } from "shared"

export default function Nota() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const { api } = useAuth()

  const fetchNota = useCallback(
    () => createNotasApi(api).obter(Number(id)),
    [api, id],
  )

  const { data, error, isLoading, refetch } = useFetch<Nota>(fetchNota)

  if (isLoading) return <LoadingSpinner message="Carregando nota..." />
  if (error) return <ErrorMessage message={error} onRetry={refetch} />
  if (!data) return <ErrorMessage message="Nota não encontrada" />

  const nota = data

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{nota.empresa}</Text>
        <Text style={styles.chave}>
          {nota.chave || "Sem chave de acesso"}
        </Text>
        <Text style={styles.detalhe}>Número: {nota.numero}</Text>
        <Text style={styles.detalhe}>Série: {nota.serie}</Text>
        <Text style={styles.detalhe}>{formatDate(nota.emissao)}</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Informações da Nota</Text>

        <View style={styles.infoRow}>
          <Text style={styles.label}>Valor Total:</Text>
          <Text style={styles.value}>
            {formatBRL(nota.valor_total)}
          </Text>
        </View>

        {nota.qtd_total_itens != null && (
          <View style={styles.infoRow}>
            <Text style={styles.label}>Quantidade de Itens:</Text>
            <Text style={styles.value}>{nota.qtd_total_itens}</Text>
          </View>
        )}

        {nota.extra?.emitente && (
          <View>
            <Text style={styles.subTitle}>Emitente</Text>
            <View style={styles.infoRow}>
              <Text style={styles.label}>CNPJ:</Text>
              <Text style={styles.value}>{nota.extra.emitente.cnpj}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.label}>Cidade:</Text>
              <Text style={styles.value}>{nota.extra.emitente.cidade}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.label}>UF:</Text>
              <Text style={styles.value}>{nota.extra.emitente.uf}</Text>
            </View>
          </View>
        )}

        {nota.extra?.protocolo_autorizacao && (
          <View>
            <Text style={styles.subTitle}>Protocolo de Autorização</Text>
            <View style={styles.infoRow}>
              <Text style={styles.label}>Número:</Text>
              <Text style={styles.value}>
                {nota.extra.protocolo_autorizacao.numero}
              </Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.label}>Data/Hora:</Text>
              <Text style={styles.value}>
                {nota.extra.protocolo_autorizacao.data_hora}
              </Text>
            </View>
          </View>
        )}

        {nota.extra?.formas_pagamento && nota.extra.formas_pagamento.length > 0 && (
          <View>
            <Text style={styles.subTitle}>Formas de Pagamento</Text>
            {nota.extra.formas_pagamento.map((forma: { tipo: string; valor: number | null }, idx: number) => (
              <View key={idx} style={styles.infoRow}>
                <Text style={styles.label}>{forma.tipo}:</Text>
                <Text style={styles.value}>
                  {forma.valor ? formatBRL(forma.valor) : "-"}
                </Text>
              </View>
            ))}
          </View>
        )}
      </View>

      {nota.items && nota.items.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Itens da Nota</Text>
          {nota.items.map((item: { id: number; item_descricao: string; item_quantidade: number; item_tipo_unidade: string | null; item_valor_total: number }, idx: number) => (
            <View key={item.id} style={styles.itemRow}>
              <View style={styles.itemInfo}>
                <Text style={styles.itemDescricao}>{item.item_descricao}</Text>
                <Text style={styles.itemDetalhe}>
                  Qtd: {item.item_quantidade} | Unid: {item.item_tipo_unidade}
                </Text>
              </View>
              <Text style={styles.itemValue}>
                {formatBRL(item.item_valor_total)}
              </Text>
            </View>
          ))}
        </View>
      )}

      <View style={styles.backContainer}>
        <Text style={styles.backLink} onPress={() => router.back()}>
          ← Voltar
        </Text>
      </View>
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
    marginBottom: 8,
  },
  chave: {
    fontSize: 12,
    color: "#9CA3AF",
    fontFamily: "monospace",
    marginBottom: 8,
  },
  detalhe: {
    fontSize: 14,
    color: "#6B7280",
    marginBottom: 4,
  },
  card: {
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
  cardTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#374151",
    marginBottom: 16,
  },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#F3F4F6",
  },
  label: {
    fontSize: 14,
    color: "#6B7280",
    fontWeight: "500",
  },
  value: {
    fontSize: 14,
    color: "#111827",
    fontWeight: "600",
  },
  subTitle: {
    fontSize: 15,
    fontWeight: "600",
    color: "#374151",
    marginBottom: 12,
    marginTop: 8,
  },
  itemRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#F9FAFB",
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  itemInfo: {
    flex: 1,
  },
  itemDescricao: {
    fontSize: 14,
    fontWeight: "500",
    color: "#111827",
    marginBottom: 4,
  },
  itemDetalhe: {
    fontSize: 12,
    color: "#6B7280",
  },
  itemValue: {
    fontSize: 14,
    fontWeight: "700",
    color: "#2563EB",
  },
  backContainer: {
    paddingVertical: 16,
    alignItems: "center",
  },
  backLink: {
    color: "#2563EB",
    fontSize: 14,
    fontWeight: "600",
  },
})
