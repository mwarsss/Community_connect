import { get } from '$lib/api';
import { user } from '$lib/stores';

export async function load() {
    try {
        const me = await get('@me');
        user.set(me);
    } catch (e) {
        user.set(null);
    }
}
