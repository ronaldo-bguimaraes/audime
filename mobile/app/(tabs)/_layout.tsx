import { Tabs } from "expo-router"
import { Text } from "react-native"
import { Redirect } from "expo-router"
import { useAuth } from "../../src/contexts/AuthContext"
import { LoadingSpinner } from "../../src/components/LoadingSpinner"

export default function TabsLayout() {
  const { token, isLoading } = useAuth()

  if (isLoading) return <LoadingSpinner />
  if (!token) return <Redirect href="/login" />

  return (
    <Tabs screenOptions={{ headerShown: true }}>
      <Tabs.Screen
        name="dashboard"
        options={{
          title: "Dashboard",
          tabBarIcon: () => <Text>📊</Text>,
        }}
      />
      <Tabs.Screen
        name="extrair"
        options={{
          title: "Extrair NFC-e",
          tabBarIcon: () => <Text>➕</Text>,
        }}
      />
      <Tabs.Screen
        name="extracao/[id]"
        options={{
          href: null,
          title: "Extração",
        }}
      />
    </Tabs>
  )
}
