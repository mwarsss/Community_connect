<script>
    import { get, post } from "$lib/api";
    import { onMount } from "svelte";

    let opportunities = [];

    async function loadOpportunities() {
        opportunities = await get("moderator/opportunities");
    }

    async function approveOpportunity(id) {
        await post(`moderator/approve/${id}`);
        loadOpportunities();
    }

    async function rejectOpportunity(id) {
        await post(`moderator/reject/${id}`);
        loadOpportunities();
    }

    onMount(loadOpportunities);
</script>

<h1 class="text-3xl font-bold mb-4">Moderate Opportunities</h1>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {#each opportunities as opportunity}
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-bold mb-2">{opportunity.title}</h2>
            <p class="text-gray-700 mb-4">{opportunity.description}</p>
            <div class="flex justify-between items-center mb-4">
                <div>
                    <p class="text-sm text-gray-500">Category: {opportunity.category}</p>
                    <p class="text-sm text-gray-500">Location: {opportunity.location}</p>
                </div>
                <p class="text-sm text-gray-500">Posted by: {opportunity.username}</p>
            </div>
            <div class="flex justify-end space-x-2">
                <button on:click={() => approveOpportunity(opportunity.id)} class="px-4 py-2 font-bold text-white bg-green-500 rounded-md hover:bg-green-600">Approve</button>
                <button on:click={() => rejectOpportunity(opportunity.id)} class="px-4 py-2 font-bold text-white bg-red-500 rounded-md hover:bg-red-600">Reject</button>
            </div>
        </div>
    {/each}
</div>
