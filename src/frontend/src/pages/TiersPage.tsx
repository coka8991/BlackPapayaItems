import { useState, useEffect } from "react";
import { fetchTiersSummary } from "../api";
import type { TierSummary } from "../types";

export default function TiersPage() {
    const [data, setData] = useState<TierSummary[]>([]);

    useEffect(() => {
        fetchTiersSummary().then(setData);
    }, []);

    return (
        <div>
            <h1>Tiers Black Papaya</h1>
            <p>Cantidad de tiers por player.</p>

            <table style={{ borderCollapse: "collapse", width: "100%", maxWidth: 400 }}>
                <thead>
                    <tr>
                        <th style={th}>Player</th>
                        <th style={th}>Count</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((row) => (
                        <tr key={row.player}>
                            <td style={td}>{row.player}</td>
                            <td style={tdNum}>{row.count}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

const th: React.CSSProperties = {
    borderBottom: "2px solid #ccc",
    padding: "6px 10px",
    textAlign: "left",
};
const td: React.CSSProperties = {
    borderBottom: "1px solid #eee",
    padding: "4px 10px",
};
const tdNum: React.CSSProperties = { ...td, textAlign: "right" };
