<script lang="ts" module>
	import type { BonusTier } from '../game/typesBookEvent';

	export type EmitterEventBeamMeter =
		| { type: 'beamMeterUpdate'; meter: number }
		| { type: 'beamMeterReset' }
		| { type: 'beamStageFire'; stage: 1 | 2 | 3 }
		| { type: 'bonusTierShow'; tier: BonusTier }
		| { type: 'bonusTierHide' };
</script>

<script lang="ts">
	import { Tween } from 'svelte/motion';

	import { Container, Rectangle, Text } from 'pixi-svelte';
	import { stateBet } from 'state-shared';
	import { waitForTimeout } from 'utils-shared/wait';

	import BoardContainer from './BoardContainer.svelte';
	import { getContext } from '../game/context';
	import { SYMBOL_SIZE, BEAM_THRESHOLDS, BEAM_METER_MAX, BONUS_TIER_NAMES } from '../game/constants';

	// Placeholder presentation: plain shapes and text until the lighthouse art exists.
	const PIP_WIDTH = SYMBOL_SIZE * 0.22;
	const PIP_HEIGHT = SYMBOL_SIZE * 0.1;
	const PIP_GAP = SYMBOL_SIZE * 0.06;
	const STAGE_COLORS = { 1: 0x7fd4ff, 2: 0xffd166, 3: 0xffffff } as const;
	const STAGE_LABELS = { 1: 'BEAM: CLEAR', 2: 'BEAM: WILDS', 3: 'BEAM: SURGE' } as const;

	const context = getContext();
	const boardSizes = $derived(context.stateGameDerived.boardLayout());

	let meter = $state(0);
	let tier = $state<BonusTier | undefined>(undefined);
	let flashStage = $state<1 | 2 | 3>(1);
	const flashAlpha = new Tween(0, { duration: 350 });

	const stageAt = (pip: number) =>
		(Object.entries(BEAM_THRESHOLDS).find(([, threshold]) => threshold === pip)?.[0] ?? 0) as
			| 0
			| '1'
			| '2'
			| '3';

	context.eventEmitter.subscribeOnMount({
		beamMeterUpdate: (emitterEvent) => (meter = Math.min(emitterEvent.meter, BEAM_METER_MAX)),
		beamMeterReset: () => (meter = 0),
		beamStageFire: async ({ stage }) => {
			flashStage = stage;
			context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_landing' });
			await flashAlpha.set(0.55, { duration: 0 });
			flashAlpha.set(0);
			await waitForTimeout(stateBet.isTurbo ? 150 : 450);
		},
		bonusTierShow: (emitterEvent) => (tier = emitterEvent.tier),
		bonusTierHide: () => (tier = undefined),
	});
</script>

<BoardContainer>
	<Rectangle
		width={boardSizes.width}
		height={boardSizes.height}
		backgroundColor={STAGE_COLORS[flashStage]}
		backgroundAlpha={flashAlpha.current}
	/>
	{#if flashAlpha.current > 0.05}
		<Text
			x={boardSizes.width / 2}
			y={boardSizes.height / 2}
			anchor={0.5}
			text={STAGE_LABELS[flashStage]}
			style={{
				fontFamily: 'proxima-nova',
				fontSize: SYMBOL_SIZE * 0.7,
				fontWeight: '800',
				fill: 0x10202c,
			}}
		/>
	{/if}

	<!-- top-left of the board: label above the pips, clear of the tumble-win panel -->
	<Container x={0} y={-SYMBOL_SIZE * 0.3}>
		<Text
			y={-SYMBOL_SIZE * 0.34}
			anchor={{ x: 0, y: 0.5 }}
			text={tier ? BONUS_TIER_NAMES[tier] : 'BEAM'}
			style={{
				fontFamily: 'proxima-nova',
				fontSize: SYMBOL_SIZE * 0.24,
				fontWeight: '700',
				fill: tier ? 0xffd166 : 0xffffff,
			}}
		/>
		{#each Array(BEAM_METER_MAX) as _, index}
			{@const pip = index + 1}
			{@const stage = stageAt(pip)}
			<Rectangle
				x={index * (PIP_WIDTH + PIP_GAP)}
				y={-(stage ? PIP_HEIGHT : PIP_HEIGHT / 2)}
				width={PIP_WIDTH}
				height={stage ? PIP_HEIGHT * 2 : PIP_HEIGHT}
				borderRadius={3}
				backgroundColor={meter >= pip ? (stage ? 0xffd166 : 0x7fd4ff) : 0x24323d}
				borderColor={0xffffff}
				borderWidth={stage ? 2 : 1}
				borderAlpha={0.6}
			/>
		{/each}
	</Container>
</BoardContainer>
