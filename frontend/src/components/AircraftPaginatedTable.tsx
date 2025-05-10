"use client";

import { Button, Modal } from "react-bootstrap";
import { useCallback, useEffect, useState } from "react";
import { API_URL } from "@/config/env";
import { useUserStore } from "@/store/user-store";
import { toast } from "react-toastify";
import { Aircraft } from "@/models/aircraft.model";
import { AddAircraftModal } from "./AddAircraftModal";
import { PartPaginatedTable } from "./PartPaginatedTable";
import PaginatedTable from "./PaginatedTable";
import { PaginatedResponse } from "@/models/pagination.model";

const columns = [
  "#",
  "Seri Numarası",
  "Model",
  "Üreten",
  "Üretim Tarihi",
  "İşlemler",
];

export const AircraftPaginatedTable = () => {
  const [data, setData] = useState<Aircraft[]>([]);
  const [totalItems, setTotalItems] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [itemsPerPage] = useState<number>(10);
  const { tokens } = useUserStore();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [aircraftToDelete, setAircraftToDelete] = useState<number | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showPartsModal, setShowPartsModal] = useState(false);
  const [selectedAircraftId, setSelectedAircraftId] = useState<number | null>(
    null
  );

  const fetchData = useCallback(
    async (page: number = 1) => {
      try {
        const offset = (page - 1) * itemsPerPage;
        const response = await fetch(
          `${API_URL}/aircraft?limit=${itemsPerPage}&offset=${offset}`,
          {
            headers: {
              Authorization: `Bearer ${tokens?.access}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch aircraft data");
        }

        const responseData: PaginatedResponse<Aircraft> = await response.json();
        setData(responseData.data);
        setTotalItems(responseData.total);
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
    },
    [tokens?.access, itemsPerPage]
  );

  useEffect(() => {
    fetchData(currentPage);
  }, [fetchData, currentPage]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
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
        fetchData(currentPage);
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

  const handleShowParts = (aircraftId: number) => {
    setSelectedAircraftId(aircraftId);
    setShowPartsModal(true);
  };

  return (
    <>
      <PaginatedTable
        data={data}
        columns={columns}
        title="Uçak Listesi"
        onAdd={() => setShowAddModal(true)}
        itemsPerPage={itemsPerPage}
        totalItems={totalItems}
        currentPage={currentPage}
        onPageChange={handlePageChange}
        renderRow={(item, rowIndex) => (
          <tr key={rowIndex}>
            <td>{item.id}</td>
            <td>{item.serial_number}</td>
            <td>{item.model?.name}</td>
            <td>{item.assembled_by?.full_name}</td>
            <td>
              {item.assembled_at
                ? new Date(item.assembled_at as string).toLocaleDateString()
                : "-"}
            </td>
            <td>
              <div className="d-flex gap-2">
                <Button
                  variant="info"
                  size="sm"
                  onClick={() => handleShowParts(item.id)}
                >
                  Parçaları Göster
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => confirmDelete(item.id)}
                >
                  Sil
                </Button>
              </div>
            </td>
          </tr>
        )}
      />

      <AddAircraftModal
        show={showAddModal}
        onHide={() => setShowAddModal(false)}
        onAircraftAdded={() => fetchData(currentPage)}
      />

      <Modal
        show={showDeleteConfirm}
        onHide={() => setShowDeleteConfirm(false)}
      >
        <Modal.Header closeButton>
          <Modal.Title>Uçak Silme Onayı</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Bu uçağı silmek istediğinizden emin misiniz? Stoklar iade edilecek.
        </Modal.Body>
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

      <Modal
        show={showPartsModal}
        onHide={() => setShowPartsModal(false)}
        size="xl"
      >
        <Modal.Header closeButton>
          <Modal.Title>Uçak Parçaları</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedAircraftId && (
            <PartPaginatedTable aircraft_id={selectedAircraftId} />
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowPartsModal(false)}>
            Kapat
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};
