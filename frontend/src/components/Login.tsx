"use client";

import { API_URL } from "@/config/env";
import { useState } from "react";
import { Form, Button, Container, Row, Col } from "react-bootstrap";
import { useUserStore } from "@/store/user-store";
import { toast } from "react-toastify";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { setAuth, isLoading, setLoading } = useUserStore();
  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/auth/`, {
        headers: {
          "Content-Type": "application/json",
        },
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();

      if (response.ok) {
        const tokens = {
          access: data.access,
          refresh: data.refresh,
        };
        const user = data.user;

        setAuth(user, tokens);
        localStorage.setItem("access", tokens.access);
        localStorage.setItem("refresh", tokens.refresh);
      } else {
        console.log("response", response);
        const errorMessage = data.detail || "Giriş başarısız";
        throw new Error(errorMessage);
      }
    } catch (error: unknown) {
      console.log(error);
      if (error instanceof Error) {
        toast.error(error.message, {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
        });
      } else {
        toast.error("Beklenmeyen bir hata oluştu", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center h-screen">
      <Container>
        <Row className="justify-content-center">
          <Col xs={12} md={6} lg={4}>
            <h1 className="text-center mb-4">Giriş</h1>
            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3">
                <Form.Control
                  type="text"
                  placeholder="Kullanıcı Adı"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Control
                  type="password"
                  placeholder="Şifre"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </Form.Group>
              <Button
                variant="primary"
                type="submit"
                className="w-100"
                disabled={isLoading}
              >
                {isLoading ? "Giriş Yapılıyor..." : "Giriş Yap"}
              </Button>
            </Form>
          </Col>
        </Row>
      </Container>
    </div>
  );
}
