<script>
    import { get } from "$lib/api";
    import { onMount } from "svelte";

    let opportunities = [];

    onMount(async () => {
        opportunities = await get("dashboard");
    });
</script>

<h1 class="text-3xl font-bold mb-4">Your Opportunities</h1>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {#each opportunities as opportunity}
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-bold mb-2">{opportunity.title}</h2>
            <p class="text-gray-700 mb-4">{opportunity.description}</p>
            <div class="flex justify-between items-center">
                <div>
                    <p class="text-sm text-gray-500">Category: {opportunity.category}</p>
                    <p class="text-sm text-gray-500">Location: {opportunity.location}</p>
                </div>
                <p class="text-sm font-bold {opportunity.is_approved ? 'text-green-500' : 'text-yellow-500'}">
                    {opportunity.is_approved ? "Approved" : "Pending Approval"}
                </p>
            </div>
        </div>
    {/each}
</div>