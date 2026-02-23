import { useState } from "react";

const ProjectAssignment = ({ projects, assignedIds, onAssign }) => {
  const [selectedProject, setSelectedProject] = useState("");
  
  const availableProjects = projects.filter(
    (p) => !assignedIds.includes(p.id)
  );

  const handleAssign = () => {
    if (selectedProject) {
      onAssign(Number(selectedProject));  //Notify Parents
      setSelectedProject("");
    }
  };

  return (
    <div className="card mt-3">
      <div className="card-body">
        <h5 className="card-title">Assign Project</h5>
        {availableProjects.length === 0 ? (
          <p className="text-muted">All projects are already assigned.</p>
        ) : (
          <div className="d-flex gap-2">
            <select
              className="form-select"
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
            >
              <option value="">Select a project</option>
              {availableProjects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            <button className="btn btn-success" onClick={handleAssign}>
              Assign
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectAssignment;