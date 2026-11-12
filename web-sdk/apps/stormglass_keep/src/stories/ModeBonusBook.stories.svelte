<script lang="ts" module>
	import { defineMeta } from '@storybook/addon-svelte-csf';

	const { Story } = defineMeta({
		title: 'MODE_BONUS/book',
	});
</script>

<script lang="ts">
	import {
		StoryGameTemplate,
		StoryLocale,
		type TemplateArgs,
		templateArgs,
	} from 'components-storybook';
	import { randomInteger } from 'utils-shared/random';

	import Game from '../components/Game.svelte';
	import { setContext } from '../game/context';
	import { playBet } from '../game/utils';
	import type { Bet } from '../game/typesBookEvent';
	import allBooks from './data/bonus_books';

	// Books are real outcomes exported from the math model (see math/stormglass_keep/tools).
	const playRandom = async (criteria?: string) => {
		const books = allBooks.filter((book) => !criteria || book.criteria === criteria);
		const data = books[randomInteger({ min: 0, max: books.length - 1 })];
		console.log('Running book', data.id, data.criteria, 'payout', data.payoutMultiplier / 100);
		await playBet({ ...data, state: data.events } as unknown as Bet);
	};

	setContext();
</script>

{#snippet template(args: TemplateArgs<any>)}
	<StoryGameTemplate
		skipLoadingScreen={args.skipLoadingScreen}
		action={async () => {
			await args.action?.(args.data);
		}}
	>
		<StoryLocale lang="en">
			<Game />
		</StoryLocale>
	</StoryGameTemplate>
{/snippet}

<Story
	name="random"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom(),
	})}
	{template}
/>

<Story
	name="watch"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('watch'),
	})}
	{template}
/>

<Story
	name="wincap"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('wincap'),
	})}
	{template}
/>
