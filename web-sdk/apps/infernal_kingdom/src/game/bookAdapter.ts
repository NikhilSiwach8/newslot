/**
 * Adapt Infernal Kingdom math books to the padded board the SDK reel components expect.
 *
 * The math engine writes 6 reels x 4 rows with no padding. The SDK board keeps one hidden
 * symbol above and below each reel, and on a tumble the hidden top symbol is the first to
 * drop into view. This adapter:
 *   - adds a padding row above and below every board and shifts every row index by +1;
 *   - rewrites each tumble's `newSymbols` to the SDK shape (new hidden top symbol first,
 *     then the cells that will sit above the old hidden symbol), and sets the old hidden
 *     symbol to the cell the math says drops in last. Because it sees the whole book first,
 *     the hidden symbol always matches what the math decided.
 * Events map one to one, so event indexes (used to resume a bet) are unchanged.
 */
import type { BookEvent } from './typesBookEvent';
import type { Position, RawSymbol } from './types';

const PAD: RawSymbol = { name: 'L5' };
const BOARD_KEYS = new Set(['reveal', 'specialResolve', 'sealPower', 'sealPattern', 'infernalTakeover', 'soulApocalypse']);

const shift = (p: Position): Position => ({ reel: p.reel, row: p.row + 1 });

export const adaptBook = (events: BookEvent[]): BookEvent[] => {
	// Current hidden top symbol of each reel, as an object we can still edit later.
	let topPads: RawSymbol[] = [];

	const pad = (board: RawSymbol[][]) => {
		topPads = board.map(() => ({ ...PAD }));
		return board.map((reel, i) => [topPads[i], ...reel.map((s) => ({ ...s })), { ...PAD }]);
	};

	return events.map((source) => {
		const event = structuredClone(source) as any;
		if (BOARD_KEYS.has(event.type) && Array.isArray(event.board)) {
			event.board = pad(event.board);
		}
		if (event.type === 'reveal') {
			event.paddingPositions = event.board.map(() => 0);
			event.anticipation = event.board.map(() => 0);
		}
		for (const key of ['positions', 'explodingSymbols']) {
			if (Array.isArray(event[key])) event[key] = event[key].map(shift);
		}
		if (event.origin) event.origin = shift(event.origin);
		if (event.type === 'winInfo') {
			event.wins = event.wins.map((w: any) => ({ ...w, positions: w.positions.map(shift) }));
		}
		if (event.type === 'tumbleBoard') {
			event.newSymbols = (event.newSymbols as RawSymbol[][]).map((fresh, reel) => {
				if (!fresh.length) return [];
				// fresh is top-down for rows 0..k-1. The old hidden symbol lands in row k-1.
				Object.assign(topPads[reel], fresh[fresh.length - 1]);
				const newTop = { ...PAD };
				topPads[reel] = newTop;
				return [newTop, ...fresh.slice(0, -1)];
			});
		}
		return event as BookEvent;
	});
};
