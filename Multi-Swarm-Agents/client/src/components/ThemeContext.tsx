// ThemeContext.tsx
import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface ThemeContextType {
  lightMode: boolean;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [lightMode, setLightMode] = useState<boolean>(false);

  useEffect(() => {
    // Optionally, retrieve theme from localStorage to persist theme preference
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
      setLightMode(savedTheme === "light");
    }
  }, []);

  const toggleTheme = () => {
    setLightMode((prevMode) => {
      const newMode = !prevMode;
      localStorage.setItem("theme", newMode ? "light" : "dark");
      return newMode;
    });
  };

  return (
    <ThemeContext.Provider value={{ lightMode, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};
