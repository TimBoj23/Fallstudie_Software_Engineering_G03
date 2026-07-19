import Sidebar from "./Sidebar.jsx";
import Header from "./Header.jsx";

export default function AppShell({ children, page, setPage, user, isLoggedIn, isAdmin, onLogout }) {
  return (
    <div className="app-shell">
      <Sidebar
        activePage={page}
        setPage={setPage}
        isLoggedIn={isLoggedIn}
        isAdmin={isAdmin}
      />
      <div className="app-main">
        <Header user={user} isLoggedIn={isLoggedIn} onLogout={onLogout} setPage={setPage} />
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
