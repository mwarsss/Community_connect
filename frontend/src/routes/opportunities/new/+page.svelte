<script>
    import { post } from "$lib/api";
    import { goto } from "$app/navigation";

    let title = "";
    let description = "";
    let category = "";
    let location = "";
    let tags = [];
    let error = null;

    const availableTags = ["Social", "Environment", "Health", "Education", "Animals"];

    async function createOpportunity() {
        const res = await post("new", { title, description, category, location, tags: tags.join(",") });
        if (res.error) {
            error = res.error;
        } else {
            goto("/dashboard");
        }
    }
</script>

<div class="flex justify-center items-center h-full">
    <div class="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 class="text-2xl font-bold text-center">Create Opportunity</h1>
        {#if error}
            <p class="text-red-500 text-center">{error}</p>
        {/if}
        <form on:submit|preventDefault={createOpportunity} class="space-y-6">
            <div>
                <label for="title" class="text-sm font-medium text-gray-700">Title</label>
                <input id="title" type="text" bind:value={title} class="w-full px-3 py-2 mt-1 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
                <label for="description" class="text-sm font-medium text-gray-700">Description</label>
                <textarea id="description" bind:value={description} class="w-full px-3 py-2 mt-1 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
            </div>
            <div>
                <label for="category" class="text-sm font-medium text-gray-700">Category</label>
                <input id="category" type="text" bind:value={category} class="w-full px-3 py-2 mt-1 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
                <label for="location" class="text-sm font-medium text-gray-700">Location</label>
                <input id="location" type="text" bind:value={location} class="w-full px-3 py-2 mt-1 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
                <label for="tags" class="text-sm font-medium text-gray-700">Tags</label>
                <select id="tags" multiple bind:value={tags} class="w-full px-3 py-2 mt-1 text-gray-700 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                    {#each availableTags as tag}
                        <option value={tag}>{tag}</option>
                    {/each}
                </select>
            </div>
            <div>
                <button type="submit" class="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">Create</button>
            </div>
        </form>
    </div>
</div>