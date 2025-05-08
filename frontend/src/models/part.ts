import { AircraftModel } from "./aircraft_model.model";
import { Aircraft } from "./aircraft.model";
import { PartType } from "./part_type";
import { User } from "./user.model";

export interface Part {
  id: number | null;
  serial_number: string | null;
  type: PartType | null;
  aircraft_model: AircraftModel | null;
  produced_by: User | null;
  used_in_aircraft: Aircraft | null;
  created_at: Date | null;
}
