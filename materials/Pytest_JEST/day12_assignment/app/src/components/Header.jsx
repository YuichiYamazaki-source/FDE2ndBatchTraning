import { Link, useNavigate } from "react-router-dom";
import { useUserContext } from "../context/UserContext";

const Header = () => {
  const { user, logout} = useUserContext();
  const navigate = useNavigate();  // For moving page
  const handleLogout = () => {
    logout();
    navigate("/login");
  };
// RRMS: Employee Resource Management System

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand" to="/dashboard">ERMS</Link>

        {/* Please registlate Employee*/}
        {user && (
          <>
            <ul className="navbar-nav me-auto">
              <li className="nav-item">
                <Link className="nav-link" to="/dashboard">Dashboard</Link>
              </li>

              {/* Admin と Manager だけ表示 */}
              {(user.role === "Admin" || user.role === "Manager") && (
                <>
                  <li className="nav-item">
                    <Link className="nav-link" to="/employees">Employees</Link>
                  </li>
                  <li className="nav-item">
                    <Link className="nav-link" to="/departments">Departments</Link>
                  </li>
                  <li className="nav-item">
                    <Link className="nav-link" to="/projects">Projects</Link>
                  </li>
                </>
              )}

              <li className="nav-item">
                <Link className="nav-link" to="/profile">Profile</Link>
              </li>
            </ul>

            {/* ユーザー情報とログアウトボタン */}
            <span className="navbar-text me-3">
              {user.username} ({user.role})
            </span>
            <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>
              Logout
            </button>
          </>
        )}
      </div>
    </nav>
  );
};

export default Header;