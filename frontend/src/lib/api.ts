const BASE_URL = 'http://localhost:5000';

async function send(method, path, data) {
    const opts = { method, headers: {} };

    if (data) {
        opts.headers['Content-Type'] = 'application/json';
        opts.body = JSON.stringify(data);
    }

    const res = await fetch(`${BASE_URL}/${path}`, opts);
    return res.json();
}

export function get(path) {
    return send('GET', path, null);
}

export function post(path, data) {
    return send('POST', path, data);
}

export function del(path) {
    return send('DELETE', path, null);
}

export function put(path, data) {
    return send('PUT', path, data);
}
