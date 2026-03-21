export interface ItemSummary {
    player: string;
    [key: string]: string | number;
    Total: number;
}

export interface PlayerItem {
    item: string;
    equipLoc: string;
    response: string;
    date: string;
    votes: string;
    instance: string;
    note: string;
}

export interface TierSummary {
    player: string;
    count: number;
}
