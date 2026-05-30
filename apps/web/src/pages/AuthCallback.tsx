import { useEffect } from "react"
import { useSearchParams, useNavigate } from "react-router"
import { setToken } from "@/lib/auth"

function AuthCallback() {
  const [params] = useSearchParams()
  const navigate = useNavigate()

  useEffect(() => {
    const token = params.get("token")
    if (token) {
      setToken(token)
    }
    navigate("/", { replace: true })
  }, [params, navigate])

  return (
    <div className="flex min-h-screen items-center justify-center">
      <p className="text-sm text-muted-foreground">Autenticando...</p>
    </div>
  )
}

export default AuthCallback
