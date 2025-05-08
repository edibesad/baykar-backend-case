"use client";

import { Table, Pagination, Card, Button, Modal } from "react-bootstrap";
import { useCallback, useEffect, useState } from "react";
import { API_URL } from "@/config/env";
import { useUserStore } from "@/store/user-store";
import { toast } from "react-toastify";
import { Aircraft } from "@/models/aircraft.model";
import { AddAircraftModal } from "./AddAircraftModal";

const columns = [
  "#",
  "Seri Numarası",
  "Model",
  "Üreten",
  "Üretim Tarihi",
  "Kanat",
  "Gövde",
  "Kuyruk",
  "Avionik",
  "Motor",
  "İşlemler",
];

export const AircraftPaginatedTable = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [data, setData] = useState<Aircraft[]>([]);
  const { tokens } = useUserStore();
  const itemsPerPage = 10;
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [aircraftToDelete, setAircraftToDelete] = useState<number | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/aircraft`, {
        headers: {
          Authorization: `Bearer ${tokens?.access}`,
        },
      });
      const responseData = await response.json();
      setData(Array.isArray(responseData) ? responseData : []);
    } catch (error) {
      console.error("Error fetching aircraft data:", error);
      setData([]);
      toast.error("Uçak verileri yüklenirken bir hata oluştu", {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
      });
    }
  }, [tokens?.access]);

  useEffect(() => {
    fetchData();
  }, [fetchData, tokens?.access]);

  // Calculate total pages
  const totalPages = Math.ceil(data.length / itemsPerPage);

  // Get current items
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = data.slice(indexOfFirstItem, indexOfLastItem);

  // Change page
  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber);
  };

  const handleDelete = async (aircraftId: number) => {
    try {
      const response = await fetch(`${API_URL}/aircraft/${aircraftId}/`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${tokens?.access}`,
        },
      });

      if (response.ok) {
        toast.success("Uçak başarıyla silindi", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
        });
        fetchData();
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || "Uçak silinirken bir hata oluştu", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
        });
      }
    } catch (error) {
      toast.error(
        `Uçak silinirken bir hata oluştu: ${
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
    setShowDeleteConfirm(false);
    setAircraftToDelete(null);
  };

  const confirmDelete = (aircraftId: number) => {
    setAircraftToDelete(aircraftId);
    setShowDeleteConfirm(true);
  };

  // Generate pagination items
  const renderPaginationItems = () => {
    const items = [];

    // Previous button
    items.push(
      <Pagination.Prev
        key="prev"
        onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
        disabled={currentPage === 1}
      />
    );

    // Page numbers
    for (let number = 1; number <= totalPages; number++) {
      items.push(
        <Pagination.Item
          key={number}
          active={number === currentPage}
          onClick={() => handlePageChange(number)}
        >
          {number}
        </Pagination.Item>
      );
    }

    // Next button
    items.push(
      <Pagination.Next
        key="next"
        onClick={() => handlePageChange(Math.min(totalPages, currentPage + 1))}
        disabled={currentPage === totalPages || totalPages === 0}
      />
    );

    return items;
  };

  return (
    <>
      <Card className="min-h-3/4">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h4 className="mb-0">Uçak Listesi</h4>
          <Button variant="primary" onClick={() => setShowAddModal(true)}>
            Ekle
          </Button>
        </Card.Header>
        <Card.Body>
          <Table>
            <thead>
              <tr>
                {columns.map((column, index) => (
                  <th key={index}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {currentItems.map((item, rowIndex) => (
                <tr key={rowIndex}>
                  <td>{item.id}</td>
                  <td>{item.serial_number}</td>
                  <td>{item.model?.name}</td>
                  <td>{item.assambled_by?.full_name}</td>
                  <td>{new Date(item.assambled_at).toLocaleDateString()}</td>
                  <td>{item.wing?.serial_number}</td>
                  <td>{item.body?.serial_number}</td>
                  <td>{item.tail?.serial_number}</td>
                  <td>{item.avionic?.serial_number}</td>
                  <td>{item.engine?.serial_number}</td>
                  <td>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => confirmDelete(item.id)}
                    >
                      Sil
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>

          {totalPages > 1 && (
            <div className="d-flex justify-content-center mt-3">
              <Pagination>{renderPaginationItems()}</Pagination>
            </div>
          )}
        </Card.Body>
      </Card>

      <AddAircraftModal
        show={showAddModal}
        onHide={() => setShowAddModal(false)}
        onAircraftAdded={fetchData}
      />

      <Modal
        show={showDeleteConfirm}
        onHide={() => setShowDeleteConfirm(false)}
      >
        <Modal.Header closeButton>
          <Modal.Title>Uçak Silme Onayı</Modal.Title>
        </Modal.Header>
        <Modal.Body>Bu uçağı silmek istediğinizden emin misiniz?</Modal.Body>
        <Modal.Footer>
          <Button
            variant="secondary"
            onClick={() => setShowDeleteConfirm(false)}
          >
            İptal
          </Button>
          <Button
            variant="danger"
            onClick={() => aircraftToDelete && handleDelete(aircraftToDelete)}
          >
            Sil
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};
