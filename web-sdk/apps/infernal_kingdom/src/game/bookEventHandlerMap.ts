import _ from 'lodash';

import { recordBookEvent, checkIsMultipleRevealEvents, type BookEventHandlerMap } from 'utils-book';
import { stateBet } from 'state-shared';

import { eventEmitter } from './eventEmitter';
import { playBookEvent } from './utils';
import { winLevelMap, type WinLevel, type WinLevelData } from './winLevelMap';
import { stateGame, stateGameDerived } from './stateGame.svelte';
import type { BookEvent, BookEventOfType, BookEventContext } from './typesBookEvent';
import type { Position, RawSymbol } from './types';
import {
	BONUS_NAMES,
	PALETTE,
	PATTERN_NAMES,
	SEAL_POWER_NAMES,
	MAX_WIN_X,
	type BonusName,
} from './constants';

// Presentation only: every amount, symbol and outcome below comes from the book. Nothing
// here draws randomness or changes a result; animations only decide how long things take.

const winLevelSoundsPlay = ({ winLevelData }: { winLevelData: WinLevelData }) => {
	if (winLevelData?.alias === 'max') eventEmitter.broadcastAsync({ type: 'uiHide' });
	if (winLevelData?.sound?.sfx) {
		eventEmitter.broadcast({ type: 'soundOnce', name: winLevelData.sound.sfx });
	}
	if (winLevelData?.sound?.bgm) {
		eventEmitter.broadcast({ type: 'soundMusic', name: winLevelData.sound.bgm });
	}
	if (winLevelData?.type === 'big') {
		eventEmitter.broadcast({ type: 'soundLoop', name: 'sfx_bigwin_coinloop' });
	}
};

const winLevelSoundsStop = () => {
	eventEmitter.broadcast({ type: 'soundStop', name: 'sfx_bigwin_coinloop' });
	if (stateGame.gameType === 'freegame') {
		eventEmitter.broadcast({ type: 'soundMusic', name: 'bgm_freespin' });
	} else {
		eventEmitter.broadcast({ type: 'soundMusic', name: 'bgm_main' });
	}
	eventEmitter.broadcastAsync({ type: 'uiShow' });
};

const animateSymbols = async ({ positions }: { positions: Position[] }) => {
	if (!positions.length) return;
	eventEmitter.broadcast({ type: 'boardShow' });
	await eventEmitter.broadcastAsync({
		type: 'boardWithAnimateSymbols',
		symbolPositions: positions,
	});
};

const settle = (board: RawSymbol[][]) => {
	eventEmitter.broadcast({ type: 'boardSettle', board });
};

const banner = async (title: string, color: number, subtitle = '', big = false) => {
	await eventEmitter.broadcastAsync({ type: 'featureBanner', title, subtitle, color, big });
};

const tumble = async ({
	explodingSymbols,
	newSymbols,
}: {
	explodingSymbols: Position[];
	newSymbols: RawSymbol[][];
}) => {
	eventEmitter.broadcast({ type: 'boardHide' });
	eventEmitter.broadcast({ type: 'tumbleBoardShow' });
	eventEmitter.broadcast({ type: 'tumbleBoardInit', addingBoard: newSymbols });
	eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_explosion_b' });
	await eventEmitter.broadcastAsync({
		type: 'tumbleBoardExplode',
		explodingPositions: explodingSymbols,
	});
	eventEmitter.broadcast({ type: 'tumbleBoardRemoveExploded' });
	await eventEmitter.broadcastAsync({ type: 'tumbleBoardSlideDown' });
	eventEmitter.broadcast({
		type: 'boardSettle',
		board: stateGameDerived
			.tumbleBoardCombined()
			.map((tumbleReel) => tumbleReel.map((tumbleSymbol) => tumbleSymbol.rawSymbol)),
	});
	eventEmitter.broadcast({ type: 'tumbleBoardReset' });
	eventEmitter.broadcast({ type: 'tumbleBoardHide' });
	eventEmitter.broadcast({ type: 'boardShow' });
};

const findBonus = (bookEvents: BookEvent[], fromIndex: number) =>
	bookEvents.find(
		(event): event is BookEventOfType<'enterBonus'> =>
			event.type === 'enterBonus' && event.index > fromIndex,
	);

const SPECIAL_LABELS = {
	split: ['SPLIT', 0xe8e8e8],
	wildBomb: ['WILD BOMB', PALETTE.orange],
	goldenWildBomb: ['GOLDEN WILD BOMB', PALETTE.gold],
	overlord: ['DEMON OVERLORD', PALETTE.crimson],
	soulWild: ['SOUL WILD', PALETTE.emerald],
} as const;

const MILESTONE_TEXT = {
	extraWild: ['3 SOULS', 'An extra Infernal Wild every spin'],
	enhancedMultipliers: ['5 SOULS', 'Enhanced wild multipliers'],
	soulApocalypse: ['7 SOULS', 'The Soul Apocalypse awakens'],
} as const;

export const bookEventHandlerMap: BookEventHandlerMap<BookEvent, BookEventContext> = {
	reveal: async (bookEvent: BookEventOfType<'reveal'>, { bookEvents }: BookEventContext) => {
		eventEmitter.broadcast({ type: 'tumbleWinAmountReset' });
		eventEmitter.broadcast({ type: 'globalMultiplierHide' });
		stateGame.takeover = false;
		const isBonusGame = checkIsMultipleRevealEvents({ bookEvents });
		if (isBonusGame) {
			eventEmitter.broadcast({ type: 'stopButtonEnable' });
			recordBookEvent({ bookEvent });
		}
		stateGame.gameType = bookEvent.gameType;
		await stateGameDerived.enhancedBoard.spin({ revealEvent: bookEvent });
		eventEmitter.broadcast({ type: 'soundScatterCounterClear' });
	},
	winInfo: async (bookEvent: BookEventOfType<'winInfo'>) => {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_winlevel_small' });
		eventEmitter.broadcast({
			type: 'waysWinShow',
			wins: bookEvent.wins.map((w) => ({
				symbol: w.symbol,
				kind: w.kind,
				ways: w.ways,
				win: w.win,
				mult: w.meta.wildMult * w.meta.globalMult,
			})),
		});
		await animateSymbols({ positions: _.uniqWith(_.flatten(bookEvent.wins.map((w) => w.positions)), _.isEqual) });
	},
	updateTumbleWin: async (bookEvent: BookEventOfType<'updateTumbleWin'>) => {
		if (bookEvent.amount > 0) {
			eventEmitter.broadcast({ type: 'tumbleWinAmountShow' });
			eventEmitter.broadcast({ type: 'tumbleWinAmountUpdate', amount: bookEvent.amount, animate: false });
		}
	},
	setTotalWin: async (bookEvent: BookEventOfType<'setTotalWin'>) => {
		stateBet.winBookEventAmount = bookEvent.amount;
	},
	setWin: async (bookEvent: BookEventOfType<'setWin'>) => {
		const winLevelData = winLevelMap[bookEvent.winLevel as WinLevel];
		eventEmitter.broadcast({ type: 'winShow' });
		winLevelSoundsPlay({ winLevelData });
		await eventEmitter.broadcastAsync({ type: 'winUpdate', amount: bookEvent.amount, winLevelData });
		winLevelSoundsStop();
		eventEmitter.broadcast({ type: 'winHide' });
	},
	tumbleBoard: async (bookEvent: BookEventOfType<'tumbleBoard'>) => {
		await tumble({ explodingSymbols: bookEvent.explodingSymbols, newSymbols: bookEvent.newSymbols });
	},

	// ------------------------------------------------------------ special symbols
	specialResolve: async (bookEvent: BookEventOfType<'specialResolve'>) => {
		const [label, color] = SPECIAL_LABELS[bookEvent.kind];
		const sub = bookEvent.kind === 'overlord' && bookEvent.multiplier ? `All wilds x${bookEvent.multiplier}` : '';
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_landing' });
		await animateSymbols({ positions: [bookEvent.origin] });
		settle(bookEvent.board);
		await banner(label, color, sub);
	},

	// ------------------------------------------------------------ Nine Hell Seals
	sealReset: async (bookEvent: BookEventOfType<'sealReset'>) => {
		eventEmitter.broadcast({ type: 'sealsReset', lit: bookEvent.lit });
	},
	sealLit: async (bookEvent: BookEventOfType<'sealLit'>) => {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_scatter_stop_3' });
		await eventEmitter.broadcastAsync({ type: 'sealsLight', seal: bookEvent.seal, lit: bookEvent.lit });
	},
	sealPower: async (bookEvent: BookEventOfType<'sealPower'>) => {
		settle(bookEvent.board);
		if (bookEvent.positions?.length) await animateSymbols({ positions: bookEvent.positions.map((p) => ({ reel: p.reel, row: p.row })) });
		await banner(SEAL_POWER_NAMES[bookEvent.seal], PALETTE.gold, bookEvent.seal.toUpperCase());
	},
	sealPattern: async (bookEvent: BookEventOfType<'sealPattern'>) => {
		eventEmitter.broadcast({ type: 'sealsPattern', pattern: bookEvent.pattern, lines: bookEvent.lines });
		settle(bookEvent.board);
		const sub = bookEvent.multiplier ? `All wins x${bookEvent.multiplier}` : '';
		await banner(PATTERN_NAMES[bookEvent.pattern], PALETTE.orange, sub, bookEvent.pattern === 'infernal_dominion');
	},
	instantWin: async (bookEvent: BookEventOfType<'instantWin'>) => {
		await animateSymbols({ positions: bookEvent.positions });
	},
	globalMult: async (bookEvent: BookEventOfType<'globalMult'>) => {
		eventEmitter.broadcast({ type: 'globalMultiplierShow' });
		await eventEmitter.broadcastAsync({ type: 'globalMultiplierUpdate', multiplier: bookEvent.multiplier });
	},

	// ------------------------------------------------------------ Infernal Takeover
	infernalTakeover: async (bookEvent: BookEventOfType<'infernalTakeover'>) => {
		stateGame.takeover = true;
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_superfreespin' });
		await banner('INFERNAL TAKEOVER', PALETTE.crimson, 'The Demon King seizes two reels', true);
		settle(bookEvent.board);
	},

	// ------------------------------------------------------------ bonuses
	freeSpinTrigger: async (bookEvent: BookEventOfType<'freeSpinTrigger'>, { bookEvents }: BookEventContext) => {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_scatter_win_v2' });
		await animateSymbols({ positions: bookEvent.positions });
		if (bookEvent.retrigger) {
			await banner('RETRIGGER', PALETTE.violet, `${bookEvent.totalFs} free spins`);
			eventEmitter.broadcast({ type: 'freeSpinCounterUpdate', current: undefined, total: bookEvent.totalFs });
			return;
		}
		const bonus = findBonus(bookEvents, bookEvent.index)?.bonus;
		stateGame.bonusTier = bonus;
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_superfreespin' });
		await eventEmitter.broadcastAsync({ type: 'uiHide' });
		await eventEmitter.broadcastAsync({ type: 'transition' });
		if (bonus) await banner(BONUS_NAMES[bonus], PALETTE.gold, `${bookEvent.totalFs} FREE SPINS`, true);
		eventEmitter.broadcast({ type: 'freeSpinIntroShow' });
		eventEmitter.broadcast({ type: 'soundOnce', name: 'jng_intro_fs' });
		eventEmitter.broadcast({ type: 'soundMusic', name: 'bgm_freespin' });
		await eventEmitter.broadcastAsync({ type: 'freeSpinIntroUpdate', totalFreeSpins: bookEvent.totalFs });
		stateGame.gameType = 'freegame';
		eventEmitter.broadcast({ type: 'freeSpinIntroHide' });
		eventEmitter.broadcast({ type: 'boardFrameGlowShow' });
		eventEmitter.broadcast({ type: 'freeSpinCounterShow' });
		eventEmitter.broadcast({ type: 'freeSpinCounterUpdate', current: undefined, total: bookEvent.totalFs });
		await eventEmitter.broadcastAsync({ type: 'uiShow' });
		await eventEmitter.broadcastAsync({ type: 'drawerButtonShow' });
		eventEmitter.broadcast({ type: 'drawerFold' });
	},
	demonsBargain: async (bookEvent: BookEventOfType<'demonsBargain'>) => {
		// The pact was chosen before the bet (it selects the bet mode); this seals the contract.
		await eventEmitter.broadcastAsync({ type: 'pactShow', pact: bookEvent.pact });
	},
	enterBonus: async (bookEvent: BookEventOfType<'enterBonus'>) => {
		stateGame.bonusTier = bookEvent.bonus as BonusName;
		eventEmitter.broadcast({ type: 'soulsShow' });
		eventEmitter.broadcast({ type: 'soulsUpdate', collected: bookEvent.souls, shards: 0, fresh: [] });
	},
	updateFreeSpin: async (bookEvent: BookEventOfType<'updateFreeSpin'>) => {
		eventEmitter.broadcast({ type: 'freeSpinCounterShow' });
		eventEmitter.broadcast({ type: 'freeSpinCounterUpdate', current: bookEvent.amount, total: bookEvent.total });
	},
	abyssalPurge: async (bookEvent: BookEventOfType<'abyssalPurge'>) => {
		if (bookEvent.positions.length) await banner('ABYSSAL PURGE', PALETTE.violet, 'J and 10 fall into the abyss');
	},

	// ------------------------------------------------------------ Seven Souls
	soulCollected: async (bookEvent: BookEventOfType<'soulCollected'>) => {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_update' });
		await eventEmitter.broadcastAsync({
			type: 'soulsUpdate',
			collected: bookEvent.collected,
			shards: bookEvent.shards,
			fresh: [...bookEvent.souls, ...bookEvent.fromShards],
		});
	},
	soulMilestone: async (bookEvent: BookEventOfType<'soulMilestone'>) => {
		const [title, sub] = MILESTONE_TEXT[bookEvent.effect];
		await banner(title, PALETTE.emerald, sub);
	},
	soulApocalypse: async (bookEvent: BookEventOfType<'soulApocalypse'>) => {
		await eventEmitter.broadcastAsync({ type: 'apocalypseShow', souls: bookEvent.souls, multiplier: bookEvent.multiplier });
		settle(bookEvent.board);
	},

	freeSpinEnd: async (bookEvent: BookEventOfType<'freeSpinEnd'>) => {
		const winLevelData = winLevelMap[bookEvent.winLevel as WinLevel];
		await eventEmitter.broadcastAsync({ type: 'uiHide' });
		stateGame.gameType = 'basegame';
		stateGame.bonusTier = undefined;
		stateGame.takeover = false;
		eventEmitter.broadcast({ type: 'boardFrameGlowHide' });
		eventEmitter.broadcast({ type: 'globalMultiplierHide' });
		eventEmitter.broadcast({ type: 'soulsHide' });
		eventEmitter.broadcast({ type: 'freeSpinOutroShow' });
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_youwon_panel' });
		winLevelSoundsPlay({ winLevelData });
		await eventEmitter.broadcastAsync({ type: 'freeSpinOutroCountUp', amount: bookEvent.amount, winLevelData });
		winLevelSoundsStop();
		eventEmitter.broadcast({ type: 'freeSpinOutroHide' });
		eventEmitter.broadcast({ type: 'freeSpinCounterHide' });
		eventEmitter.broadcast({ type: 'tumbleWinAmountHide' });
		await eventEmitter.broadcastAsync({ type: 'transition' });
		await eventEmitter.broadcastAsync({ type: 'uiShow' });
		await eventEmitter.broadcastAsync({ type: 'drawerUnfold' });
		eventEmitter.broadcast({ type: 'drawerButtonHide' });
	},
	wincap: async () => {
		await eventEmitter.broadcastAsync({ type: 'maxWinShow', multiplier: MAX_WIN_X });
	},
	finalWin: async () => {
		stateGame.takeover = false;
		eventEmitter.broadcast({ type: 'globalMultiplierHide' });
		eventEmitter.broadcast({ type: 'tumbleWinAmountHide' });
		eventEmitter.broadcast({ type: 'waysWinHide' });
	},

	// customised: rebuild bonus HUD state when resuming mid-bonus
	createBonusSnapshot: async (bookEvent: BookEventOfType<'createBonusSnapshot'>) => {
		const { bookEvents } = bookEvent;
		const last = <T extends BookEvent['type']>(type: T) =>
			_.findLast(bookEvents, (e) => e.type === type) as BookEventOfType<T> | undefined;
		const trigger = _.find(bookEvents, (e) => e.type === 'freeSpinTrigger') as BookEventOfType<'freeSpinTrigger'> | undefined;
		const enter = last('enterBonus');
		if (trigger) await playBookEvent({ ...trigger, retrigger: false }, { bookEvents });
		if (enter) playBookEvent(enter, { bookEvents });
		for (const type of ['updateFreeSpin', 'setTotalWin', 'globalMult', 'soulCollected'] as const) {
			const e = last(type);
			if (e) playBookEvent(e, { bookEvents });
		}
		const reset = last('sealReset');
		if (reset) {
			playBookEvent(reset, { bookEvents });
			for (const e of bookEvents) {
				if (e.type === 'sealLit' && e.index > reset.index) playBookEvent(e, { bookEvents });
			}
		}
	},
};
