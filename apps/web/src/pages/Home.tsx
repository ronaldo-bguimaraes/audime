import { useEffect, useState } from "react"
import { useNavigate, Link } from "react-router"
import { Button } from "@/components/ui/button"
import { fetchUser, clearToken, type AuthUser } from "@/lib/auth"

function Home() {
  const [user, setUser] = useState<AuthUser["user"] | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchUser()
      .then((data) => setUser(data.user))
      .catch(() => navigate("/login", { replace: true }))
      .finally(() => setLoading(false))
  }, [navigate])

  function handleLogout() {
    clearToken()
    navigate("/login", { replace: true })
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-muted-foreground">Carregando...</p>
      </div>
    )
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-4xl flex-col px-4 py-6">
      <header className="flex items-center justify-between rounded-lg border bg-card px-6 py-4 shadow-sm">
        <div className="flex items-center gap-3">
          {user?.avatar && (
            <img
              src={user.avatar}
              alt={user.name ?? ""}
              className="size-9 rounded-full ring-2 ring-border"
            />
          )}
          <div>
            <p className="text-sm font-medium">{user?.name ?? "Sem nome"}</p>
            <p className="text-xs text-muted-foreground">{user?.email}</p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={handleLogout}>
          Sair
        </Button>
      </header>

      <main className="mt-6 flex flex-1 flex-col items-center justify-center gap-6">
        <div className="space-y-3 text-center">
          <h1 className="text-4xl font-semibold tracking-tight">Audime</h1>
          <p className="max-w-md text-sm text-muted-foreground">
            Abra o scanner QR integrado ao tema do app e leia códigos usando a câmera do dispositivo.
          </p>
        </div>
        <Link to="/scanner">
          <Button className="w-full max-w-xs">Abrir scanner QR</Button>
        </Link>
      </main>
    </div>
  )
}

export default Home
