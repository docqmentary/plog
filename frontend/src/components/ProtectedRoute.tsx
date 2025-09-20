import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../hooks";

export function ProtectedRoute(): JSX.Element {
  const location = useLocation();
  const { session, isBootstrapping } = useAuth();

  if (isBootstrapping) {
    return <div className="page-loading">Loading session…</div>;
  }

  if (!session) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

export default ProtectedRoute;
