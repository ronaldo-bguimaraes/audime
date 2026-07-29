import { Link, useNavigate, useLocation } from "react-router";
import { Zap } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import styles from "./NavBar.module.css";

export function NavBar() {
  const { isAuthenticated, logout, nome } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!isAuthenticated) return null;

  return (
    <header className={styles.header}>
      <nav className={styles.nav}>
        <Link to="/dashboard" className={styles.logo}>
          <Zap size={20} className={styles.logoIcon} />
          audime
        </Link>
        <div className={styles.links}>
          <Link
            to="/dashboard"
            className={`${styles.link} ${location.pathname === "/dashboard" ? styles.linkActive : ""}`}
          >
            Notas
          </Link>
          <Link
            to="/extrair"
            className={`${styles.link} ${location.pathname === "/extrair" ? styles.linkActive : ""}`}
          >
            Nova Extração
          </Link>
        </div>
        <div className={styles.userArea}>
          {nome && <span className={styles.userName}>{nome}</span>}
          <button
            type="button"
            className={styles.logoutBtn}
            onClick={handleLogout}
          >
            Sair
          </button>
        </div>
      </nav>
    </header>
  );
}
