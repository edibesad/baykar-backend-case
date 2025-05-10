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
  });
  const [parts, setParts] = useState<string[]>([""]);
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
        const responseData = await response.json();
        const models = responseData.data || responseData;
        setModels(Array.isArray(models) ? models : []);
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
      const filteredParts = parts.filter((part) => part.trim() !== "");
      // Gönderilecek veriyi konsola yazdır
      console.log(
        JSON.stringify({
          serial_number: formData.serial_number,
          model: parseInt(formData.model),
          parts: filteredParts,
        })
      );
      const response = await fetch(`${API_URL}/aircraft/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${tokens?.access}`,
        },
        body: JSON.stringify({
          serial_number: formData.serial_number,
          model_id: parseInt(formData.model),
          parts: filteredParts,
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
        });
        setParts([""]);
      } else {
        console.log(response);
        const errorData = await response.json();
        console.log("errorData", errorData.details);
        toast.error(errorData.details || "Uçak eklenirken bir hata oluştu", {
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

  const handlePartChange = (index: number, value: string) => {
    const newParts = [...parts];
    newParts[index] = value;
    setParts(newParts);
  };

  const addPart = () => {
    setParts([...parts, ""]);
  };

  const removePart = (index: number) => {
    if (parts.length > 1) {
      const newParts = [...parts];
      newParts.splice(index, 1);
      setParts(newParts);
    }
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

          <div className="mb-3">
            <Form.Label>Parça Seri Numaraları</Form.Label>
            {parts.map((part, index) => (
              <div key={index} className="d-flex mb-2 gap-2">
                <Form.Control
                  type="text"
                  value={part}
                  onChange={(e) => handlePartChange(index, e.target.value)}
                  placeholder="Parça seri numarası girin"
                  required={index === 0}
                />
                <Button
                  variant="outline-danger"
                  onClick={() => removePart(index)}
                  disabled={parts.length === 1 && index === 0}
                >
                  Sil
                </Button>
              </div>
            ))}
            <Button
              variant="outline-primary"
              onClick={addPart}
              className="mt-2"
              size="sm"
            >
              Yeni Parça Ekle
            </Button>
          </div>

          <div className="d-flex justify-content-end gap-2">
            <Button variant="secondary" onClick={onHide}>
              İptal
            </Button>
            <Button variant="primary" type="submit">
              Üret
            </Button>
          </div>
        </Form>
      </Modal.Body>
    </Modal>
  );
};
