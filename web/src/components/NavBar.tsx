import { Link, useNavigate, useLocation } from "react-router";
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
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" className={styles.logoIcon}>
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" fill="currentColor" />
          </svg>
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
