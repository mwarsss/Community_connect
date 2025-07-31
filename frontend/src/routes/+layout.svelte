<script>
    import { user } from "$lib/stores";
    import { post } from "$lib/api";
    import { goto } from "$app/navigation";
    import "../app.css";

    async function logout() {
        await post("logout");
        user.set(null);
        goto("/login");
    }
</script>

<header class="bg-gray-800 text-white p-4">
    <nav class="container mx-auto flex justify-between">
        <div>
            <a href="/" class="hover:text-gray-300">Community Connect</a>
        </div>
        <div>
            {#if $user}
                <a href="/dashboard" class="px-4 hover:text-gray-300">Dashboard</a>
                {#if $user.role === 'admin' || $user.role === 'moderator'}
                    <a href="/moderator" class="px-4 hover:text-gray-300">Moderator</a>
                {/if}
                <button on:click={logout} class="px-4 hover:text-gray-300">Logout</button>
            {:else}
                <a href="/login" class="px-4 hover:text-gray-300">Login</a>
                <a href="/register" class="px-4 hover:text-gray-300">Register</a>
            {/if}
        </div>
    </nav>
</header>

<main class="container mx-auto p-4">
    <slot />
</main>