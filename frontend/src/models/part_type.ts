import { Team } from "./team.enum";

export interface PartType {
  id: number;
  name: string;
  allowed_team: Team;
}
