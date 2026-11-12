import _ from 'lodash';

import type { RawSymbol, SymbolState } from './types';

export const SYMBOL_SIZE = 100;

export const REEL_PADDING = 0.53;

// Initial board: 6 reels x (padding + 4 rows + padding). Math books carry no padding rows;
// game/bookAdapter.ts adds them before playback.
export const INITIAL_BOARD: RawSymbol[][] = [
	[{ name: 'L1' }, { name: 'H1' }, { name: 'L2' }, { name: 'L3' }, { name: 'H4' }, { name: 'L5' }],
	[{ name: 'L2' }, { name: 'L4' }, { name: 'H2' }, { name: 'L1' }, { name: 'L3' }, { name: 'L2' }],
	[{ name: 'L3' }, { name: 'H3' }, { name: 'L1' }, { name: 'W' }, { name: 'L4' }, { name: 'H5' }],
	[{ name: 'H5' }, { name: 'L5' }, { name: 'L2' }, { name: 'H2' }, { name: 'L1' }, { name: 'L3' }],
	[{ name: 'L1' }, { name: 'L2' }, { name: 'H3' }, { name: 'H1' }, { name: 'L4' }, { name: 'L2' }],
	[{ name: 'L4' }, { name: 'H4' }, { name: 'L3' }, { name: 'L5' }, { name: 'H5' }, { name: 'L1' }],
];

export const BOARD_DIMENSIONS = { x: INITIAL_BOARD.length, y: INITIAL_BOARD[0].length - 2 };

export const BOARD_SIZES = {
	width: SYMBOL_SIZE * BOARD_DIMENSIONS.x,
	height: SYMBOL_SIZE * BOARD_DIMENSIONS.y,
};

export const BACKGROUND_RATIO = 2039 / 1000;
export const PORTRAIT_BACKGROUND_RATIO = 1242 / 2208;
const PORTRAIT_RATIO = 800 / 1422;
const LANDSCAPE_RATIO = 1600 / 900;
const DESKTOP_RATIO = 1422 / 800;

const DESKTOP_HEIGHT = 800;
const LANDSCAPE_HEIGHT = 900;
const PORTRAIT_HEIGHT = 1422;
export const DESKTOP_MAIN_SIZES = { width: DESKTOP_HEIGHT * DESKTOP_RATIO, height: DESKTOP_HEIGHT };
export const LANDSCAPE_MAIN_SIZES = {
	width: LANDSCAPE_HEIGHT * LANDSCAPE_RATIO,
	height: LANDSCAPE_HEIGHT,
};
export const PORTRAIT_MAIN_SIZES = {
	width: PORTRAIT_HEIGHT * PORTRAIT_RATIO,
	height: PORTRAIT_HEIGHT,
};

export const HIGH_SYMBOLS = ['H1', 'H2', 'H3', 'H4', 'H5'];

export const INITIAL_SYMBOL_STATE: SymbolState = 'static';


const SPIN_OPTIONS_SHARED = {
	reelFallInDelay: 80,
	reelPaddingMultiplierNormal: 1.25,
	reelPaddingMultiplierAnticipated: 18,
	reelFallOutDelay: 145,
};

export const SPIN_OPTIONS_DEFAULT = {
	...SPIN_OPTIONS_SHARED,
	symbolFallInSpeed: 3.5,
	symbolFallInInterval: 30,
	symbolFallInBounceSpeed: 0.15,
	symbolFallInBounceSizeMulti: 0.5,
	symbolFallOutSpeed: 3.5,
	symbolFallOutInterval: 20,
};

export const SPIN_OPTIONS_FAST = {
	...SPIN_OPTIONS_SHARED,
	symbolFallInSpeed: 7,
	symbolFallInInterval: 0,
	symbolFallInBounceSpeed: 0.3,
	symbolFallInBounceSizeMulti: 0.25,
	symbolFallOutSpeed: 7,
	symbolFallOutInterval: 0,
};

export const MOTION_BLUR_VELOCITY = 31;

export const zIndexes = {
	background: {
		backdrop: -3,
		normal: -2,
		feature: -1,
	},
};

const explosion = {
	type: 'spine',
	assetKey: 'explosion',
	animationName: 'explosion',
	sizeRatios: { width: 1, height: 1 },
};

// Infernal Kingdom symbols are single sprites (placeholders until final art; see
// docs/ASSET_MANIFEST.md). A win is shown with a short pulse (SymbolSprite.svelte). The burst
// on removal is still the SDK sample's and must be replaced before submission.
const ikSymbol = (name: string) => {
	const still = {
		type: 'sprite',
		assetKey: `ik_${name}.png`,
		sizeRatios: { width: 1, height: 1 },
		pulse: false,
	};
	return {
		explosion,
		win: { ...still, pulse: true },
		postWinStatic: still,
		static: still,
		spin: still,
		land: still,
	};
};

export const SYMBOL_INFO_MAP = {
	H1: ikSymbol('h1'),
	H2: ikSymbol('h2'),
	H3: ikSymbol('h3'),
	H4: ikSymbol('h4'),
	H5: ikSymbol('h5'),
	L1: ikSymbol('l1'),
	L2: ikSymbol('l2'),
	L3: ikSymbol('l3'),
	L4: ikSymbol('l4'),
	L5: ikSymbol('l5'),
	W: ikSymbol('w'),
	HS: ikSymbol('hs'),
	S: ikSymbol('s'),
	WB: ikSymbol('wb'),
	GB: ikSymbol('gb'),
	SP: ikSymbol('sp'),
	DO: ikSymbol('do'),
} as const;

export const SCATTER_LAND_SOUND_MAP = {
	1: 'sfx_scatter_stop_1',
	2: 'sfx_scatter_stop_2',
	3: 'sfx_scatter_stop_3',
	4: 'sfx_scatter_stop_4',
	5: 'sfx_scatter_stop_5',
} as const;

// ---------------------------------------------------------------- Infernal Kingdom
// Mirrors math/infernal_kingdom/game_config.py.
export const PALETTE = {
	gold: 0xd6a04a,
	crimson: 0xa51d24,
	orange: 0xff6a00,
	obsidian: 0x080708,
	iron: 0x211a1a,
	emerald: 0x14b86e,
	violet: 0x923dce,
} as const;

export const SEALS = [
	'wrath', 'greed', 'envy', 'pride', 'lust', 'sloth', 'gluttony', 'despair', 'dominion',
] as const;
export type SealName = (typeof SEALS)[number];
export const SEAL_POWER_NAMES: Record<SealName, string> = {
	wrath: 'HELLFIRE',
	greed: 'SOUL HARVEST',
	envy: 'SYMBOL CORRUPTION',
	pride: 'INFERNAL SHIELD',
	lust: 'WILD ATTRACTION',
	sloth: 'TIME LOCK',
	gluttony: 'DEVOUR',
	despair: 'CATACLYSM',
	dominion: 'INFERNAL TAKEOVER',
};
export const PATTERN_NAMES = {
	hellfire: 'HELLFIRE',
	soul_harvest: 'SOUL HARVEST',
	cataclysm: 'CATACLYSM',
	infernal_dominion: 'INFERNAL DOMINION',
} as const;
export type PatternName = keyof typeof PATTERN_NAMES;

export const SOULS = ['wrath', 'greed', 'envy', 'pride', 'lust', 'sloth', 'gluttony'] as const;
export type SoulName = (typeof SOULS)[number];
export const SOUL_COLORS: Record<SoulName, number> = {
	wrath: 0xa51d24,
	greed: 0xd6a04a,
	envy: 0x14b86e,
	pride: 0x923dce,
	lust: 0xd0209a,
	sloth: 0x2f6fd6,
	gluttony: 0xff6a00,
};

export const BONUS_NAMES = {
	hellfire: 'HELLFIRE SPINS',
	covenant: "DEMON'S COVENANT",
	abyssal: 'ABYSSAL DESCENT',
	furnace: 'THE SOUL FURNACE',
} as const;
export type BonusName = keyof typeof BONUS_NAMES;

export const PACTS = {
	blood: {
		name: 'BLOOD PACT',
		color: 0xa51d24,
		lines: ['Higher wild multipliers', 'More Hellfire wilds', 'Takeover wilds x3 or x5', 'Highest peak, more volatile'],
	},
	soul: {
		name: 'SOUL PACT',
		color: 0x14b86e,
		lines: ['Wilds survive a cascade', 'Seals persist between spins', 'More Soul orbs', 'Steadier, lower peak'],
	},
} as const;
export type PactName = keyof typeof PACTS;

export const MAX_WIN_X = 66666;
