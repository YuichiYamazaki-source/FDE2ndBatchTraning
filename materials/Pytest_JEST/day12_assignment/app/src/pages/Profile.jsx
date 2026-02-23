import { useState } from "react";
import {useUserContext } from "../context/UserContext";

const Profile = () => {
    const { user } = useUserContext();

    //Manage a display Name on local state
    const [displayName, setDisplayName] = useState(user?.username || "");

    const handleSave = () => {
        alert(`Display name updated to: ${displayName}`);
    };

  return (
    <div className="container mt-4">
      <h2>User Profile</h2>

      <div className="card mt-3">
        <div className="card-body">
          <p><strong>Username:</strong> {user?.username}</p>
          <p><strong>Role:</strong> {user?.role}</p>

          <hr />

          <div className="mb-3">
            <label className="form-label">Display Name</label>
            <input
              type="text"
              className="form-control"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
            />
          </div>

          <button className="btn btn-primary" onClick={handleSave}>
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile;