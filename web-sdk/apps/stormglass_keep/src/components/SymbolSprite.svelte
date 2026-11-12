<script lang="ts">
	import { onMount } from 'svelte';
	import { Tween } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	import { Sprite } from 'pixi-svelte';
	import { stateBet } from 'state-shared';

	import { getSymbolInfo } from '../game/utils';
	import { SYMBOL_SIZE } from '../game/constants';

	type Props = {
		x?: number;
		y?: number;
		symbolInfo: ReturnType<typeof getSymbolInfo>;
		oncomplete?: () => void;
	};

	const props: Props = $props();
	const PULSE_SCALE = 1.22;
	const scale = new Tween(1, { easing: cubicOut });

	// Win state: grow and settle twice, then report completion so the tumble can continue.
	const pulse = async () => {
		const duration = stateBet.isTurbo ? 110 : 230;
		for (let i = 0; i < 2; i++) {
			await scale.set(PULSE_SCALE, { duration });
			await scale.set(1, { duration });
		}
	};

	const play = async () => {
		if ('pulse' in props.symbolInfo && props.symbolInfo.pulse) await pulse();
		props.oncomplete?.();
	};

	let mounted = false;
	onMount(() => {
		mounted = true;
		play();
	});

	$effect(() => {
		props.symbolInfo;
		if (mounted) play();
	});
</script>

<Sprite
	x={props.x}
	y={props.y}
	anchor={0.5}
	key={props.symbolInfo.assetKey}
	width={SYMBOL_SIZE * props.symbolInfo.sizeRatios.width * scale.current}
	height={SYMBOL_SIZE * props.symbolInfo.sizeRatios.height * scale.current}
/>
