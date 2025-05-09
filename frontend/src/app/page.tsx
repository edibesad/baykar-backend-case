"use client";

import Login from "@/components/Login";
import PageByTeam from "@/components/PageByTeam";
import { useUserStore } from "@/store/user-store";
import { Button, Container, Spinner } from "react-bootstrap";
import Link from "next/link";

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
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h1>Baykar Uçak Üretim ve Parça Takip Sistemi</h1>
          <div>
            <Link href="/part-stock" passHref>
              <Button variant="primary" className="me-2">
                Parça Stokları
              </Button>
            </Link>
            <Button onClick={() => logout()}>Çıkış Yap</Button>
          </div>
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
