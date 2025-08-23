<script lang="ts">
	import { get } from '$lib/api';
	import { onMount } from 'svelte';
	import {
		Mail,
		MapPin,
		Calendar,
		CheckCircle,
		XCircle,
		ArrowRight,
		Info
	} from 'lucide-svelte';

	interface Opportunity {
		id: number;
		title: string;
		description: string;
		category: string;
		location: string;
		is_approved: boolean;
	}

	let opportunities: Opportunity[] = [];

	onMount(async () => {
		const res = await get('dashboard');
		opportunities = res.opportunities;
	});
</script>

<div class="container mx-auto px-4 py-8">
	<h1 class="text-4xl font-extrabold text-gray-800 mb-8">Your Opportunities</h1>

	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
		{#each opportunities as opportunity}
			<div
				class="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-shadow duration-300 ease-in-out overflow-hidden"
			>
				<div class="p-6">
					<div class="flex items-center mb-4">
						<div
							class="p-2 rounded-full mr-4"
							class:bg-green-100={opportunity.is_approved}
							class:text-green-600={opportunity.is_approved}
							class:bg-yellow-100={!opportunity.is_approved}
							class:text-yellow-600={!opportunity.is_approved}
						>
							{#if opportunity.is_approved}
								<CheckCircle size={24} />
							{:else}
								<Info size={24} />
							{/if}
						</div>
						<h2 class="text-2xl font-bold text-gray-800">{opportunity.title}</h2>
					</div>

					<p class="text-gray-600 mb-6 h-24 overflow-hidden">
						{opportunity.description}
					</p>

					<div class="flex items-center text-sm text-gray-500 mb-2">
						<MapPin size={16} class="mr-2" />
						<span>{opportunity.location}</span>
					</div>
					<div class="flex items-center text-sm text-gray-500 mb-4">
						<Calendar size={16} class="mr-2" />
						<span>{opportunity.category}</span>
					</div>

					<div class="flex justify-between items-center">
						<div
							class="text-sm font-semibold px-4 py-2 rounded-full"
							class:bg-green-100={opportunity.is_approved}
							class:text-green-700={opportunity.is_approved}
							class:bg-yellow-100={!opportunity.is_approved}
							class:text-yellow-700={!opportunity.is_approved}
						>
							{opportunity.is_approved ? 'Approved' : 'Pending'}
						</div>
						<button
							class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-full transition-colors duration-300 flex items-center"
						>
							<span>View Details</span>
							<ArrowRight size={16} class="ml-2" />
						</button>
					</div>
				</div>
			</div>
		{/each}
	</div>
</div>
