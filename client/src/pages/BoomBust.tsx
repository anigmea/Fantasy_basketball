// frontend/src/components/BoomBust.tsx
import { useState, useEffect } from "react";
import { getPlayers, getBoomBust } from "../services/api";

export default function BoomBust() {
  const [players, setPlayers] = useState<string[]>([]);
  const [team, setTeam] = useState<string[]>([]);
  const [results, setResults] = useState<any[]>([]);

  // Load all players from backend on mount
  useEffect(() => {
    getPlayers().then((data) => setPlayers(data.map((p: any) => p.name)));
  }, []);

  const handleAnalyze = async () => {
    const analysis = await getBoomBust(team);
    setResults(analysis);
  };

  return (
    <div>
      <h1>Boom/Bust Analyzer</h1>

      <div>
        <h3>Select Your Team</h3>
        {players.map((player) => (
          <label key={player}>
            <input
              type="checkbox"
              value={player}
              onChange={(e) => {
                const value = e.target.value;
                setTeam((prev) =>
                  prev.includes(value)
                    ? prev.filter((p) => p !== value)
                    : [...prev, value]
                );
              }}
            />
            {player}
          </label>
        ))}
      </div>

      <button onClick={handleAnalyze}>Analyze Team</button>

      <div>
        <h3>Results</h3>
        <pre>{JSON.stringify(results, null, 2)}</pre>
      </div>
    </div>
  );
}
