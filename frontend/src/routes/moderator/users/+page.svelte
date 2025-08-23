<script lang="ts">
    import { get, post } from "$lib/api";
    import { onMount } from "svelte";

    interface User {
        id: number;
        username: string;
        email: string;
        role: string;
        account_active: boolean;
        is_banned: boolean;
    }

    let users: User[] = [];

    async function loadUsers() {
        const res = await get("admin/users");
        users = res.users;
    }

    async function suspendUser(id: number) {
        await post(`admin/suspend/${id}`, {});
        loadUsers();
    }

    async function activateUser(id: number) {
        await post(`admin/activate/${id}`, {});
        loadUsers();
    }

    async function banUser(id: number) {
        await post(`moderator/ban_user/${id}`, {});
        loadUsers();
    }

    onMount(loadUsers);
</script>

<h1 class="text-3xl font-bold mb-4">Manage Users</h1>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {#each users as user}
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-bold mb-2">{user.username}</h2>
            <p class="text-gray-700 mb-2">Email: {user.email}</p>
            <p class="text-gray-700 mb-2">Role: {user.role}</p>
            <p class="text-gray-700 mb-4">Status: {user.account_active ? "Active" : "Suspended"}</p>
            <p class="text-gray-700 mb-4">Banned: {user.is_banned ? "Yes" : "No"}</p>
            <div class="flex justify-end space-x-2">
                <button on:click={() => suspendUser(user.id)} class="px-4 py-2 font-bold text-white bg-yellow-500 rounded-md hover:bg-yellow-600">Suspend</button>
                <button on:click={() => activateUser(user.id)} class="px-4 py-2 font-bold text-white bg-green-500 rounded-md hover:bg-green-600">Activate</button>
                <button on:click={() => banUser(user.id)} class="px-4 py-2 font-bold text-white bg-red-500 rounded-md hover:bg-red-600">Ban</button>
            </div>
        </div>
    {/each}
</div>