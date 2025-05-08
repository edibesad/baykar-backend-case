"use client";

import { Table, Pagination, Card, Button, Modal } from "react-bootstrap";
import { useCallback, useEffect, useState } from "react";
import { Part } from "@/models/part";
import { API_URL } from "@/config/env";
import { useUserStore } from "@/store/user-store";
import { AddPartModal } from "./AddPartModal";
import { toast } from "react-toastify";

const columns = [
  "#",
  "Seri numarası",
  "Tipi",
  "Uçak Modeli",
  "Üreten",
  "Kullanıldığı Uçak",
  "İşlemler",
];

export const PartPaginatedTable = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [data, setData] = useState<Part[]>([]);
  const { tokens } = useUserStore();
  const itemsPerPage = 10;
  const [showModal, setShowModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [partToDelete, setPartToDelete] = useState<number | null>(null);

  const fetchData = useCallback(async () => {
    const response = await fetch(`${API_URL}/parts`, {
      headers: {
        Authorization: `Bearer ${tokens?.access}`,
      },
    });
    const data = await response.json();
    setData(data);
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

  const handleShowModal = () => setShowModal(true);
  const handleCloseModal = () => setShowModal(false);
  const handlePartAdded = () => {
    fetchData();
  };

  const handleDelete = async (partId: number) => {
    try {
      const response = await fetch(`${API_URL}/parts/${partId}/`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${tokens?.access}`,
        },
      });

      if (response.ok) {
        toast.success("Parça başarıyla silindi", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
        });
        fetchData();
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || "Parça silinirken bir hata oluştu", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
        });
      }
    } catch (error) {
      toast.error(
        `Parça silinirken bir hata oluştu: ${
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
    setPartToDelete(null);
  };

  const confirmDelete = (partId: number) => {
    setPartToDelete(partId);
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
          <h4 className="mb-0">Parça Listesi</h4>
          <Button variant="primary" onClick={handleShowModal}>
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
                  <td>{item.type?.name}</td>
                  <td>{item.aircraft_model?.name}</td>
                  <td>{item.produced_by?.full_name}</td>
                  <td>{item.used_in_aircraft?.model?.name}</td>
                  <td>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => confirmDelete(item.id!)}
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

      <AddPartModal
        show={showModal}
        onHide={handleCloseModal}
        onPartAdded={handlePartAdded}
      />

      <Modal
        show={showDeleteConfirm}
        onHide={() => setShowDeleteConfirm(false)}
      >
        <Modal.Header closeButton>
          <Modal.Title>Parça Silme Onayı</Modal.Title>
        </Modal.Header>
        <Modal.Body>Bu parçayı silmek istediğinizden emin misiniz?</Modal.Body>
        <Modal.Footer>
          <Button
            variant="secondary"
            onClick={() => setShowDeleteConfirm(false)}
          >
            İptal
          </Button>
          <Button
            variant="danger"
            onClick={() => partToDelete && handleDelete(partToDelete)}
          >
            Sil
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};
