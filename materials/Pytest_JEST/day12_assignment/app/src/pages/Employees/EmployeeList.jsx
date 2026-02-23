import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useUserContext } from "../../context/UserContext";
import axios from "axios";

const EmployeeList = () => {
  const [employeeList, setEmployeeList] = useState([]);
  const { user } = useUserContext();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  //Fetch employees from API when componet mounts
  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await axios.get(
          "https://jsonplaceholder.typicode.com/users"
        );

        setEmployeeList(response.data);
      } catch (err) {
        setError("Failed to fetch employee data. Please try again later.");
        console.error("Error fetching employees:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchEmployees();
  }, []); // Fetch only once on mount

  // delete
  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this employee?")) {
      setEmployeeList(employeeList.filter((emp) => emp.id !== id));
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="container mt-5 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-3">Loading employees...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger" role="alert">
          <h4 className="alert-heading">Error!</h4>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  // Then your current return with the table...
  return (
    <div className="container mt-4">
      <h2>Employee List</h2>
      <table className="table table-striped table-hover mt-3">
        <thead className="table-dark">
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Company</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {employeeList.map((emp) => (
            <tr key={emp.id}>
              <td>{emp.id}</td>
              <td>{emp.name}</td>
              <td>{emp.email}</td>
              <td>{emp.phone}</td>
              <td>{emp.company.name}</td>
                <td><button
                  className="btn btn-info btn-sm me-2"
                  onClick={() => navigate(`/employees/${emp.id}`)}
                >
                  View
                </button>
                {user.role === "Admin" && (
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(emp.id)}
                  >
                    Delete
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default EmployeeList;