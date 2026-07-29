import { ActivityIndicator, View, Text, StyleSheet } from "react-native"

type Props = {
  message?: string
}

export function LoadingSpinner({ message }: Props) {
  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#2563EB" />
      {message && <Text style={styles.text}>{message}</Text>}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 24,
  },
  text: {
    marginTop: 12,
    fontSize: 14,
    color: "#6B7280",
  },
})
