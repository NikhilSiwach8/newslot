<script lang="ts">
	import { Circle, SpineProvider, SpineTrack, Text } from 'pixi-svelte';

	import SymbolSpine from './SymbolSpine.svelte';
	import SymbolSprite from './SymbolSprite.svelte';
	import type { SymbolState, RawSymbol } from '../game/types';
	import { SYMBOL_SIZE, SOUL_COLORS, PALETTE, type SoulName } from '../game/constants';
	import { getSymbolInfo } from '../game/utils';
	import { getContext } from '../game/context';

	type Props = {
		x?: number;
		y?: number;
		state: SymbolState;
		rawSymbol: RawSymbol;
		oncomplete?: () => void;
		loop?: boolean;
	};

	const props: Props = $props();
	const context = getContext();
	const symbolInfo = $derived(getSymbolInfo({ rawSymbol: props.rawSymbol, state: props.state }));
	const isSprite = $derived(symbolInfo.type === 'sprite');
	const showWinFrame = $derived(
		['win', 'postWinStatic', 'explosion'].includes(props.state) &&
			!['S'].includes(props.rawSymbol.name),
	);
</script>

{#if isSprite}
	<SymbolSprite {symbolInfo} x={props.x} y={props.y} oncomplete={props.oncomplete} />
{:else}
	<SymbolSpine
		loop={props.loop}
		{symbolInfo}
		x={props.x}
		y={props.y}
		listener={{
			complete: props.oncomplete,
			event: (_, event) => {
				if (event.data?.name === 'wildExplode') {
					context.eventEmitter?.broadcast({ type: 'soundOnce', name: 'sfx_wild_explode' });
				}
			},
		}}
	/>
{/if}

<!-- Wild multiplier, Soul orb and Split marker overlays (all values come from the book) -->
{#if props.rawSymbol.multiplier && props.rawSymbol.multiplier > 1}
	<Text
		x={(props.x ?? 0) + SYMBOL_SIZE * 0.28}
		y={(props.y ?? 0) + SYMBOL_SIZE * 0.3}
		anchor={0.5}
		text={`x${props.rawSymbol.multiplier}`}
		style={{ fontFamily: 'proxima-nova', fontSize: SYMBOL_SIZE * 0.26, fontWeight: '900', fill: PALETTE.gold, stroke: { color: 0x000000, width: 4 } }}
	/>
{/if}
{#if props.rawSymbol.soul}
	<Circle
		x={(props.x ?? 0) - SYMBOL_SIZE * 0.3}
		y={(props.y ?? 0) - SYMBOL_SIZE * 0.3}
		anchor={0.5}
		diameter={SYMBOL_SIZE * 0.24}
		backgroundColor={SOUL_COLORS[props.rawSymbol.soul as SoulName] ?? 0xffffff}
		borderColor={0xffffff}
		borderWidth={2}
	/>
{/if}
{#if props.rawSymbol.double}
	<Text
		x={(props.x ?? 0) + SYMBOL_SIZE * 0.3}
		y={(props.y ?? 0) - SYMBOL_SIZE * 0.32}
		anchor={0.5}
		text="2x"
		style={{ fontFamily: 'proxima-nova', fontSize: SYMBOL_SIZE * 0.2, fontWeight: '900', fill: 0xffffff, stroke: { color: 0x000000, width: 4 } }}
	/>
{/if}

{#if showWinFrame}
	<SpineProvider x={props.x} y={props.y} key="anticipation" width={SYMBOL_SIZE * 0.19}>
		<SpineTrack trackIndex={0} animationName={'payframe'} loop />
	</SpineProvider>
{/if}
