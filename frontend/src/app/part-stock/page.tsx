"use client";

import PartStockPage from "@/components/PartStockPage";
import { useUserStore } from "@/store/user-store";
import { Spinner } from "react-bootstrap";
import Login from "@/components/Login";

export default function Page() {
  const { isAuthenticated, isLoading } = useUserStore();

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

  if (!isAuthenticated) {
    return <Login />;
  }

  return <PartStockPage />;
}
