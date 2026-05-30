import { useEffect } from "react"
import { useNavigate } from "react-router"
import { getToken } from "@/lib/auth"
import { API } from "@/lib/auth"

function Login() {
  const navigate = useNavigate();

  function handleLogin() {
    if (getToken()) {
      navigate("/", { replace: true })
    }
  }

  useEffect(handleLogin, [navigate])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-4">
      <div className="space-y-3 text-center">
        <h1 className="text-4xl font-semibold tracking-tight">Audime</h1>
        <p className="max-w-md text-sm text-muted-foreground">
          Faça login com sua conta Google para continuar.
        </p>
      </div>

      <h1>
        frontend: {API}
      </h1>

      <a href={`${API}/auth/google`}>
        <button
          data-slot="button"
          data-variant="default"
          data-size="lg"
          className="inline-flex items-center gap-3 rounded-lg border bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground transition-all hover:bg-primary/80"
        >
          Fazer login com o Google
        </button>
      </a>
    </div>
  )
}

export default Login
