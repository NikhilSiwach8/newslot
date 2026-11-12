<script lang="ts" module>
	import { defineMeta } from '@storybook/addon-svelte-csf';

	const { Story } = defineMeta({
		title: 'MODE_BASE/book',
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
	import allBooks from './data/base_books';

	// Books are real outcomes exported from the math model (math/infernal_kingdom/tools/export_frontend.py).
	// filter: '' (any), 'criteria:<name>' or 'tag:<feature>'.
	const playRandom = async (filter: string) => {
		const [kind, value] = filter.split(':');
		const books = (allBooks as any[]).filter((book) =>
			!filter ? true : kind === 'criteria' ? book.criteria === value : book.tags?.includes(value),
		);
		if (!books.length) {
			console.warn('No exported book for', filter);
			return;
		}
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
		action: async () => await playRandom(''),
	})}
	{template}
/>

<Story
	name="basegame"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('criteria:basegame'),
	})}
	{template}
/>

<Story
	name="no win"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('criteria:0'),
	})}
	{template}
/>

<Story
	name="hellfire"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('criteria:hellfire'),
	})}
	{template}
/>

<Story
	name="covenant"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('criteria:covenant'),
	})}
	{template}
/>

<Story
	name="abyssal"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('criteria:abyssal'),
	})}
	{template}
/>

<Story
	name="furnace"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('criteria:furnace'),
	})}
	{template}
/>

<Story
	name="takeover"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('tag:takeover'),
	})}
	{template}
/>

<Story
	name="apocalypse"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('tag:apocalypse'),
	})}
	{template}
/>

<Story
	name="wincap"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('tag:wincap'),
	})}
	{template}
/>

<Story
	name="pattern"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('tag:pattern'),
	})}
	{template}
/>

<Story
	name="wildBomb"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('tag:wildBomb'),
	})}
	{template}
/>

<Story
	name="goldenWildBomb"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('tag:goldenWildBomb'),
	})}
	{template}
/>

<Story
	name="split"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('tag:split'),
	})}
	{template}
/>

<Story
	name="overlord"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('tag:overlord'),
	})}
	{template}
/>

<Story
	name="retrigger"
	args={templateArgs({
		skipLoadingScreen: true,
		data: {},
		action: async () => await playRandom('tag:retrigger'),
	})}
	{template}
/>
