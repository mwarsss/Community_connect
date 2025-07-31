<script>
    import { get } from "$lib/api";
    import { onMount } from "svelte";

    let opportunities = [];
    let pagination = {};
    let page = 1;
    let selectedCategory = "";

    const CATEGORIES = ["Education", "Climate", "Health", "Youth", "Technology", "Mental Health"];

    async function loadOpportunities(page = 1, category = "") {
        let url = `/?page=${page}`;
        if (category) {
            url += `&category=${category}`;
        }
        const res = await get(url);
        opportunities = res.opportunities;
        pagination = res.pagination;
    }

    onMount(() => loadOpportunities(page, selectedCategory));

    function changePage(newPage) {
        if (newPage > 0 && newPage <= pagination.total_pages) {
            page = newPage;
            loadOpportunities(page, selectedCategory);
        }
    }

    function filterByCategory(category) {
        page = 1;
        selectedCategory = category;
        loadOpportunities(page, selectedCategory);
    }
</script>

<h1 class="text-3xl font-bold mb-4">Opportunities</h1>

<div class="flex space-x-2 mb-4">
    <button on:click={() => filterByCategory("")} class="px-4 py-2 rounded-md {selectedCategory === '' ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}">All</button>
    {#each CATEGORIES as category}
        <button on:click={() => filterByCategory(category)} class="px-4 py-2 rounded-md {selectedCategory === category ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}">{category}</button>
    {/each}
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
        </div>
    {/each}
</div>

<div class="flex justify-center mt-8">
    <nav class="flex space-x-2">
        <button on:click={() => changePage(page - 1)} disabled={page === 1} class="px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300 disabled:opacity-50">Previous</button>
        {#each Array(pagination.total_pages) as _, i}
            <button on:click={() => changePage(i + 1)} class="px-4 py-2 rounded-md {page === i + 1 ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}">{i + 1}</button>
        {/each}
        <button on:click={() => changePage(page + 1)} disabled={page === pagination.total_pages} class="px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300 disabled:opacity-50">Next</button>
    </nav>
</div>
