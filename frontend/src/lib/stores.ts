import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface User {
    id: number;
    role: string;
    username: string;
    email: string;
    account_active: boolean;
    is_banned: boolean;
}

const storedUser = browser ? JSON.parse(localStorage.getItem('user') || 'null') : null;

export const user = writable<User | null>(storedUser);

user.subscribe((value) => {
    if (browser) {
        localStorage.setItem('user', JSON.stringify(value));
    }
});