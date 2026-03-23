import { useState, useEffect, useCallback } from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";
import { fetchItemsSummary, fetchPlayerItems } from "../api";
import type { ItemSummary, PlayerItem } from "../types";

const RESPONSE_OPTIONS = ["Tier Set", "Bis", "Catalyst", "Mejora"];
const DIFFICULTY_OPTIONS = ["Normal", "Heroica", "Mítica"];

const COLORS: Record<string, string> = {
    Bis: "darkorange",
    "Catalyst": "purple",
    "Tier Set": "steelblue",
    Mejora: "seagreen",
};

export default function ItemsPage() {
    const [responses, setResponses] = useState(["Tier Set", "Bis", "Catalyst"]);
    const [difficulties, setDifficulties] = useState([
        "Normal",
        "Heroic",
        "Mythic",
    ]);
    const [data, setData] = useState<ItemSummary[]>([]);
    const [selectedPlayer, setSelectedPlayer] = useState<string>("");
    const [playerItems, setPlayerItems] = useState<PlayerItem[]>([]);

    const loadSummary = useCallback(async () => {
        if (responses.length === 0 || difficulties.length === 0) {
            setData([]);
            return;
        }
        const result = await fetchItemsSummary(responses, difficulties);
        setData(result);
    }, [responses, difficulties]);

    useEffect(() => {
        loadSummary();
    }, [loadSummary]);

    useEffect(() => {
        if (!selectedPlayer) {
            setPlayerItems([]);
            return;
        }
        fetchPlayerItems(selectedPlayer, responses, difficulties).then(
            setPlayerItems
        );
    }, [selectedPlayer, responses, difficulties]);

    function toggleFilter(
        arr: string[],
        setter: (v: string[]) => void,
        val: string
    ) {
        setter(
            arr.includes(val) ? arr.filter((v) => v !== val) : [...arr, val]
        );
    }

    const chartData = [...data].reverse(); // ascending for horizontal bar chart

    return (
        <div>
            <h1>Items Black Papaya</h1>

            {/* Filters */}
            <div style={{ display: "flex", gap: 32, marginBottom: 24 }}>
                <fieldset style={{ border: "1px solid #555", padding: 12, borderRadius: 6 }}>
                    <legend>Filtros</legend>
                    {RESPONSE_OPTIONS.map((opt) => (
                        <label key={opt} style={{ marginRight: 12 }}>
                            <input
                                type="checkbox"
                                checked={responses.includes(opt)}
                                onChange={() => toggleFilter(responses, setResponses, opt)}
                            />{" "}
                            {opt}
                        </label>
                    ))}
                </fieldset>

                <fieldset style={{ border: "1px solid #555", padding: 12, borderRadius: 6 }}>
                    <legend>Dificultades</legend>
                    {DIFFICULTY_OPTIONS.map((opt) => (
                        <label key={opt} style={{ marginRight: 12 }}>
                            <input
                                type="checkbox"
                                checked={difficulties.includes(opt)}
                                onChange={() =>
                                    toggleFilter(difficulties, setDifficulties, opt)
                                }
                            />{" "}
                            {opt}
                        </label>
                    ))}
                </fieldset>
            </div>

            {/* Table + Chart */}
            <div style={{ display: "flex", gap: 32, alignItems: "flex-start" }}>
                {/* Table */}
                <div style={{ flex: 1, overflowX: "auto" }}>
                    <table style={{ borderCollapse: "collapse", width: "100%" }}>
                        <thead>
                            <tr>
                                <th style={th}>Player</th>
                                {responses.map((r) => (
                                    <th key={r} style={th}>
                                        {r}
                                    </th>
                                ))}
                                <th style={th}>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((row) => (
                                <tr key={row.player}>
                                    <td style={td}>{row.player}</td>
                                    {responses.map((r) => (
                                        <td key={r} style={tdNum}>
                                            {(row[r] as number) ?? 0}
                                        </td>
                                    ))}
                                    <td style={tdNum}>{row.Total}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Chart */}
                <div style={{ flex: 1, minHeight: Math.max(400, chartData.length * 28) }}>
                    <ResponsiveContainer width="100%" height={Math.max(400, chartData.length * 28)}>
                        <BarChart data={chartData} layout="vertical" margin={{ left: 100 }}>
                            <XAxis type="number" />
                            <YAxis type="category" dataKey="player" width={120} tick={{ fontSize: 12 }} />
                            <Tooltip />
                            <Legend />
                            {responses.map((r) => (
                                <Bar key={r} dataKey={r} stackId="a" fill={COLORS[r]} />
                            ))}
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Player detail */}
            <div style={{ marginTop: 32 }}>
                <label>
                    Selecciona un player para ver los items:{" "}
                    <select
                        value={selectedPlayer}
                        onChange={(e) => setSelectedPlayer(e.target.value)}
                    >
                        <option value="">--</option>
                        {data.map((d) => (
                            <option key={d.player} value={d.player}>
                                {d.player}
                            </option>
                        ))}
                    </select>
                </label>

                {playerItems.length > 0 && (
                    <table style={{ borderCollapse: "collapse", width: "100%", marginTop: 16 }}>
                        <thead>
                            <tr>
                                {["Item", "Slot", "Response", "Date", "Votes", "Instance", "Note"].map(
                                    (h) => (
                                        <th key={h} style={th}>
                                            {h}
                                        </th>
                                    )
                                )}
                            </tr>
                        </thead>
                        <tbody>
                            {playerItems.map((item, i) => (
                                <tr key={i}>
                                    <td style={td}>{item.item}</td>
                                    <td style={td}>{item.equipLoc}</td>
                                    <td style={td}>{item.response}</td>
                                    <td style={td}>{item.date}</td>
                                    <td style={tdNum}>{item.votes}</td>
                                    <td style={td}>{item.instance}</td>
                                    <td style={td}>{item.note}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
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
