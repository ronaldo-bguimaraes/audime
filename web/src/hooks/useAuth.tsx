import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { requestCode, verifyCode, fetchMe } from "../api/auth";
import type { AuthState } from "../types";

interface AuthContextType extends AuthState {
  isAuthenticated: boolean;
  loading: boolean;
  sendCode: (email: string) => Promise<void>;
  verify: (code: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

function getStoredAuth(): AuthState {
  const token = localStorage.getItem("audime_token");
  const idUsuario = localStorage.getItem("audime_user_id");
  return {
    token,
    idUsuario: idUsuario ? Number(idUsuario) : null,
    nome: null,
    email: null,
  };
}

function clearStoredAuth() {
  localStorage.removeItem("audime_token");
  localStorage.removeItem("audime_user_id");
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthState>(getStoredAuth);
  const [loading, setLoading] = useState(false);

  // On mount, try to fetch user info if token exists
  useEffect(() => {
    if (auth.token && !auth.nome) {
      fetchMe()
        .then((user) => {
          setAuth((prev) => ({
            ...prev,
            nome: user.nome,
            email: user.email,
          }));
        })
        .catch(() => {
          // Token inválido ou expirado
          clearStoredAuth();
          setAuth({ token: null, idUsuario: null, nome: null, email: null });
        });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sendCode = useCallback(async (email: string) => {
    setLoading(true);
    try {
      await requestCode(email);
    } finally {
      setLoading(false);
    }
  }, []);

  const verify = useCallback(async (code: string) => {
    setLoading(true);
    try {
      const pendingEmail = localStorage.getItem("pending_email") ?? "";
      const result = await verifyCode(pendingEmail, code);
      if (result.status === "ok" && result.access_token) {
        localStorage.setItem("audime_token", result.access_token);
        if (result.id_usuario) {
          localStorage.setItem("audime_user_id", String(result.id_usuario));
        }
        localStorage.removeItem("pending_email");
        setAuth({
          token: result.access_token,
          idUsuario: result.id_usuario ?? null,
          nome: null,
          email: pendingEmail,
        });
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    clearStoredAuth();
    setAuth({ token: null, idUsuario: null, nome: null, email: null });
  }, []);

  return (
    <AuthContext.Provider
      value={{
        ...auth,
        isAuthenticated: !!auth.token,
        loading,
        sendCode,
        verify,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return ctx;
}
