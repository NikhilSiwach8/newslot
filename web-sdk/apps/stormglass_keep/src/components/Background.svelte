<script lang="ts">
	import { Rectangle, Sprite } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';
	import { SECOND } from 'constants-shared/time';

	import { getContext } from '../game/context';

	// Source image sizes, used to scale each painting so it always covers the canvas.
	const BACKGROUNDS = {
		bgBaseLandscape: { width: 1672, height: 941 },
		bgBasePortrait: { width: 1024, height: 1536 },
		bgBonus: { width: 1145, height: 1374 },
		bgDrowned: { width: 1145, height: 1374 },
	} as const;
	type BackgroundKey = keyof typeof BACKGROUNDS;

	const context = getContext();
	const canvas = $derived(context.stateLayoutDerived.canvasSizes());
	const isFreeGame = $derived(context.stateGame.gameType === 'freegame');
	const isDrowned = $derived(isFreeGame && context.stateGame.bonusTier === 'drowned');
	const baseKey = $derived<BackgroundKey>(
		canvas.width >= canvas.height ? 'bgBaseLandscape' : 'bgBasePortrait',
	);

	const cover = (key: BackgroundKey) => {
		const image = BACKGROUNDS[key];
		const scale = Math.max(canvas.width / image.width, canvas.height / image.height);
		return {
			key,
			anchor: 0.5,
			x: canvas.width / 2,
			y: canvas.height / 2,
			width: image.width * scale,
			height: image.height * scale,
		};
	};
</script>

<Rectangle {...canvas} backgroundColor={0x06121a} zIndex={-4} />

<FadeContainer show={!isFreeGame} duration={SECOND} zIndex={-3}>
	<Sprite {...cover(baseKey)} />
</FadeContainer>

<FadeContainer show={isFreeGame && !isDrowned} duration={SECOND} zIndex={-2}>
	<Sprite {...cover('bgBonus')} />
</FadeContainer>

<FadeContainer show={isDrowned} duration={SECOND} zIndex={-1}>
	<Sprite {...cover('bgDrowned')} />
</FadeContainer>

<!-- darken slightly so symbols and UI stay readable over the painting -->
<Rectangle {...canvas} backgroundColor={0x000000} backgroundAlpha={0.25} zIndex={0} />
