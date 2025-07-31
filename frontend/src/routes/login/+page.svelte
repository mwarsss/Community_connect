<script>
    import { post } from "$lib/api";
    import { goto } from "$app/navigation";

    let username = "";
    let password = "";
    let error = null;

    async function login() {
        const res = await post("login", { username, password });
        if (res.error) {
            error = res.error;
        } else {
            goto("/");
        }
    }
</script>

<div class="flex justify-center items-center h-full">
    <div class="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 class="text-2xl font-bold text-center">Login</h1>
        {#if error}
            <p class="text-red-500 text-center">{error}</p>
        {/if}
        <form on:submit|preventDefault={login} class="space-y-6">
            <div>
                <label for="username" class="text-sm font-medium text-gray-700">Username</label>
                <input id="username" type="text" bind:value={username} class="w-full px-3 py-2 mt-1 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
                <label for="password" class="text-sm font-medium text-gray-700">Password</label>
                <input id="password" type="password" bind:value={password} class="w-full px-3 py-2 mt-1 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
                <button type="submit" class="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">Login</button>
            </div>
        </form>
    </div>
</div>