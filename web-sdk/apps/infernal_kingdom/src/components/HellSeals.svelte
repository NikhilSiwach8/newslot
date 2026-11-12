<script lang="ts" module>
	import type { SealName, PatternName } from '../game/constants';

	export type EmitterEventHellSeals =
		| { type: 'sealsReset'; lit: SealName[] }
		| { type: 'sealsLight'; seal: SealName; lit: SealName[] }
		| { type: 'sealsPattern'; pattern: PatternName; lines: number[][] };
</script>

<script lang="ts">
	import { Tween } from 'svelte/motion';

	import { Circle, Container, Rectangle, Text } from 'pixi-svelte';
	import { stateBet } from 'state-shared';
	import { waitForTimeout } from 'utils-shared/wait';

	import BoardContainer from './BoardContainer.svelte';
	import { getContext } from '../game/context';
	import { SYMBOL_SIZE, SEALS, PALETTE } from '../game/constants';

	// The Nine Hell Seals board: a 3x3 grid beside the reels (above them on stacked layouts).
	const CELL = SYMBOL_SIZE * 0.42;
	const GAP = SYMBOL_SIZE * 0.08;
	const PANEL = CELL * 3 + GAP * 4;

	const context = getContext();
	const board = $derived(context.stateGameDerived.boardLayout());
	const stacked = $derived(context.stateLayoutDerived.isStacked());
	const position = $derived(
		stacked
			? { x: 0, y: -PANEL - SYMBOL_SIZE * 0.35 }
			: { x: -PANEL - SYMBOL_SIZE * 0.35, y: board.height - PANEL },
	);

	let lit = $state<SealName[]>([]);
	let flash = $state<SealName | undefined>(undefined);
	let lineCells = $state<number[]>([]);
	const glow = new Tween(0, { duration: 300 });

	context.eventEmitter.subscribeOnMount({
		sealsReset: ({ lit: l }) => {
			lit = [...l];
			lineCells = [];
		},
		sealsLight: async ({ seal, lit: l }) => {
			lit = [...l];
			flash = seal;
			await glow.set(1, { duration: 0 });
			await glow.set(0, { duration: stateBet.isTurbo ? 150 : 450 });
			flash = undefined;
		},
		sealsPattern: async ({ lines }) => {
			lineCells = lines.flat();
			await waitForTimeout(stateBet.isTurbo ? 150 : 500);
		},
	});
</script>

<BoardContainer>
	<Container {...position}>
		<Rectangle
			width={PANEL}
			height={PANEL + SYMBOL_SIZE * 0.3}
			y={-SYMBOL_SIZE * 0.3}
			borderRadius={10}
			backgroundColor={PALETTE.obsidian}
			backgroundAlpha={0.85}
			borderColor={PALETTE.gold}
			borderWidth={2}
		/>
		<Text
			x={PANEL / 2}
			y={-SYMBOL_SIZE * 0.15}
			anchor={0.5}
			text="NINE HELL SEALS"
			style={{ fontFamily: 'proxima-nova', fontSize: SYMBOL_SIZE * 0.13, fontWeight: '700', fill: PALETTE.gold }}
		/>
		{#each SEALS as seal, i}
			{@const on = lit.includes(seal)}
			{@const x = GAP + (i % 3) * (CELL + GAP)}
			{@const y = GAP + Math.floor(i / 3) * (CELL + GAP)}
			<Circle
				{x}
				{y}
				diameter={CELL}
				backgroundColor={on ? (seal === 'dominion' ? PALETTE.crimson : PALETTE.orange) : PALETTE.iron}
				backgroundAlpha={on ? 1 : 0.9}
				borderColor={lineCells.includes(i) ? 0xffffff : PALETTE.gold}
				borderWidth={lineCells.includes(i) ? 4 : 2}
				alpha={flash === seal ? 0.6 + 0.4 * (1 - glow.current) : 1}
			/>
			<Text
				x={x + CELL / 2}
				y={y + CELL / 2}
				anchor={0.5}
				text={seal.slice(0, 4).toUpperCase()}
				style={{ fontFamily: 'proxima-nova', fontSize: CELL * 0.24, fontWeight: '800', fill: on ? PALETTE.obsidian : 0x8a7560 }}
			/>
		{/each}
	</Container>
</BoardContainer>
