import type { ItemSummary, PlayerItem, TierSummary } from "./types";

const BASE = "/api";

function qs(params: Record<string, string | string[]>): string {
    const sp = new URLSearchParams();
    for (const [key, val] of Object.entries(params)) {
        if (Array.isArray(val)) {
            val.forEach((v) => sp.append(key, v));
        } else {
            sp.append(key, val);
        }
    }
    return sp.toString();
}

export async function fetchItemsSummary(
    responses: string[],
    difficulties: string[],
    minDate = "2025-08-13"
): Promise<ItemSummary[]> {
    const q = qs({ responses, difficulties, min_date: minDate });
    const res = await fetch(`${BASE}/items/summary?${q}`);
    return res.json();
}

export async function fetchPlayerItems(
    player: string,
    responses: string[],
    difficulties: string[],
    minDate = "2025-08-13"
): Promise<PlayerItem[]> {
    const q = qs({ responses, difficulties, min_date: minDate });
    const res = await fetch(
        `${BASE}/items/player/${encodeURIComponent(player)}?${q}`
    );
    return res.json();
}

export async function fetchTiersSummary(
    minDate = "2025-03-05"
): Promise<TierSummary[]> {
    const res = await fetch(`${BASE}/tiers/summary?min_date=${minDate}`);
    return res.json();
}
