import { FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { login } from "../api/auth";
import { useAuth } from "../hooks";

export default function LoginPage(): JSX.Element {
  const { setSession } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("dev@example.com");
  const [idToken, setIdToken] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from = (location.state as { from?: Location } | undefined)?.from?.pathname ?? "/dashboard";

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      if (idToken.trim()) {
        // Real Google sign-in would provide this token; left as placeholder.
        const response = await login({ id_token: idToken.trim() });
        setSession(response);
      } else {
        const response = await login({ dev_user: email.trim() });
        setSession(response);
      }
      navigate(from, { replace: true });
    } catch (err) {
      setError((err as Error).message || "Unable to log in");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <div className="auth-card">
        <h1>Welcome back</h1>
        <p className="auth-subtitle">
          Use a Google ID token or the development shortcut email to enter the Plog workspace.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label htmlFor="devEmail">Development email (shortcut)</label>
          <input
            id="devEmail"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="clinic-owner@example.com"
            required={!idToken}
            disabled={isSubmitting}
          />

          <div className="divider">
            <span>or</span>
          </div>

          <label htmlFor="idToken">Google ID token</label>
          <input
            id="idToken"
            type="text"
            value={idToken}
            onChange={(event) => setIdToken(event.target.value)}
            placeholder="Paste ID token from Google sign-in"
            disabled={isSubmitting}
          />

          {error ? <p className="form-error">{error}</p> : null}

          <button type="submit" className="btn primary" disabled={isSubmitting}>
            {isSubmitting ? "Signing in…" : "Continue"}
          </button>
        </form>

        <p className="auth-footer">
          Need an overview first? <Link to="/">Return to the product page.</Link>
        </p>
      </div>
    </main>
  );
}



