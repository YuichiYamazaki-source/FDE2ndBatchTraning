import { Link } from "react-router-dom";

const NotFound = () => {
  return (
    <div className="container mt-5 text-center">
      <h1 className="display-1">404</h1>
      <p className="lead">Page Not Found</p>
      <Link to="/dashboard" className="btn btn-primary">
        Go to Dashboard
      </Link>
    </div>
  );
};

export default NotFound;