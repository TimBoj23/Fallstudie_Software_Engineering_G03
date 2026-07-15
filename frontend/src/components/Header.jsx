import { LogIn, LogOut, UserRound } from "lucide-react";
import Button from "./Button.jsx";

export default function Header({ user, isLoggedIn, onLogout, setPage }) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">RePlan Workspace</p>
        <h1>Räume und Ressourcen buchen</h1>
      </div>
      <div className="topbar-actions">
        {isLoggedIn ? (
          <>
            <div className="user-pill">
              <UserRound size={16} />
              <span>{user?.name || user?.email}</span>
              {user?.role === "admin" && <strong>Admin</strong>}
            </div>
            <Button variant="secondary" icon={LogOut} onClick={onLogout}>
              Logout
            </Button>
          </>
        ) : (
          <Button icon={LogIn} onClick={() => setPage("login")}>
            Login
          </Button>
        )}
      </div>
    </header>
  );
}
