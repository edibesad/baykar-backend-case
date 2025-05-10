"use client";

import { useState, useEffect, useCallback } from "react";
import { Button, Container, Modal } from "react-bootstrap";
import { AircraftPartStock } from "@/models/part_stock";
import { API_URL } from "@/config/env";
import { useUserStore } from "@/store/user-store";
import { toast } from "react-toastify";
import Link from "next/link";
import PaginatedTable from "./PaginatedTable";
import { PaginatedResponse } from "@/models/pagination.model";

export default function PartStockPage() {
  const [data, setData] = useState<AircraftPartStock[]>([]);
  const [totalItems, setTotalItems] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [itemsPerPage] = useState<number>(10);
  const [showAlerts, setShowAlerts] = useState(false);
  const { tokens } = useUserStore();

  // API'den veri çek
  const fetchData = useCallback(
    async (page: number = 1) => {
      try {
        const offset = (page - 1) * itemsPerPage;
        const response = await fetch(
          `${API_URL}/parts/stock/?limit=${itemsPerPage}&offset=${offset}`,
          {
            headers: {
              Authorization: `Bearer ${tokens?.access}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }

        const result: PaginatedResponse<AircraftPartStock> =
          await response.json();
        setData(result.data);
        setTotalItems(result.total);
      } catch (error) {
        toast.error(
          `Stok verisi alınırken bir hata oluştu: ${
            error instanceof Error ? error.message : "Bilinmeyen hata"
          }`,
          {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: false,
            closeOnClick: true,
          }
        );
      }
    },
    [tokens?.access, itemsPerPage]
  );

  useEffect(() => {
    fetchData(currentPage);
  }, [fetchData, currentPage]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  // Stok dışı ürünleri uyarılar için hesapla
  const outOfStockItems = Array.isArray(data)
    ? data.flatMap((aircraft) =>
        aircraft.parts
          .filter((part) => part.stock_count === 0)
          .map((part) => ({
            aircraft: aircraft.aircraft_model_name,
            part: part.part_type_name,
          }))
      )
    : [];

  // Tablo için düzleştirilmiş veriyi hazırla
  const flattenedData = Array.isArray(data)
    ? data.flatMap((aircraft) =>
        aircraft.parts.map((part) => ({
          aircraft_model_name: aircraft.aircraft_model_name,
          ...part,
        }))
      )
    : [];

  // Tablo sütunlarını tanımla
  const columns = [
    "Uçak Modeli",
    "Parça Tipi",
    "Toplam Üretilen",
    "Kullanılan",
    "Stok",
  ];

  return (
    <Container className="mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Parça Stok Durumu</h1>
        <div>
          <Button
            variant="warning"
            className="me-2"
            onClick={() => setShowAlerts(true)}
            disabled={outOfStockItems.length === 0}
          >
            Uyarılar{" "}
            {outOfStockItems.length > 0 && `(${outOfStockItems.length})`}
          </Button>
          <Link href="/" passHref>
            <Button variant="secondary">Ana Sayfa</Button>
          </Link>
        </div>
      </div>

      <PaginatedTable
        data={flattenedData}
        columns={columns}
        title="Uçak Modeli Bazında Parça Stokları"
        itemsPerPage={itemsPerPage}
        totalItems={totalItems}
        currentPage={currentPage}
        onPageChange={handlePageChange}
        renderRow={(item, index) => (
          <tr key={index}>
            <td>{item.aircraft_model_name}</td>
            <td>{item.part_type_name}</td>
            <td>{item.total_produced}</td>
            <td>{item.used_count}</td>
            <td className={item.stock_count === 0 ? "text-danger fw-bold" : ""}>
              {item.stock_count}
            </td>
          </tr>
        )}
      />

      {/* Uyarılar Modalı */}
      <Modal show={showAlerts} onHide={() => setShowAlerts(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Stok Uyarıları</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {outOfStockItems.length === 0 ? (
            <p>Stok uyarısı bulunmamaktadır.</p>
          ) : (
            <ul className="list-group">
              {outOfStockItems.map((item, index) => (
                <li key={index} className="list-group-item text-danger">
                  {item.aircraft} uçağının {item.part} parçasının stoğu tükendi
                </li>
              ))}
            </ul>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowAlerts(false)}>
            Kapat
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
}
