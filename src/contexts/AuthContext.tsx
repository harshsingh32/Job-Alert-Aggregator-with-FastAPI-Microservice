import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthTokens } from '../types';
import { authAPI, setAuthTokens, getAuthTokens, clearAuthTokens } from '../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: {
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    password: string;
    password_confirm: string;
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const tokens = getAuthTokens();
      if (tokens) {
        try {
          const userData = await authAPI.getProfile();
          setUser(userData);
        } catch (error) {
          clearAuthTokens();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const tokens = await authAPI.login({ email, password });
    setAuthTokens(tokens);
    setUser(tokens.user);
  };

  const register = async (userData: {
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    password: string;
    password_confirm: string;
  }) => {
    const tokens = await authAPI.register(userData);
    setAuthTokens(tokens);
    setUser(tokens.user);
  };

  const logout = () => {
    clearAuthTokens();
    setUser(null);
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};