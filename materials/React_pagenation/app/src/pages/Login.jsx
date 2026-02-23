import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useUserContext } from "../context/UserContext";

const Login = () => {
  const [username, setUsername] = useState("");
  const [role, setRole] = useState("Admin");
  
  const { login } = useUserContext();
  const navigate = useNavigate();
  const handleSubmit = (e) => {
    e.preventDefault();

    if (username.trim() === "") {
        alert("Please enter your username");
        return;
    }

    login(username, role);
    navigate("/dashboard");
  };


  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header bg-primary text-white text-center">
              <h3>ERMS Login</h3>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>

                <div className="mb-3">
                  <label className="form-label">Username</label>
                  <input
                    type="text"
                    className="form-control"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Role</label>
                  <select
                    className="form-select"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                  >
                    <option value="Admin">Admin</option>
                    <option value="Manager">Manager</option>
                    <option value="Employee">Employee</option>
                  </select>
                </div>

                <button type="submit" className="btn btn-primary w-100">
                  Login
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;