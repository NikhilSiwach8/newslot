<script lang="ts" module>
	import type { PactName, SoulName } from '../game/constants';

	export type EmitterEventFeatureOverlay =
		| { type: 'featureBanner'; title: string; subtitle: string; color: number; big: boolean }
		| { type: 'pactShow'; pact: PactName }
		| { type: 'apocalypseShow'; souls: SoulName[]; multiplier: number }
		| { type: 'maxWinShow'; multiplier: number }
		| { type: 'waysWinShow'; wins: { symbol: string; kind: number; ways: number; win: number; mult: number }[] }
		| { type: 'waysWinHide' };
</script>

<script lang="ts">
	import { Circle, Container, Rectangle, Text } from 'pixi-svelte';
	import { stateBet } from 'state-shared';
	import { waitForTimeout } from 'utils-shared/wait';

	import BoardContainer from './BoardContainer.svelte';
	import { getContext } from '../game/context';
	import { SYMBOL_SIZE, PALETTE, PACTS, SOUL_COLORS } from '../game/constants';

	// Banners for features, the Demon's Bargain contracts, the Soul Apocalypse and the max
	// win. Presentation only: it waits, it never changes what the book says.
	const context = getContext();
	const board = $derived(context.stateGameDerived.boardLayout());
	const wait = (ms: number) => waitForTimeout(stateBet.isTurbo ? ms * 0.35 : ms);
	const font = (size: number, fill: number, weight = '800') => ({
		fontFamily: 'proxima-nova',
		fontSize: SYMBOL_SIZE * size,
		fontWeight: weight as '800',
		fill,
		align: 'center' as const,
	});

	let banner = $state<{ title: string; subtitle: string; color: number; big: boolean } | undefined>();
	let pact = $state<PactName | undefined>();
	let apocalypse = $state<{ souls: SoulName[]; multiplier: number; step: number } | undefined>();
	let maxWin = $state<number | undefined>();
	let waysText = $state('');
	let pactVisible = $state(false);

	context.eventEmitter.subscribeOnMount({
		featureBanner: async (e) => {
			banner = e;
			await wait(e.big ? 1400 : 650);
			banner = undefined;
		},
		pactShow: async (e) => {
			pact = undefined;
			pactVisible = true;
			await wait(900); // both contracts on show
			pact = e.pact; // the contract chosen before the bet is sealed
			await wait(1300);
			pactVisible = false;
			pact = undefined;
		},
		apocalypseShow: async (e) => {
			for (let step = 0; step < 4; step++) {
				apocalypse = { souls: e.souls, multiplier: e.multiplier, step };
				await wait(600);
			}
			apocalypse = undefined;
		},
		maxWinShow: async (e) => {
			maxWin = e.multiplier;
			await wait(2600);
			maxWin = undefined;
		},
		waysWinShow: (e) => {
			waysText = e.wins
				.map((w) => `${w.symbol} ${w.kind}OAK ${w.ways} WAYS${w.mult > 1 ? ` x${w.mult}` : ''}`)
				.join('   ');
		},
		waysWinHide: () => (waysText = ''),
	});
</script>

<BoardContainer>
	{#if waysText}
		<Text x={board.width / 2} y={board.height + SYMBOL_SIZE * 0.05} anchor={{ x: 0.5, y: 0 }} text={waysText} style={font(0.12, 0xe8d9c0, '600')} />
	{/if}

	{#if banner}
		<Rectangle y={board.height / 2 - SYMBOL_SIZE * (banner.big ? 0.75 : 0.5)} width={board.width} height={SYMBOL_SIZE * (banner.big ? 1.5 : 1)} backgroundColor={PALETTE.obsidian} backgroundAlpha={0.82} />
		<Text x={board.width / 2} y={board.height / 2 - (banner.subtitle ? SYMBOL_SIZE * 0.14 : 0)} anchor={0.5} text={banner.title} style={font(banner.big ? 0.55 : 0.38, banner.color)} />
		{#if banner.subtitle}
			<Text x={board.width / 2} y={board.height / 2 + SYMBOL_SIZE * (banner.big ? 0.36 : 0.26)} anchor={0.5} text={banner.subtitle} style={font(0.17, 0xffffff, '600')} />
		{/if}
	{/if}

	{#if pactVisible}
		<Rectangle width={board.width} height={board.height} backgroundColor={PALETTE.obsidian} backgroundAlpha={0.9} />
		<Text x={board.width / 2} y={SYMBOL_SIZE * 0.4} anchor={0.5} text="THE DEMON'S BARGAIN" style={font(0.36, PALETTE.gold)} />
		{#each ['blood', 'soul'] as const as key, i}
			{@const c = PACTS[key]}
			{@const chosen = pact === key}
			{@const dim = pact !== undefined && !chosen}
			<Container x={board.width * (i === 0 ? 0.06 : 0.53)} y={SYMBOL_SIZE * 0.8} alpha={dim ? 0.35 : 1}>
				<Rectangle width={board.width * 0.41} height={board.height - SYMBOL_SIZE * 1.0} borderRadius={14} backgroundColor={PALETTE.iron} borderColor={chosen ? 0xffffff : c.color} borderWidth={chosen ? 6 : 3} />
				<Text x={board.width * 0.205} y={SYMBOL_SIZE * 0.35} anchor={0.5} text={c.name} style={font(0.28, c.color)} />
				{#each c.lines as line, j}
					<Text x={board.width * 0.205} y={SYMBOL_SIZE * (0.8 + j * 0.32)} anchor={0.5} text={line} style={font(0.14, 0xe8d9c0, '600')} />
				{/each}
				{#if chosen}
					<Text x={board.width * 0.205} y={board.height - SYMBOL_SIZE * 1.3} anchor={0.5} text="SEALED" style={font(0.3, 0xffffff)} />
				{/if}
			</Container>
		{/each}
	{/if}

	{#if apocalypse}
		<Rectangle width={board.width} height={board.height} backgroundColor={0x000000} backgroundAlpha={0.88} />
		<Text x={board.width / 2} y={board.height / 2} anchor={0.5} text={apocalypse.step >= 2 ? 'APOCALYPSE CROWN' : 'CROWN'} style={font(0.34, PALETTE.gold)} />
		{#each apocalypse.souls as soul, i}
			{@const angle = (i / apocalypse.souls.length) * Math.PI * 2 + apocalypse.step * 0.6}
			<Circle x={board.width / 2 + Math.cos(angle) * SYMBOL_SIZE * 1.4 - SYMBOL_SIZE * 0.2} y={board.height / 2 + Math.sin(angle) * SYMBOL_SIZE * 1.4 - SYMBOL_SIZE * 0.2} diameter={SYMBOL_SIZE * 0.4} backgroundColor={SOUL_COLORS[soul]} borderColor={PALETTE.gold} borderWidth={2} />
		{/each}
		<Text x={board.width / 2} y={SYMBOL_SIZE * 0.35} anchor={0.5} text="SOUL APOCALYPSE" style={font(0.42, PALETTE.violet)} />
		{#if apocalypse.step >= 3}
			<Text x={board.width / 2} y={board.height - SYMBOL_SIZE * 0.4} anchor={0.5} text={`Wilds x${apocalypse.multiplier}`} style={font(0.24, 0xffffff)} />
		{/if}
	{/if}

	{#if maxWin}
		<Rectangle width={board.width} height={board.height} backgroundColor={PALETTE.obsidian} backgroundAlpha={0.92} />
		<Text x={board.width / 2} y={board.height / 2 - SYMBOL_SIZE * 0.4} anchor={0.5} text={`${maxWin.toLocaleString('en-US')}x`} style={font(0.8, PALETTE.gold)} />
		<Text x={board.width / 2} y={board.height / 2 + SYMBOL_SIZE * 0.45} anchor={0.5} text="MAXIMUM WIN" style={font(0.34, PALETTE.orange)} />
		<Text x={board.width / 2} y={board.height / 2 + SYMBOL_SIZE * 0.9} anchor={0.5} text="RULE BEYOND THE FLAMES" style={font(0.16, 0xffffff, '600')} />
	{/if}
</BoardContainer>
