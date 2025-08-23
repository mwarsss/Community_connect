import { writable } from 'svelte/store';

export interface User {
    id: number;
    role: string;
}

export const user = writable<User | null>(null);
