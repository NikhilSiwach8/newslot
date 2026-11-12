import type { BetModeMeta } from 'state-shared';

import config from './config';

// Bet modes shown in the bet-mode / bonus-buy menu. Costs and max wins come from the math config.
//
// Demon's Bargain: Stake Engine decides the whole round when the bet is placed, so the pact
// is chosen BEFORE the bet. BASE plays with the Blood Pact; activating SOUL PACT switches the
// base game to the Soul Pact at the same 1x price. Pact bonuses can also be bought directly.
// Asset slots stay empty until Infernal Kingdom art is on the Stake Engine CDN.
const NO_ASSETS = { icon: '', volatility: '', button: '', dialogImage: '', dialogVolatility: '' };
const MAX = `Maximum win ${config.betModes.base.max_win.toLocaleString('en-US')}x the bet.`;

const mode = (
	key: keyof typeof config.betModes,
	type: 'default' | 'activate' | 'buy',
	text: { title: string; dialog: string; description: string; button: string; tickerSpin: string },
) => ({
	mode: key.toUpperCase(),
	costMultiplier: config.betModes[key].cost,
	maxWin: config.betModes[key].max_win,
	type,
	parent: '',
	children: '',
	assets: NO_ASSETS,
	text: {
		title: text.title,
		dialog: text.dialog,
		description: text.description,
		button: text.button,
		betAmountLabel: type === 'activate' ? text.title : '',
		tickerIdle: type === 'activate' ? `${text.title} IS ACTIVE` : 'RULE BEYOND THE FLAMES',
		tickerSpin: text.tickerSpin,
		bannerText: '',
	},
});

const cost = (key: keyof typeof config.betModes) => `${config.betModes[key].cost}x the bet`;

export const betModeMeta: BetModeMeta = {
	BASE: mode('base', 'default', {
		title: '',
		dialog: '',
		description: '',
		button: '',
		tickerSpin: 'GOOD LUCK',
	}),
	BASE_SOUL: mode('base_soul', 'activate', {
		title: 'SOUL PACT',
		dialog: `Choose the Soul Pact for every Demon's Covenant and Soul Furnace you trigger: wilds survive a cascade, the Hell Seals persist between free spins and Soul orbs appear more often, with a lower peak than the Blood Pact. Same price as the normal bet. Without it you play the Blood Pact. Return to player is the same for both pacts. ${MAX}`,
		description: 'Your triggered pact bonuses use the Soul Pact.',
		button: 'ACTIVATE',
		tickerSpin: 'GOOD LUCK',
	}),
	HELLFIRE: mode('hellfire', 'buy', {
		title: 'HELLFIRE SPINS',
		dialog: `Buy HELLFIRE SPINS for ${cost('hellfire')}: 10 free spins with multiplier wilds, the Nine Hell Seals and the Seven Souls. ${MAX}`,
		description: '10 free spins, multiplier wilds, Seven Souls.',
		button: 'BUY',
		tickerSpin: 'BONUS BUY ACTIVATED',
	}),
	COVENANT_BLOOD: mode('covenant_blood', 'buy', {
		title: "DEMON'S COVENANT - BLOOD",
		dialog: `Buy DEMON'S COVENANT with the BLOOD PACT for ${cost('covenant_blood')}: 12 free spins with higher wild multipliers and more Hellfire wilds. ${MAX}`,
		description: '12 free spins, Blood Pact.',
		button: 'BUY',
		tickerSpin: 'BONUS BUY ACTIVATED',
	}),
	COVENANT_SOUL: mode('covenant_soul', 'buy', {
		title: "DEMON'S COVENANT - SOUL",
		dialog: `Buy DEMON'S COVENANT with the SOUL PACT for ${cost('covenant_soul')}: 12 free spins where wilds survive a cascade and the Hell Seals persist between spins. ${MAX}`,
		description: '12 free spins, Soul Pact.',
		button: 'BUY',
		tickerSpin: 'BONUS BUY ACTIVATED',
	}),
	ABYSSAL: mode('abyssal', 'buy', {
		title: 'ABYSSAL DESCENT',
		dialog: `Buy ABYSSAL DESCENT for ${cost('abyssal')}: 10 free spins with a win multiplier that grows by 1 with every winning cascade and never resets (up to x25). Every spin starts by purging J and 10. ${MAX}`,
		description: '10 free spins, ever-growing multiplier.',
		button: 'BUY',
		tickerSpin: 'BONUS BUY ACTIVATED',
	}),
	FURNACE_BLOOD: mode('furnace_blood', 'buy', {
		title: 'THE SOUL FURNACE - BLOOD',
		dialog: `Buy THE SOUL FURNACE with the BLOOD PACT for ${cost('furnace_blood')}: 12 free spins starting with 2 Souls and 2 lit Seals, frequent Infernal Takeovers. ${MAX}`,
		description: '12 free spins, 2 Souls to start, Blood Pact.',
		button: 'BUY',
		tickerSpin: 'BONUS BUY ACTIVATED',
	}),
	FURNACE_SOUL: mode('furnace_soul', 'buy', {
		title: 'THE SOUL FURNACE - SOUL',
		dialog: `Buy THE SOUL FURNACE with the SOUL PACT for ${cost('furnace_soul')}: 12 free spins starting with 2 Souls and 2 lit Seals, frequent Infernal Takeovers. ${MAX}`,
		description: '12 free spins, 2 Souls to start, Soul Pact.',
		button: 'BUY',
		tickerSpin: 'BONUS BUY ACTIVATED',
	}),
};
