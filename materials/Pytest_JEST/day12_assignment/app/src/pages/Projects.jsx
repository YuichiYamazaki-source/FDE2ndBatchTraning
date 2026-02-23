import { useState } from "react";
import { projects, employees } from "../data/mockData";

const Projects = () => {
  const [selectedProjectId, setSelectedProjectId] = useState(null);

  // Get a selected Project Information
  const selectedProject = projects.find((p) => p.id === selectedProjectId);

  //Get a selected employee who joins a project
  const assignedEmployees = selectedProject ? employees.filter((emp) => selectedProject.employeeIds.includes(emp.id)): [];

  return (
    <div className="container mt-4">
      <h2>Projects</h2>

      <div className="row mt-3">
        {projects.map((project) => (
          <div key={project.id} className="col-md-6 mb-3">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">{project.name}</h5>
                <p className="card-text">
                  <span className={`badge ${project.status === "Active" ? "bg-success" : "bg-secondary"}`}>
                    {project.status}
                  </span>
                </p>
                <p className="text-muted">
                  Assigned: {project.employeeIds.length} employees
                </p>
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => setSelectedProjectId(project.id)}
                >
                  View Details
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {selectedProject && (
        <div className="card mt-4">
          <div className="card-header bg-info text-white">
            <h4>Project Details: {selectedProject.name}</h4>
          </div>
          <div className="card-body">
            <p><strong>Status:</strong> {selectedProject.status}</p>
            <p><strong>Assigned Employees:</strong></p>
            <ul className="list-group">
              {assignedEmployees.map((emp) => (
                <li key={emp.id} className="list-group-item">
                  {emp.name} - {emp.email}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default Projects;