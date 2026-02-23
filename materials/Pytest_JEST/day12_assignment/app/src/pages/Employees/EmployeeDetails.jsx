import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { employees, departments, projects } from "../../data/mockData";
import ProjectAssignment from "./ProjectAssignment";

const EmployeeDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // Search Employee by ID
  const employee = employees.find((emp) => emp.id === Number(id));

  const [assignedProjectIds, setAssignedProjectIds] =useState(
    employee ? employee.projectIds: []
  );

  // Not found
  if (!employee) {
    return (
      <div className="container mt-4">
        <div className="alert alert-danger">Employee not found.</div>
        <button className="btn-secondary" onClick={() => navigate("/employees")}>
          Back to List
        </button>
      </div>
    );
  }

  // Get a Name of Department
  const department = departments.find((d) => d.id === employee.departmentId);

  // Get a Project details that is assigned
  const assignedProjects = projects.filter((p) => 
    assignedProjectIds.includes(p.id)
  );

  // Callback
  const handleAssignProgect = (projectId) => {
    setAssignedProjectIds([...assignedProjectIds, projectId]);
  };

  return (
    <div className="container mt-4">
      <button className="btn btn-secondary mb-3" onClick={() => navigate("/employees")}>
        Back to List
      </button>

      <div className="card">
        <div className="card-header bg-primary text-white">
          <h3>{employee.name}</h3>
        </div>
        <div className="card-body">
          <p><strong>Email:</strong> {employee.email}</p>
          <p><strong>Department:</strong> {department?.name}</p>
          <p><strong>Assigned Projects:</strong></p>
          <ul className="list-group mb-3">
            {assignedProjects.map((p) => (
              <li key={p.id} className="list-group-item">
                {p.name} - {p.status}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 子コンポーネントに props とコールバックを渡す */}
      <ProjectAssignment
        projects={projects}
        assignedIds={assignedProjectIds}
        onAssign={handleAssignProject}
      />
    </div>
  );
};

export default EmployeeDetails;