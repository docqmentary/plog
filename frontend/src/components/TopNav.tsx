import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks";

export function TopNav(): JSX.Element {
  const { session, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/", { replace: true });
  };

  return (
    <header className="top-nav">
      <div className="nav-brand">
        <Link to="/">Plog</Link>
      </div>
      <nav className="nav-links">
        <Link to="/">Product</Link>
        {session ? <Link to="/dashboard">Dashboard</Link> : null}
      </nav>
      <div className="nav-actions">
        {session ? (
          <>
            <span className="nav-user">{session.display_name ?? session.email}</span>
            <button type="button" className="btn" onClick={handleLogout}>
              Log out
            </button>
          </>
        ) : (
          <Link className="btn" to="/login">
            Log in
          </Link>
        )}
      </div>
    </header>
  );
}

export default TopNav;
