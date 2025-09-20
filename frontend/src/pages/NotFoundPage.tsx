import { Link } from "react-router-dom";

export default function NotFoundPage(): JSX.Element {
  return (
    <main className="auth-page">
      <div className="auth-card" style={{ textAlign: "center" }}>
        <h1>Page not found</h1>
        <p className="auth-subtitle">The page you requested does not exist.</p>
        <Link className="btn primary" to="/">
          Go home
        </Link>
      </div>
    </main>
  );
}
