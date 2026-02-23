import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { UserProvider } from "./context/UserContext";
import Header from "./components/Header";
import Footer from "./components/Footer";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import EmployeeList from "./pages/Employees/EmployeeList";
import EmployeeDetails from "./pages/Employees/EmployeeDetails";
import Departments from "./pages/Departments";
import Projects from "./pages/Projects";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound";

function App() {
  return (
    <UserProvider>
      <BrowserRouter>
        <div className="d-flex flex-column min-vh-100">
          <Header />
          
          <main className="flex-grow-1">
            <Routes>
              {/* Public Route */}
              <Route path="/login" element={<Login />} />

              {/* Protected Routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/employees"
                element={
                  <ProtectedRoute allowedRoles={["Admin", "Manager"]}>
                    <EmployeeList />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/employees/:id"
                element={
                  <ProtectedRoute allowedRoles={["Admin", "Manager"]}>
                    <EmployeeDetails />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/departments"
                element={
                  <ProtectedRoute allowedRoles={["Admin", "Manager"]}>
                    <Departments />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/projects"
                element={
                  <ProtectedRoute allowedRoles={["Admin", "Manager"]}>
                    <Projects />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                }
              />

              {/* Redirect root to dashboard */}
              <Route path="/" element={<Navigate to="/dashboard" />} />

              {/* 404 Page */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>

          <Footer />
        </div>
      </BrowserRouter>
    </UserProvider>
  );
}

export default App;