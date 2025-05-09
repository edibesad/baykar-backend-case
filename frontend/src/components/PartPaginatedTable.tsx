"use client";

import { Button, Modal } from "react-bootstrap";
import { useCallback, useEffect, useState } from "react";
import { Part } from "@/models/part";
import { API_URL } from "@/config/env";
import { useUserStore } from "@/store/user-store";
import { AddPartModal } from "./AddPartModal";
import { toast } from "react-toastify";
import PaginatedTable from "./PaginatedTable";
import { PaginatedResponse } from "@/models/pagination.model";

const columns = [
  "#",
  "Seri numarası",
  "Tipi",
  "Uçak Modeli",
  "Üreten",
  "Kullanıldığı Uçak",
  "İşlemler",
];

type PartPaginatedTableProps = {
  aircraft_id?: number;
};

export const PartPaginatedTable = ({
  aircraft_id,
}: PartPaginatedTableProps) => {
  const [data, setData] = useState<Part[]>([]);
  const [totalItems, setTotalItems] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [itemsPerPage] = useState<number>(10);
  const { tokens } = useUserStore();
  const [showModal, setShowModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [partToDelete, setPartToDelete] = useState<number | null>(null);

  const fetchData = useCallback(
    async (page: number = 1) => {
      try {
        const offset = (page - 1) * itemsPerPage;
        let url = `${API_URL}/parts?limit=${itemsPerPage}&offset=${offset}`;

        if (aircraft_id) {
          url += `&aircraft_id=${aircraft_id}`;
        }

        const response = await fetch(url, {
          headers: {
            Authorization: `Bearer ${tokens?.access}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch parts data");
        }

        const responseData: PaginatedResponse<Part> = await response.json();
        setData(responseData.data);
        setTotalItems(responseData.total);
      } catch (error) {
        console.error("Error fetching parts data:", error);
        setData([]);
        toast.error("Parça verileri yüklenirken bir hata oluştu", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
        });
      }
    },
    [tokens?.access, aircraft_id, itemsPerPage]
  );

  useEffect(() => {
    fetchData(currentPage);
  }, [fetchData, currentPage]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleShowModal = () => setShowModal(true);
  const handleCloseModal = () => setShowModal(false);
  const handlePartAdded = () => {
    fetchData(1); // Reset to first page after adding a part
    setCurrentPage(1);
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
        fetchData(currentPage);
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

  return (
    <>
      <PaginatedTable
        data={data}
        columns={columns}
        title="Parça Listesi"
        onAdd={handleShowModal}
        itemsPerPage={itemsPerPage}
        totalItems={totalItems}
        currentPage={currentPage}
        onPageChange={handlePageChange}
        renderRow={(item, rowIndex) => (
          <tr key={rowIndex}>
            <td>{item.id}</td>
            <td>{item.serial_number}</td>
            <td>{item.type?.name}</td>
            <td>{item.aircraft_model?.name}</td>
            <td>{item.produced_by?.full_name}</td>
            <td>{item.used_in_aircraft?.serial_number}</td>
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
        )}
      />

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
