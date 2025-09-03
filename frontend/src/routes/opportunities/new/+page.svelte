<script lang="ts">
    import { post, get } from "$lib/api";
    import { goto } from "$app/navigation";
    import { Briefcase, MapPin, Tag, FileText, LayoutGrid } from "lucide-svelte";
    import { onMount } from "svelte";

    let title: string = "";
    let description: string = "";
    let category: string = "";
    let location: string = "";
    let selectedTags: string[] = [];
    let error: string | null = null;
    let loading: boolean = false;
    let availableTags: {id: number, name: string}[] = [];
    let availableCategories: string[] = [];
    let isLoading: boolean = true;

    onMount(async () => {
        const tagsRes = await get("tags");
        if (tagsRes.error) {
            error = tagsRes.error;
        } else {
            availableTags = tagsRes;
        }

        const categoriesRes = await get("categories");
        if (categoriesRes.error) {
            error = categoriesRes.error;
        } else {
            availableCategories = categoriesRes;
        }
        isLoading = false;
    });

    async function createOpportunity() {
        loading = true;
        const res = await post("new", { title, description, category, location, tags: selectedTags.join(",") });
        if (res.error) {
            error = res.error;
        } else {
            goto("/dashboard");
        }
        loading = false;
    }

    function toggleTag(tag: string) {
        if (selectedTags.includes(tag)) {
            selectedTags = selectedTags.filter(t => t !== tag);
        } else {
            selectedTags = [...selectedTags, tag];
        }
    }
</script>

<div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-2xl">
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create a New Opportunity
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
            Fill out the form below to post a new volunteer opportunity.
        </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-2xl">
        <div class="bg-white py-8 px-4 shadow-lg sm:rounded-lg sm:px-10">
            {#if error}
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6" role="alert">
                    <strong class="font-bold">Error:</strong>
                    <span class="block sm:inline">{error}</span>
                </div>
            {/if}

            <form on:submit|preventDefault={createOpportunity} class="space-y-8">
                <div class="relative">
                    <label for="title" class="block text-sm font-medium text-gray-700">Title</label>
                    <div class="mt-1 relative rounded-md shadow-sm">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Briefcase class="h-5 w-5 text-gray-400" />
                        </div>
                        <input id="title" type="text" bind:value={title} placeholder="e.g., Community Garden Cleanup" class="form-input block w-full pl-10 sm:text-sm sm:leading-5 rounded-md border-gray-300 focus:ring-indigo-500 focus:border-indigo-500" />
                    </div>
                </div>

                <div>
                    <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
                    <div class="mt-1 relative rounded-md shadow-sm">
                         <div class="absolute top-3 left-0 pl-3 flex items-center pointer-events-none">
                            <FileText class="h-5 w-5 text-gray-400" />
                        </div>
                        <textarea id="description" bind:value={description} rows="4" placeholder="Describe the opportunity in detail." class="form-textarea block w-full pl-10 sm:text-sm sm:leading-5 rounded-md border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"></textarea>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label for="category" class="block text-sm font-medium text-gray-700">Category</label>
                        <div class="mt-1 relative rounded-md shadow-sm">
                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <LayoutGrid class="h-5 w-5 text-gray-400" />
                            </div>
                            <select id="category" bind:value={category} class="form-select block w-full pl-10 sm:text-sm sm:leading-5 rounded-md border-gray-300 focus:ring-indigo-500 focus:border-indigo-500">
                                <option value="" disabled>Select a category</option>
                                {#each availableCategories as cat}
                                    <option value={cat}>{cat}</option>
                                {/each}
                            </select>
                        </div>
                    </div>
                    <div>
                        <label for="location" class="block text-sm font-medium text-gray-700">Location</label>
                        <div class="mt-1 relative rounded-md shadow-sm">
                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <MapPin class="h-5 w-5 text-gray-400" />
                            </div>
                            <input id="location" type="text" bind:value={location} placeholder="e.g., City Park" class="form-input block w-full pl-10 sm:text-sm sm:leading-5 rounded-md border-gray-300 focus:ring-indigo-500 focus:border-indigo-500" />
                        </div>
                    </div>
                </div>

                <div>
                    <span id="tags-label" class="block text-sm font-medium text-gray-700">Tags</span>
                    <div class="mt-2 flex flex-wrap gap-2" role="group" aria-labelledby="tags-label">
                        {#if isLoading}
                            <p>Loading tags...</p>
                        {:else}
                            {#each availableTags as tag}
                                <button type="button" on:click={() => toggleTag(tag.name)} class="px-4 py-2 rounded-full text-sm font-medium transition-colors {selectedTags.includes(tag.name) ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}">
                                    {tag.name}
                                </button>
                            {/each}
                        {/if}
                    </div>
                </div>

                <div>
                    <button type="submit" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" disabled={loading}>
                        {#if loading}
                            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        {/if}
                        {loading ? 'Creating...' : 'Create Opportunity'}
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>