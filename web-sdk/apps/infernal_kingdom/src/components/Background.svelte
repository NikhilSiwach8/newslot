<script lang="ts">
	import { Rectangle, Sprite } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';
	import { SECOND } from 'constants-shared/time';

	import { getContext } from '../game/context';

	// Source image sizes, used to scale each painting so it always covers the canvas.
	const BACKGROUNDS = {
		bgBaseLandscape: { width: 1920, height: 1080 },
		bgBasePortrait: { width: 1080, height: 1920 },
		bgBonus: { width: 1920, height: 1080 },
		bgTakeover: { width: 1920, height: 1080 },
	} as const;
	type BackgroundKey = keyof typeof BACKGROUNDS;

	const context = getContext();
	const canvas = $derived(context.stateLayoutDerived.canvasSizes());
	const isFreeGame = $derived(context.stateGame.gameType === 'freegame');
	// Infernal Takeover turns the world red for the rest of that spin.
	const isTakeover = $derived(context.stateGame.takeover);
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

<Rectangle {...canvas} backgroundColor={0x080708} zIndex={-4} />

<FadeContainer show={!isFreeGame && !isTakeover} duration={SECOND} zIndex={-3}>
	<Sprite {...cover(baseKey)} />
</FadeContainer>

<FadeContainer show={isFreeGame && !isTakeover} duration={SECOND} zIndex={-2}>
	<Sprite {...cover('bgBonus')} />
</FadeContainer>

<FadeContainer show={isTakeover} duration={SECOND / 2} zIndex={-1}>
	<Sprite {...cover('bgTakeover')} />
</FadeContainer>

<!-- darken slightly so symbols and UI stay readable over the painting -->
<Rectangle {...canvas} backgroundColor={0x000000} backgroundAlpha={0.25} zIndex={0} />
