import { type CascadingReelSymbolState } from 'utils-slots';
import type config from './config';

export type SymbolName =
	| 'H1' | 'H2' | 'H3' | 'H4' | 'H5'
	| 'L1' | 'L2' | 'L3' | 'L4' | 'L5'
	| 'W' | 'HS' | 'S' | 'WB' | 'GB' | 'SP' | 'DO';
export type RawSymbol = {
	name: SymbolName;
	multiplier?: number; // wild multiplier (x2 and above)
	group?: number; // wilds sharing a group share one multiplier
	soul?: string; // Seven Souls orb carried by the symbol (bonus only)
	double?: boolean; // Split Symbol result: counts as two
	scatter?: boolean;
};
export type BetMode = keyof typeof config.betModes;
export type GameType = 'basegame' | 'freegame';

export const SYMBOL_STATES = [
	'static',
	'spin',
	'land',
	'win',
	'postWinStatic',
	'explosion',
] as const;

export type SymbolState = CascadingReelSymbolState | (typeof SYMBOL_STATES)[number];

export type Position = {
	reel: number;
	row: number;
};
