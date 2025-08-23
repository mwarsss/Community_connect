<script lang="ts">
    import { get, post } from "$lib/api";
    import { onMount } from "svelte";

    interface ReportedUser {
        username: string;
    }

    interface ReportedOpportunity {
        title: string;
    }

    interface Report {
        id: number;
        reason: string;
        reporter_username: string;
        is_reviewed: boolean;
        reported_user?: ReportedUser;
        reported_opportunity?: ReportedOpportunity;
    }

    let reports: Report[] = [];

    async function loadReports() {
        const res = await get("moderator/reports");
        reports = res.reports;
    }

    async function markReviewed(id: number) {
        await post(`moderator/mark_reviewed/${id}`, {});
        loadReports();
    }

    onMount(loadReports);
</script>

<h1 class="text-3xl font-bold mb-4">View Reports</h1>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {#each reports as report}
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-bold mb-2">Report ID: {report.id}</h2>
            <p class="text-gray-700 mb-2">Reason: {report.reason}</p>
            <p class="text-gray-700 mb-2">Reporter: {report.reporter_username}</p>
            <p class="text-gray-700 mb-4">Reviewed: {report.is_reviewed ? "Yes" : "No"}</p>
            {#if report.reported_user}
                <p class="text-gray-700 mb-2">Reported User: {report.reported_user.username}</p>
            {/if}
            {#if report.reported_opportunity}
                <p class="text-gray-700 mb-2">Reported Opportunity: {report.reported_opportunity.title}</p>
            {/if}
            <div class="flex justify-end">
                <button on:click={() => markReviewed(report.id)} class="px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600" disabled={report.is_reviewed}>
                    {report.is_reviewed ? "Reviewed" : "Mark as Reviewed"}
                </button>
            </div>
        </div>
    {/each}
</div>