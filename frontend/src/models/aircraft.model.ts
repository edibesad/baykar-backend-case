import { AircraftModel } from "./aircraft_model.model";
import { Part } from "./part";
import { User } from "./user.model";

export interface Aircraft {
  id: number;
  serial_number: string;
  model: AircraftModel;
  assembled_by?: User;
  assembled_at?: string;
  parts: Part[];
}
