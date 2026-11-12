import _ from 'lodash';
import { stateBet } from 'state-shared';
import { createPlayBookUtils } from 'utils-book';
import { createGetEmptyPaddedBoard } from 'utils-slots';

import { SYMBOL_SIZE, REEL_PADDING, SYMBOL_INFO_MAP, BOARD_DIMENSIONS } from './constants';
import { eventEmitter } from './eventEmitter';
import type { Bet, BookEventOfType } from './typesBookEvent';
import { bookEventHandlerMap } from './bookEventHandlerMap';
import { adaptBook } from './bookAdapter';
import type { RawSymbol, SymbolState } from './types';

// general utils
export const { getEmptyBoard } = createGetEmptyPaddedBoard({ reelsDimensions: BOARD_DIMENSIONS });
export const { playBookEvent, playBookEvents } = createPlayBookUtils({ bookEventHandlerMap });
export const playBet = async (bet: Bet) => {
	stateBet.winBookEventAmount = 0;
	const adapted = (bet as Bet & { adapted?: boolean }).adapted;
	await playBookEvents(adapted ? bet.state : adaptBook(bet.state));
	eventEmitter.broadcast({ type: 'stopButtonEnable' });
};

// resume bet
const BOOK_EVENT_TYPES_TO_RESERVE_FOR_SNAPSHOT = [
	'globalMult',
	'freeSpinTrigger',
	'enterBonus',
	'updateFreeSpin',
	'setTotalWin',
	'soulCollected',
	'sealReset',
	'sealLit',
];

export const convertTorResumableBet = (betToResumeRaw: Bet) => {
	// Already adapted here, so playBet must not adapt again: mark the bet.
	const betToResume = { ...betToResumeRaw, state: adaptBook(betToResumeRaw.state) };
	const resumingIndex = Number(betToResume.event);
	const bookEventsBeforeResume = betToResume.state.filter(
		(_, eventIndex) => eventIndex < resumingIndex,
	);
	const bookEventsAfterResume = betToResume.state.filter(
		(_, eventIndex) => eventIndex >= resumingIndex,
	);

	const bookEventToCreateSnapshot: BookEventOfType<'createBonusSnapshot'> = {
		index: 0,
		type: 'createBonusSnapshot',
		bookEvents: bookEventsBeforeResume.filter((bookEvent) =>
			BOOK_EVENT_TYPES_TO_RESERVE_FOR_SNAPSHOT.includes(bookEvent.type),
		),
	};

	const stateToResume = [bookEventToCreateSnapshot, ...bookEventsAfterResume];

	return { ...betToResume, state: stateToResume, adapted: true };
};

// other utils
export const getSymbolX = (reelIndex: number) => SYMBOL_SIZE * (reelIndex + REEL_PADDING);
export const getSymbolY = (symbolIndexOfBoard: number) => (symbolIndexOfBoard + 0.5) * SYMBOL_SIZE;

// Multipliers, Soul orbs and Split doubles are drawn as overlays (Symbol.svelte), so the
// sprite is chosen by name alone.
export const getSymbolKey = ({ rawSymbol }: { rawSymbol: RawSymbol }) =>
	rawSymbol.name as keyof typeof SYMBOL_INFO_MAP;

export const getSymbolInfo = ({
	rawSymbol,
	state,
}: {
	rawSymbol: RawSymbol;
	state: SymbolState;
}) => {
	const symbolKey = getSymbolKey({ rawSymbol });
	return SYMBOL_INFO_MAP[symbolKey][state];
};
