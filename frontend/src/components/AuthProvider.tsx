"use client";

import { useUserStore } from "@/store/user-store";
import { useEffect } from "react";
import { API_URL } from "@/config/env";

export default function AuthProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const { setAuth, setLoading } = useUserStore();

  useEffect(() => {
    setLoading(true);
    const access = localStorage.getItem("access");
    const refresh = localStorage.getItem("refresh");

    if (access && refresh) {
      // Fetch user data to validate token and get user info
      const fetchUser = async () => {
        try {
          const response = await fetch(`${API_URL}/me`, {
            headers: {
              Authorization: `Bearer ${access}`,
            },
          });

          if (response.ok) {
            const user = await response.json();
            setAuth(user, { access, refresh });
          } else {
            // Eğer token geçersizse, refresh token'ı kullan
            const refreshResponse = await fetch(`${API_URL}/refresh`, {
              headers: {
                Authorization: `Bearer ${refresh}`,
              },
            });

            if (refreshResponse.ok) {
              const user = await refreshResponse.json();
              setAuth(user, { access, refresh });
            } else {
              localStorage.removeItem("access");
              localStorage.removeItem("refresh");
            }
          }
        } catch (error) {
          console.error("Error fetching user:", error);
        } finally {
          setLoading(false);
        }
      };

      fetchUser();
    } else {
      // No tokens found, set loading to false immediately
      setLoading(false);
    }
  }, [setAuth, setLoading]);

  return <>{children}</>;
}
