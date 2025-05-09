import AssambleTeamPage from "./AssambleTeamPage";
import TeamPage from "./TeamPage";

export default function PageByTeam({
  team,
}: {
  team: "kuyruk" | "kanat" | "gövde" | "aviyonik" | "montaj" | null;
}) {
  console.log("team", team);
  if (
    team === "kuyruk" ||
    team === "kanat" ||
    team === "gövde" ||
    team === "aviyonik"
  ) {
    return <TeamPage />;
  } else if (team === "montaj") {
    return <AssambleTeamPage />;
  }
  return null;
}
