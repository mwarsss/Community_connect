/// <reference types="@vitest/browser/matchers" />
import { page } from '@vitest/browser/context';
import { describe, expect, it, vi } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Page from './+page.svelte';

vi.mock('$lib/api', () => ({
	get: vi.fn(() => Promise.resolve({ opportunities: [], pagination: {} })),
	post: vi.fn(() => Promise.resolve({})),
	del: vi.fn(() => Promise.resolve({})),
	put: vi.fn(() => Promise.resolve({}))
}));

describe('/+page.svelte', () => {
	it('should render h1', async () => {
		render(Page);
		
		const heading = page.getByRole('heading', { level: 1, name: 'Opportunities' });
		await expect(heading).toBeInTheDocument();
	});
});
