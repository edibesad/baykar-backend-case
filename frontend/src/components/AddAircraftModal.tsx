"use client";

import { Modal, Button, Form } from "react-bootstrap";
import { useState, useEffect } from "react";
import { API_URL } from "@/config/env";
import { useUserStore } from "@/store/user-store";
import { toast } from "react-toastify";

interface AircraftModel {
  id: number;
  name: string;
}

interface AddAircraftModalProps {
  show: boolean;
  onHide: () => void;
  onAircraftAdded: () => void;
}

export const AddAircraftModal = ({
  show,
  onHide,
  onAircraftAdded,
}: AddAircraftModalProps) => {
  const [formData, setFormData] = useState({
    serial_number: "",
    model: "",
    wing_serial: "",
    body_serial: "",
    tail_serial: "",
    avionic_serial: "",
    engine_serial: "",
  });
  const [models, setModels] = useState<AircraftModel[]>([]);
  const { tokens } = useUserStore();

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch(`${API_URL}/aircraft-models/`, {
          headers: {
            Authorization: `Bearer ${tokens?.access}`,
          },
        });
        const data = await response.json();
        setModels(data);
      } catch (error) {
        console.error("Error fetching aircraft models:", error);
        toast.error("Uçak modelleri yüklenirken bir hata oluştu", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
        });
      }
    };

    if (show) {
      fetchModels();
    }
  }, [show, tokens?.access]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/aircraft/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${tokens?.access}`,
        },
        body: JSON.stringify({
          ...formData,
          model: parseInt(formData.model),
        }),
      });

      if (response.ok) {
        toast.success("Uçak başarıyla eklendi", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
        });
        onAircraftAdded();
        onHide();
        setFormData({
          serial_number: "",
          model: "",
          wing_serial: "",
          body_serial: "",
          tail_serial: "",
          avionic_serial: "",
          engine_serial: "",
        });
      } else {
        console.log(response);
        const errorData = await response.json();
        toast.error(errorData.detail || "Uçak eklenirken bir hata oluştu", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
        });
      }
    } catch (error) {
      console.error("Error adding aircraft:", error);
      toast.error("Uçak eklenirken bir hata oluştu", {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
      });
    }
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>Yeni Uçak Ekle</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Seri Numarası</Form.Label>
            <Form.Control
              type="text"
              name="serial_number"
              value={formData.serial_number}
              onChange={handleChange}
              required
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Model</Form.Label>
            <Form.Select
              name="model"
              value={formData.model}
              onChange={handleChange}
              required
            >
              <option value="">Model Seçin</option>
              {models.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.name}
                </option>
              ))}
            </Form.Select>
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Kanat Seri Numarası</Form.Label>
            <Form.Control
              type="text"
              name="wing_serial"
              value={formData.wing_serial}
              onChange={handleChange}
              required
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Gövde Seri Numarası</Form.Label>
            <Form.Control
              type="text"
              name="body_serial"
              value={formData.body_serial}
              onChange={handleChange}
              required
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Kuyruk Seri Numarası</Form.Label>
            <Form.Control
              type="text"
              name="tail_serial"
              value={formData.tail_serial}
              onChange={handleChange}
              required
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Avionik Seri Numarası</Form.Label>
            <Form.Control
              type="text"
              name="avionic_serial"
              value={formData.avionic_serial}
              onChange={handleChange}
              required
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Motor Seri Numarası</Form.Label>
            <Form.Control
              type="text"
              name="engine_serial"
              value={formData.engine_serial}
              onChange={handleChange}
              required
            />
          </Form.Group>
          <div className="d-flex justify-content-end gap-2">
            <Button variant="secondary" onClick={onHide}>
              İptal
            </Button>
            <Button variant="primary" type="submit">
              Ekle
            </Button>
          </div>
        </Form>
      </Modal.Body>
    </Modal>
  );
};
