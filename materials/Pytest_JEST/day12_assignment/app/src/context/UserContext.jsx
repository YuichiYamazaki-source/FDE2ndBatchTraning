import { createContext, useContext, useState } from "react";

// 1. Create Context
const UserContext = createContext(null);

// 2. Provider Component
// Provider privides accesibility to all component in app.
export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  const login = (username, role) => {
    setUser({ username, role, isLoggedIn: true});
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <UserContext.Provider value={{ user, login, logout}}>
      {children}
    </UserContext.Provider>
  );
};

// 3. CostomHook
// It enable Other Files to access to user, login and logout.
export const useUserContext = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error("useUserContext must be used within a UserProvider");
  }
  return context;
};