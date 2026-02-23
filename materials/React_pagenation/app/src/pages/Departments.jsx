import { useState } from "react";
import { departments, employees } from "../data/mockData";

const Departments = () => {
  const [selectedDeptId, setSelectedDeptId] = useState(null);

  // 選択された部署に所属する従業員を取得
  const filteredEmployees = selectedDeptId
    ? employees.filter((emp) => emp.departmentId === selectedDeptId)
    : [];

  // 選択された部署の情報を取得
  const selectedDept = departments.find((d) => d.id === selectedDeptId);

  return (
    <div className="container mt-4">
      <h2>Departments</h2>

      <div className="d-flex gap-2 flex-wrap mt-3">
        {departments.map((dept) => (
          <button
            key={dept.id}
            className={`btn ${
              selectedDeptId === dept.id ? "btn-primary" : "btn-outline-primary"
            }`}
            onClick={() => setSelectedDeptId(dept.id)}
          >
            {dept.name}
          </button>
        ))}
      </div>

      {selectedDept && (
        <div className="mt-4">
          <h4>Employees in {selectedDept.name}</h4>
          {filteredEmployees.length === 0 ? (
            <p className="text-muted">No employees in this department.</p>
          ) : (
            <ul className="list-group">
              {filteredEmployees.map((emp) => (
                <li key={emp.id} className="list-group-item">
                  {emp.name} - {emp.email}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default Departments;
