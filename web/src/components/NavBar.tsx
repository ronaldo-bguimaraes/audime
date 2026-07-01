import { Link, useNavigate } from "react-router";
import { useAuth } from "../hooks/useAuth";
import styles from "./NavBar.module.css";

export function NavBar() {
  const { isAuthenticated, logout, nome } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!isAuthenticated) return null;

  return (
    <header className={styles.header}>
      <nav className={styles.nav}>
        <Link to="/dashboard" className={styles.logo}>
          audime
        </Link>
        <div className={styles.links}>
          <Link to="/dashboard" className={styles.link}>
            Notas
          </Link>
          <Link to="/extrair" className={styles.link}>
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
