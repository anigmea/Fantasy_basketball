
import { useEffect, useState } from "react";
import { healthCheck, getRankings } from "../services/api";

function Schedule() {
  const [status, setStatus] = useState("");
  const [rankings, setRankings] = useState<any[]>([]);

  useEffect(() => {
    healthCheck()
      .then(res => setStatus(res.data.message))
      .catch(() => setStatus("Backend unreachable"));

    getRankings()
      .then(res => setRankings(res.data.data))
      .catch(console.error);
  }, []);

  return (
    <div>
      <h1>Fantasy Analyzer</h1>
      <p>{status}</p>

      <h2>Schedule</h2>
      <pre>{JSON.stringify(rankings, null, 2)}</pre>
    </div>
  );
}

export default Schedule;
