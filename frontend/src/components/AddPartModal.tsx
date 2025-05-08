"use client";

import { useState, useEffect, ChangeEvent, FormEvent } from "react";
import { Modal, Button, Form } from "react-bootstrap";
import { API_URL } from "@/config/env";
import { useUserStore } from "@/store/user-store";
import { toast } from "react-toastify";

interface PartType {
  id: number;
  name: string;
}

interface AircraftModel {
  id: number;
  name: string;
}

interface NewPartForm {
  serial_number: string;
  type: string;
  aircraft_model: string;
}

interface AddPartModalProps {
  show: boolean;
  onHide: () => void;
  onPartAdded: () => void;
}

export const AddPartModal = ({
  show,
  onHide,
  onPartAdded,
}: AddPartModalProps) => {
  const [newPart, setNewPart] = useState<NewPartForm>({
    serial_number: "",
    type: "",
    aircraft_model: "",
  });
  const [types, setTypes] = useState<PartType[]>([]);
  const [aircraftModels, setAircraftModels] = useState<AircraftModel[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { tokens, user } = useUserStore();

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [typesRes, modelsRes] = await Promise.all([
          fetch(`${API_URL}/part-types`, {
            headers: { Authorization: `Bearer ${tokens?.access}` },
          }),
          fetch(`${API_URL}/aircraft-models`, {
            headers: { Authorization: `Bearer ${tokens?.access}` },
          }),
        ]);

        const typesData = await typesRes.json();
        const modelsData = await modelsRes.json();

        setTypes(typesData);
        setAircraftModels(modelsData);

        newPart.type = typesData.find(
          (type: PartType) => type.name === user?.team_responsibility
        )?.id;
      } catch (error) {
        console.error("Error fetching options:", error);
        toast.error("Seçenekler yüklenirken bir hata oluştu", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
        });
      }
    };

    if (show) {
      fetchOptions();
    }
  }, [newPart, show, tokens?.access, user?.team_responsibility]);

  const handleInputChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setNewPart({
      ...newPart,
      [name]: value,
    });
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);

    // Convert string IDs to numbers for the API
    const requestData = {
      serial_number: newPart.serial_number,
      type_id: newPart.type ? parseInt(newPart.type) : null,
      aircraft_model_id: newPart.aircraft_model
        ? parseInt(newPart.aircraft_model)
        : null,
    };

    console.log("Sending request payload:", requestData);

    try {
      const response = await fetch(`${API_URL}/parts/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${tokens?.access}`,
        },
        body: JSON.stringify(requestData),
      });

      if (response.ok) {
        // Reset form and close modal
        setNewPart({
          serial_number: "",
          type: "",
          aircraft_model: "",
        });
        toast.success("Parça başarıyla eklendi", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
        });
        onPartAdded();
        onHide();
      } else {
        const errorData = await response.json();
        console.error("API Error Response:", errorData);

        // Handle the specific case where the error is in the "detail" field
        let errorMessage = "Parça eklenirken bir hata oluştu";

        if (errorData && errorData.detail) {
          // This is the primary expected error format from the backend
          errorMessage = errorData.detail;
        } else if (typeof errorData === "string") {
          errorMessage = errorData;
        } else if (errorData.details) {
          errorMessage = errorData.details;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (errorData.error) {
          errorMessage =
            typeof errorData.error === "string"
              ? errorData.error
              : JSON.stringify(errorData.error);
        } else {
          // Check for field-specific errors
          const fieldErrors = Object.keys(errorData)
            .filter(
              (key) =>
                typeof errorData[key] === "string" ||
                Array.isArray(errorData[key])
            )
            .map((key) => {
              const value = errorData[key];
              if (Array.isArray(value)) {
                return `${key}: ${value.join(", ")}`;
              }
              return `${key}: ${value}`;
            });

          if (fieldErrors.length > 0) {
            errorMessage = fieldErrors.join("\n");
          } else {
            // If we can't extract a specific error message, show the raw error
            errorMessage = `Hata: ${JSON.stringify(errorData)}`;
          }
        }

        toast.error(errorMessage, {
          position: "top-right",
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: true,
        });
      }
    } catch (error) {
      console.error("Error adding part:", error);
      let errorMessage = "Parça eklenirken bir hata oluştu";

      if (error instanceof Error) {
        errorMessage += `: ${error.message}`;
      }

      toast.error(errorMessage, {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>Yeni Parça Ekle</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Seri Numarası</Form.Label>
            <Form.Control
              type="text"
              name="serial_number"
              value={newPart.serial_number}
              onChange={handleInputChange}
              required
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Parça Tipi</Form.Label>
            <Form.Select
              name="type"
              value={newPart.type}
              onChange={handleInputChange}
              disabled={true}
              required
            >
              <option value="">Seçiniz</option>
              {types.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Uçak Modeli</Form.Label>
            <Form.Select
              name="aircraft_model"
              value={newPart.aircraft_model}
              onChange={handleInputChange}
              required
            >
              <option value="">Seçiniz</option>
              {aircraftModels.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.name}
                </option>
              ))}
            </Form.Select>
          </Form.Group>

          <div className="d-flex justify-content-end gap-2">
            <Button variant="secondary" onClick={onHide}>
              İptal
            </Button>
            <Button variant="primary" type="submit" disabled={isLoading}>
              {isLoading ? "Ekleniyor..." : "Ekle"}
            </Button>
          </div>
        </Form>
      </Modal.Body>
    </Modal>
  );
};
