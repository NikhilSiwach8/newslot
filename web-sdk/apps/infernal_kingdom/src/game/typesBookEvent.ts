import type { BetType } from 'rgs-requests';

import type { SymbolName, RawSymbol, GameType, Position } from './types';
import type { BonusName, PactName, PatternName, SealName, SoulName } from './constants';

// Book events as produced by math/infernal_kingdom (see game_events.py). Boards and rows
// below are AFTER game/bookAdapter.ts has added one padding row above and below each reel.

type E<T extends string, P> = { index: number; type: T } & P;

type BookEventReveal = E<'reveal', {
	board: RawSymbol[][];
	paddingPositions: number[];
	anticipation: number[];
	gameType: GameType;
	reelStrip?: string;
}>;

type BookEventWinInfo = E<'winInfo', {
	totalWin: number;
	cappedFrom?: number;
	wins: {
		symbol: SymbolName;
		kind: number;
		ways: number;
		win: number;
		positions: Position[];
		meta: { wildMult: number; globalMult: number; winWithoutMult: number };
	}[];
}>;

type BookEventSetTumbleWin = E<'updateTumbleWin', { amount: number }>;
type BookEventSetTotalWin = E<'setTotalWin', { amount: number }>;
type BookEventSetWin = E<'setWin', { amount: number; winLevel: number }>;
type BookEventFinalWin = E<'finalWin', { amount: number }>;
type BookEventWincap = E<'wincap', { amount: number }>;
type BookEventFreeSpinTrigger = E<'freeSpinTrigger', { totalFs: number; positions: Position[]; retrigger: boolean }>;
type BookEventUpdateFreeSpin = E<'updateFreeSpin', { amount: number; total: number }>;
type BookEventFreeSpinEnd = E<'freeSpinEnd', { amount: number; winLevel: number }>;
type BookEventTumbleBoard = E<'tumbleBoard', {
	reason: string;
	explodingSymbols: Position[];
	newSymbols: RawSymbol[][];
}>;

type BookEventSpecialResolve = E<'specialResolve', {
	kind: 'split' | 'wildBomb' | 'goldenWildBomb' | 'overlord' | 'soulWild';
	origin: Position;
	positions: Position[];
	board: RawSymbol[][];
	symbol?: SymbolName;
	multiplier?: number;
}>;
type BookEventSealReset = E<'sealReset', { lit: SealName[]; prelit: SealName[] }>;
type BookEventSealLit = E<'sealLit', { seal: SealName; reason: string; lit: SealName[] }>;
type BookEventSealPower = E<'sealPower', {
	seal: SealName;
	board: RawSymbol[][];
	positions?: Position[];
	from?: SymbolName;
	to?: SymbolName;
	symbol?: SymbolName;
	symbols?: SymbolName[];
	reels?: number[];
	multiplier?: number;
}>;
type BookEventSealPattern = E<'sealPattern', {
	pattern: PatternName;
	lines: number[][];
	board: RawSymbol[][];
	reels?: number[];
	multiplier?: number;
}>;
type BookEventInstantWin = E<'instantWin', { source: string; amount: number; positions: Position[] }>;
type BookEventTakeover = E<'infernalTakeover', {
	trigger: 'random' | 'dominion';
	reels: number[];
	multiplier: number;
	board: RawSymbol[][];
}>;
type BookEventGlobalMult = E<'globalMult', { source: 'dominion' | 'descent'; multiplier: number; dominion: number; descent: number }>;
type BookEventSoulCollected = E<'soulCollected', {
	souls: SoulName[];
	duplicates: SoulName[];
	fromShards: SoulName[];
	collected: SoulName[];
	shards: number;
}>;
type BookEventSoulMilestone = E<'soulMilestone', { count: number; effect: 'extraWild' | 'enhancedMultipliers' | 'soulApocalypse' }>;
type BookEventSoulApocalypse = E<'soulApocalypse', { reels: number[]; multiplier: number; souls: SoulName[]; board: RawSymbol[][] }>;
type BookEventBargain = E<'demonsBargain', { pact: PactName }>;
type BookEventEnterBonus = E<'enterBonus', { bonus: BonusName; pact: PactName | null; totalFs: number; souls: SoulName[] }>;
type BookEventAbyssalPurge = E<'abyssalPurge', { positions: Position[] }>;

// customised
type BookEventCreateBonusSnapshot = E<'createBonusSnapshot', { bookEvents: BookEvent[] }>;

export type BookEvent =
	| BookEventReveal
	| BookEventWinInfo
	| BookEventSetTumbleWin
	| BookEventSetTotalWin
	| BookEventSetWin
	| BookEventFinalWin
	| BookEventWincap
	| BookEventFreeSpinTrigger
	| BookEventUpdateFreeSpin
	| BookEventFreeSpinEnd
	| BookEventTumbleBoard
	| BookEventSpecialResolve
	| BookEventSealReset
	| BookEventSealLit
	| BookEventSealPower
	| BookEventSealPattern
	| BookEventInstantWin
	| BookEventTakeover
	| BookEventGlobalMult
	| BookEventSoulCollected
	| BookEventSoulMilestone
	| BookEventSoulApocalypse
	| BookEventBargain
	| BookEventEnterBonus
	| BookEventAbyssalPurge
	| BookEventCreateBonusSnapshot;

export type Bet = BetType<BookEvent>;
export type BookEventOfType<T> = Extract<BookEvent, { type: T }>;
export type BookEventContext = { bookEvents: BookEvent[] };
