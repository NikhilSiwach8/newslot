<script lang="ts" module>
	import type { SoulName } from '../game/constants';

	export type EmitterEventSoulsMeter =
		| { type: 'soulsShow' }
		| { type: 'soulsHide' }
		| { type: 'soulsUpdate'; collected: SoulName[]; shards: number; fresh: SoulName[] };
</script>

<script lang="ts">
	import { Circle, Container, Rectangle, Text } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';
	import { stateBet } from 'state-shared';
	import { waitForTimeout } from 'utils-shared/wait';

	import BoardContainer from './BoardContainer.svelte';
	import { getContext } from '../game/context';
	import { SYMBOL_SIZE, SOULS, SOUL_COLORS, PALETTE } from '../game/constants';

	// Seven Souls collection meter: a column to the right of the reels during bonuses.
	const ORB = SYMBOL_SIZE * 0.36;
	const GAP = SYMBOL_SIZE * 0.1;
	const WIDTH = ORB + SYMBOL_SIZE * 0.5;
	const HEIGHT = SOULS.length * (ORB + GAP) + SYMBOL_SIZE * 0.75;

	const context = getContext();
	const board = $derived(context.stateGameDerived.boardLayout());
	// Stacked (portrait) layouts: a horizontal row above the reels, opposite the seals panel.
	const stacked = $derived(context.stateLayoutDerived.isStacked());
	const W = $derived(stacked ? SOULS.length * (ORB + GAP) + GAP : WIDTH);
	const H = $derived(stacked ? ORB + SYMBOL_SIZE * 0.55 : HEIGHT);
	const origin = $derived(
		stacked
			? { x: board.width - W, y: -H - SYMBOL_SIZE * 0.35 }
			: { x: board.width + SYMBOL_SIZE * 0.35, y: (board.height - HEIGHT) / 2 },
	);
	const orb = (i: number) =>
		stacked
			? { x: GAP + i * (ORB + GAP), y: SYMBOL_SIZE * 0.3 }
			: { x: (WIDTH - ORB) / 2, y: SYMBOL_SIZE * 0.38 + i * (ORB + GAP) };

	let show = $state(false);
	let collected = $state<SoulName[]>([]);
	let shards = $state(0);
	let fresh = $state<SoulName[]>([]);

	context.eventEmitter.subscribeOnMount({
		soulsShow: () => (show = true),
		soulsHide: () => {
			show = false;
			collected = [];
			shards = 0;
		},
		soulsUpdate: async (e) => {
			collected = [...e.collected];
			shards = e.shards;
			fresh = [...e.fresh];
			if (fresh.length) await waitForTimeout(stateBet.isTurbo ? 120 : 400);
			fresh = [];
		},
	});
</script>

<FadeContainer {show}>
	<BoardContainer>
		<Container {...origin}>
			<Rectangle width={W} height={H} borderRadius={10} backgroundColor={PALETTE.obsidian} backgroundAlpha={0.85} borderColor={PALETTE.gold} borderWidth={2} />
			<Text x={stacked ? GAP : W / 2} y={SYMBOL_SIZE * 0.15} anchor={stacked ? { x: 0, y: 0.5 } : 0.5} text={`SOULS ${collected.length}/7`} style={{ fontFamily: 'proxima-nova', fontSize: SYMBOL_SIZE * 0.13, fontWeight: '800', fill: PALETTE.gold }} />
			{#each SOULS as soul, i}
				{@const have = collected.includes(soul)}
				<Circle
					{...orb(i)}
					diameter={ORB}
					backgroundColor={SOUL_COLORS[soul]}
					backgroundAlpha={have ? 1 : 0.18}
					borderColor={fresh.includes(soul) ? 0xffffff : PALETTE.gold}
					borderWidth={fresh.includes(soul) ? 4 : 1}
				/>
			{/each}
			<Text x={stacked ? W - GAP : W / 2} y={stacked ? SYMBOL_SIZE * 0.15 : H - SYMBOL_SIZE * 0.16} anchor={stacked ? { x: 1, y: 0.5 } : 0.5} text={`SHARDS ${shards}/3`} style={{ fontFamily: 'proxima-nova', fontSize: SYMBOL_SIZE * 0.11, fontWeight: '700', fill: 0xc9b8a0 }} />
		</Container>
	</BoardContainer>
</FadeContainer>
