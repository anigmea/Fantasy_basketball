import { Tabs } from "@chakra-ui/react";
import { useNavigate, useLocation } from "react-router-dom";

export const NavBar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Determine active tab based on current route
  const getActiveTab = () => {
    const path = location.pathname;
    if (path === "/" || path === "/players") return "players";
    if (path === "/boombust") return "boombust";
    if (path === "/trades") return "trades";
    if (path === "/schedule") return "schedule";
    if (path === "/replacements") return "replacements";
    return "players";
  };

  const handleTabChange = (details: { value: string }) => {
    const routes: Record<string, string> = {
      players: "/players",
      boombust: "/boombust",
      trades: "/trades",
      schedule: "/schedule",
      replacements: "/replacements",
    };
    navigate(routes[details.value]);
  };

  return (
    <Tabs.Root
      value={getActiveTab()}
      onValueChange={handleTabChange}
      variant="plain"
      css={{
        "--tabs-indicator-bg": "colors.gray.subtle",
        "--tabs-indicator-shadow": "shadows.xs",
        "--tabs-trigger-radius": "radii.full",
      }}
    >
      <Tabs.List>
        <Tabs.Trigger value="players">Players</Tabs.Trigger>
        <Tabs.Trigger value="boombust">Boom/Bust</Tabs.Trigger>
        <Tabs.Trigger value="trades">Trades</Tabs.Trigger>
        <Tabs.Trigger value="schedule">Schedule</Tabs.Trigger>
        <Tabs.Trigger value="replacements">Replacements</Tabs.Trigger>
        <Tabs.Indicator />
      </Tabs.List>
    </Tabs.Root>
  );
};