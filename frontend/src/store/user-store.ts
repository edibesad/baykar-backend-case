import { AuthTokens } from "@/models/tokens.model";
import { User } from "@/models/user.model";
import { create } from "zustand";

interface UserState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setAuth: (user: User, tokens: AuthTokens) => void;
  logout: () => void;
  setLoading: (isLoading: boolean) => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: true,
  setAuth: (user: User, tokens: AuthTokens) =>
    set({
      user,
      tokens,
      isAuthenticated: true,
    }),
  logout: () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    return set({
      user: null,
      tokens: null,
      isAuthenticated: false,
    });
  },
  setLoading: (isLoading: boolean) =>
    set({
      isLoading,
    }),
}));
