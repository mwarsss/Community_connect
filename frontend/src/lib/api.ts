const BASE_URL = 'http://localhost:5000';

type Options = {
    method: string;
    headers: Record<string, string>;
    body?: string;
}

async function send<T>(method: string, path: string, data?: T) {
    const opts: Options = { method, headers: {}, credentials: 'include' };

    if (data) {
        opts.headers['Content-Type'] = 'application/json';
        opts.body = JSON.stringify(data);
    }

    const res = await fetch(`${BASE_URL}/${path}`, opts as RequestInit);
    return res.json();
}

export function get(path: string) {
    return send('GET', path);
}

export function post<T>(path: string, data: T) {
    return send('POST', path, data);
}

export function del(path: string) {
    return send('DELETE', path);
}

export function put<T>(path: string, data: T) {
    return send('PUT', path, data);
}
