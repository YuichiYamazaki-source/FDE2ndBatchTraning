import { useState, useEffect } from "react";
import { employees, departments, projects } from "../data/mockData";
import { useUserContext } from "../context/UserContext";
import StatCard from "../components/StatCard";

const Dashboard = () => {
  const { user } =useUserContext();
  const [stats, setStats] = useState({
    totalEmployees: 0,
    totalDepartments: 0,
    activeProjects: 0,
  });

  // load data when a componets are display

  useEffect(() => {
    const activeCount = projects.filter((p) => p.status === "Active").length;
    
    setStats({
      totalEmployees: employees.length,
      totalDepartments: departments.length,
      activeProjects: activeCount,
    });
  }, []);

  return (
    <div className="container mt-4">
      <h2>Dashboard</h2>
      <p>Welcome, {user?.username}!</p>

      <div className="row mt-4">
        <StatCard title="Total Employees" value={stats.totalEmployees} color="primary" />
        <StatCard title="Total Departments" value={stats.totalDepartments} color="success" />
        <StatCard title="Active Projects" value={stats.activeProjects} color="warning" />
      </div>
    </div>
  );
};

export default Dashboard;