"use client";

import { Table, Pagination, Card, Button } from "react-bootstrap";
import { useEffect, useState } from "react";
import { Part } from "@/models/part";
import { API_URL } from "@/config/env";
import { useUserStore } from "@/store/user-store";
import { AddPartModal } from "./AddPartModal";

const columns = [
  "#",
  "Seri numarası",
  "Tipi",
  "Uçak Modeli",
  "Üreten",
  "Kullanıldığı Uçak",
];

export const PaginatedTable = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [data, setData] = useState<Part[]>([]);
  const { tokens } = useUserStore();
  const itemsPerPage = 10;
  const [showModal, setShowModal] = useState(false);

  const fetchData = async () => {
    const response = await fetch(`${API_URL}/parts`, {
      headers: {
        Authorization: `Bearer ${tokens?.access}`,
      },
    });
    const data = await response.json();
    setData(data);
  };

  useEffect(() => {
    fetchData();
  }, [tokens?.access]);

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
    </>
  );
};
