"use client";

import { ReactNode, useState } from "react";
import { Card, Table, Pagination, Button } from "react-bootstrap";

interface PaginatedTableProps<T> {
  data: T[];
  itemsPerPage?: number;
  columns: string[];
  title: string;
  renderRow: (item: T, index: number) => ReactNode;
  onAdd?: () => void;
  addButtonText?: string;
  className?: string;
  headerActions?: ReactNode;
  // Server-side pagination props
  totalItems?: number;
  currentPage?: number;
  onPageChange?: (page: number) => void;
}

export default function PaginatedTable<T>({
  data,
  itemsPerPage = 10,
  columns,
  title,
  renderRow,
  onAdd,
  addButtonText = "Üret",
  className = "min-h-3/4",
  headerActions,
  // Server-side pagination props
  totalItems,
  currentPage: controlledCurrentPage,
  onPageChange,
}: PaginatedTableProps<T>) {
  const [internalCurrentPage, setInternalCurrentPage] = useState(1);

  // Use either controlled or internal state
  const currentPage = controlledCurrentPage || internalCurrentPage;

  // Calculate total pages based on either server total or local data length
  const totalPages = totalItems
    ? Math.ceil(totalItems / itemsPerPage)
    : Math.ceil(data.length / itemsPerPage);

  // For client-side pagination only
  const currentItems = onPageChange
    ? data // If using server-side pagination, all data is current
    : data.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  // Change page function
  const handlePageChange = (pageNumber: number) => {
    if (onPageChange) {
      // Server-side pagination
      onPageChange(pageNumber);
    } else {
      // Client-side pagination
      setInternalCurrentPage(pageNumber);
    }
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
    <Card className={className}>
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h4 className="mb-0">{title}</h4>
        <div className="d-flex gap-2">
          {headerActions}
          {onAdd && (
            <Button variant="primary" onClick={onAdd}>
              {addButtonText}
            </Button>
          )}
        </div>
      </Card.Header>
      <Card.Body>
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              {columns.map((column, index) => (
                <th key={index}>{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentItems.map((item, index) => renderRow(item, index))}
          </tbody>
        </Table>

        {totalPages > 1 && (
          <div className="d-flex justify-content-center mt-3">
            <Pagination>{renderPaginationItems()}</Pagination>
          </div>
        )}
      </Card.Body>
    </Card>
  );
}
