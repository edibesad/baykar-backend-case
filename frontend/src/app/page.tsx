"use client";

import Login from "@/components/Login";
import PageByTeam from "@/components/PageByTeam";
import { useUserStore } from "@/store/user-store";
import { Button, Container, Spinner } from "react-bootstrap";

export default function Home() {
  const { isAuthenticated, logout, isLoading, user } = useUserStore();

  if (isLoading) {
    return (
      <div
        className="d-flex justify-content-center align-items-center"
        style={{ height: "100vh" }}
      >
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  if (isAuthenticated) {
    return (
      <Container className="h-screen flex flex-col justify-around">
        <div className="d-flex justify-content-between align-items-center">
          <h1>Baykar Uçak Üretim ve Parça Takip Sistemi</h1>
          <Button onClick={() => logout()}>Çıkış Yap</Button>
        </div>
        <PageByTeam
          team={
            user?.team_responsibility as
              | "kuyruk"
              | "kanat"
              | "gövde"
              | "aviyonik"
              | "montaj"
              | null
          }
        />
      </Container>
    );
  }
  return <Login />;
}
