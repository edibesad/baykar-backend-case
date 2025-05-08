import { AircraftModel } from "./aircraft_model.model";
import { Part } from "./part";
import { User } from "./user.model";

export interface Aircraft {
  id: number;
  serial_number: string;
  model: AircraftModel;
  assambled_by: User;
  assambled_at: Date;
  wing: Part | null;
  body: Part | null;
  tail: Part | null;
  avionic: Part | null;
  engine: Part | null;
}
