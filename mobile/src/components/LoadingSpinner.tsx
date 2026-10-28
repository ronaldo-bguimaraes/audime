import { View, ActivityIndicator, StyleSheet, Text } from "react-native"

interface LoadingSpinnerProps {
  message?: string
}

export function LoadingSpinner({ message = "Carregando..." }: LoadingSpinnerProps) {
  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <ActivityIndicator size="large" color="#2563EB" />
        {message ? <Text style={styles.message}>{message}</Text> : null}
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F3F4F6",
    justifyContent: "center",
    alignItems: "center",
  },
  content: {
    alignItems: "center",
    padding: 24,
  },
  message: {
    marginTop: 16,
    fontSize: 16,
    color: "#6B7280",
    textAlign: "center",
  },
})
