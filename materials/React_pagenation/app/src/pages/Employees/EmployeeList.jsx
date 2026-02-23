import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { employees as initialEmployees, departments } from "../../data/mockData";
import { useUserContext } from "../../context/UserContext";

const EmployeeList = () => {
  const [employeeList, setEmployeeList] = useState(initialEmployees);
  const { user } = useUserContext();
  const navigate = useNavigate();

  // delete
  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this employee?")) {
      setEmployeeList(employeeList.filter((emp) => emp.id !== id));
    }
  };

  // helper function
  const getDepartmentName = (deptId) => {
    const dept = departments.find((d) => d.id === deptId);
    return dept ? dept.name : "Unknown";
  };

  return (
    <div className="container mt-4">
      <h2>Employee List</h2>
      <table className="table table-striped table-hover mt-3">
        <thead className="table-dark">
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Department</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {employeeList.map((emp) => (
            <tr key={emp.id}>
              <td>{emp.id}</td>
              <td>{emp.name}</td>
              <td>{emp.email}</td>
              <td>{getDepartmentName(emp.departmentId)}</td>
              <td>
                <button
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