import { Navigate } from "react-router-dom";
import { useUserContext } from "../context/UserContext";

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user } = useUserContext();
    // not login
    if (!user) {
      return <Navigate to="/login" />;
    }

    if (allowedRoles && !allowedRoles.includes(user.role)) {
      return (
        <div className="container mt-5">
          <div className="alert alert-danger text-center">
            <h3>Access Denied</h3>
          <p>You do not have permission to view this page.</p>
        </div>
      </div>
    );
  }
  return children;
}

export default ProtectedRoute;
