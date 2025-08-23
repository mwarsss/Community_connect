<script lang="ts">
    import { get, post } from "$lib/api";
    import socket from "$lib/socket";
    import { onMount } from "svelte";
    import { user } from "$lib/stores";

    interface Reaction {
        [key: string]: string;
    }

    interface Opportunity {
        id: number;
        title: string;
        description: string;
        category: string;
        location: string;
        username: string;
        reactions: Reaction;
        bookmarks: number[];
    }

    interface Pagination {
        total_pages?: number;
    }

    let opportunities: Opportunity[] = [];
    let pagination: Pagination = {};
    let page: number = 1;
    let selectedCategory: string = "";
    let location: string = "";
    let tags: string = "";
    let status: string = "";

    const CATEGORIES: string[] = ["Education", "Climate", "Health", "Youth", "Technology", "Mental Health"];

    async function loadOpportunities(page: number = 1, category: string = "", loc: string = "", inputTags: string = "", stat: string = "") {
        let url = `/?page=${page}`;
        if (category) url += `&category=${category}`;
        if (loc) url += `&location=${loc}`;
        if (inputTags) url += `&tags=${inputTags}`;
        if (stat) url += `&status=${stat}`;
        const res = await get(url);
        opportunities = res.opportunities;
        pagination = res.pagination;
    }

    onMount(() => loadOpportunities(page, selectedCategory, location, tags, status));

    function changePage(newPage: number) {
        if (newPage > 0 && newPage <= (pagination.total_pages || 1)) {
            page = newPage;
            loadOpportunities(page, selectedCategory, location, tags, status);
        }
    }

    function filterByCategory(category: string) {
        page = 1;
        selectedCategory = category;
        loadOpportunities(page, selectedCategory, location, tags, status);
    }

    async function react(opportunityId: number, reactionType: string) {
        await post(`opportunity/${opportunityId}/react`, { reaction_type: reactionType });
    }

    async function bookmark(opportunityId: number) {
        await post(`opportunity/${opportunityId}/bookmark`, {});
    }

    onMount(() => {
        socket.on('reaction_update', ({ opportunity_id, reactions }: { opportunity_id: number, reactions: Reaction }) => {
            opportunities = opportunities.map(opp => {
                if (opp.id === opportunity_id) {
                    return { ...opp, reactions };
                }
                return opp;
            });
        });

        socket.on('bookmark_update', ({ opportunity_id, bookmarks }: { opportunity_id: number, bookmarks: number[] }) => {
            opportunities = opportunities.map(opp => {
                if (opp.id === opportunity_id) {
                    return { ...opp, bookmarks };
                }
                return opp;
            });
        });
    });
</script>

<h1 class="text-3xl font-bold mb-4">Opportunities</h1>

<div class="flex space-x-2 mb-4">
    <button on:click={() => filterByCategory("")} class="px-4 py-2 rounded-md {selectedCategory === '' ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}">All</button>
    {#each CATEGORIES as category}
        <button on:click={() => filterByCategory(category)} class="px-4 py-2 rounded-md {selectedCategory === category ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}">{category}</button>
    {/each}
</div>

<div class="flex space-x-2 mb-4">
    <input type="text" bind:value={location} placeholder="Location" class="px-4 py-2 rounded-md bg-gray-200" />
    <input type="text" bind:value={tags} placeholder="Tags (comma-separated)" class="px-4 py-2 rounded-md bg-gray-200" />
    <select bind:value={status} class="px-4 py-2 rounded-md bg-gray-200">
        <option value="">All Statuses</option>
        <option value="approved">Approved</option>
        <option value="pending">Pending</option>
    </select>
    <button on:click={() => loadOpportunities(1, selectedCategory, location, tags, status)} class="px-4 py-2 rounded-md bg-blue-500 text-white">Filter</button>
</div>

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
                <p class="text-sm text-gray-500">Posted by: {opportunity.username}</p>
            </div>
            <div class="flex justify-between items-center mt-4">
                <div>
                    <button on:click={() => react(opportunity.id, 'like')} class="px-2 py-1 rounded-md bg-gray-200 hover:bg-gray-300">👍 {Object.values(opportunity.reactions).filter(r => r === 'like').length}</button>
                    <button on:click={() => react(opportunity.id, 'love')} class="px-2 py-1 rounded-md bg-gray-200 hover:bg-gray-300">❤️ {Object.values(opportunity.reactions).filter(r => r === 'love').length}</button>
                    <button on:click={() => react(opportunity.id, 'wow')} class="px-2 py-1 rounded-md bg-gray-200 hover:bg-gray-300">😮 {Object.values(opportunity.reactions).filter(r => r === 'wow').length}</button>
                </div>
                {#if $user}
                <button on:click={() => bookmark(opportunity.id)} class="px-2 py-1 rounded-md bg-gray-200 hover:bg-gray-300">{opportunity.bookmarks.includes($user.id) ? '❤️' : '🤍'}</button>
                {/if}
            </div>
        </div>
    {/each}
</div>

<div class="flex justify-center mt-8">
    <nav class="flex space-x-2">
        <button on:click={() => changePage(page - 1)} disabled={page === 1} class="px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300 disabled:opacity-50">Previous</button>
        {#each Array(pagination.total_pages || 0) as _, i}
            <button on:click={() => changePage(i + 1)} class="px-4 py-2 rounded-md {page === i + 1 ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}">{i + 1}</button>
        {/each}
        <button on:click={() => changePage(page + 1)} disabled={page === (pagination.total_pages || 1)} class="px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300 disabled:opacity-50">Next</button>
    </nav>
</div>
