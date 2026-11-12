import type { BetModeMeta } from 'state-shared';

import config from './config';

// Bet modes shown in the bet-mode / bonus-buy menu. Costs and max wins come from the math config.
// Asset slots are left empty until Stormglass Keep art is on the Stake Engine CDN.
const NO_ASSETS = { icon: '', volatility: '', button: '', dialogImage: '', dialogVolatility: '' };

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
		tickerIdle: type === 'activate' ? `${text.title} IS ACTIVE` : 'PLACE YOUR BET',
		tickerSpin: text.tickerSpin,
		bannerText: '',
	},
});

export const betModeMeta: BetModeMeta = {
	BASE: mode('base', 'default', {
		title: '',
		dialog: '',
		description: '',
		button: '',
		tickerSpin: 'GOOD LUCK',
	}),
	SURGE: mode('surge', 'activate', {
		title: 'SURGE SPIN',
		dialog:
			'Every spin costs 3x the bet. Lantern scatters land more often, so every bonus triggers about six times as often as in the base game. SURGE SPIN stays active until you turn it off.',
		description: 'Bonuses trigger about six times as often.',
		button: 'ACTIVATE',
		tickerSpin: 'GOOD LUCK',
	}),
	BEAM: mode('beam', 'activate', {
		title: 'BEAM SPIN',
		dialog:
			'Every spin costs 20x the bet. Six cells start charged at x4 and the beam meter starts at 4. Bonuses cannot trigger in BEAM SPIN. Maximum win 2,500x. BEAM SPIN stays active until you turn it off.',
		description: 'Six cells start at x4 and the beam meter starts at 4. No bonus trigger.',
		button: 'ACTIVATE',
		tickerSpin: 'GOOD LUCK',
	}),
	BONUS: mode('bonus', 'buy', {
		title: "KEEPER'S WATCH",
		dialog:
			"Buy the KEEPER'S WATCH bonus for 100x the bet: 10 free spins, every cell starts charged, and charges last for the whole bonus.",
		description: '10 free spins. Every cell starts charged.',
		button: 'BUY',
		tickerSpin: 'BONUS BUY ACTIVATED',
	}),
	SUPER: mode('super', 'buy', {
		title: 'EYE OF THE STORM',
		dialog:
			'Buy the EYE OF THE STORM bonus for 300x the bet: 12 free spins and every cell starts at x2.',
		description: '12 free spins. Every cell starts at x2.',
		button: 'BUY',
		tickerSpin: 'BONUS BUY ACTIVATED',
	}),
	MYSTERY: mode('mystery', 'buy', {
		title: 'MYSTERY BUY',
		dialog:
			'Costs 170x the bet. 65% chance of no bonus (one ordinary spin), 25% chance of EYE OF THE STORM, 10% chance of THE DROWNED LIGHT (15 free spins, every cell starts at x4, multipliers up to x1024).',
		description: '65% no bonus, 25% EYE OF THE STORM, 10% THE DROWNED LIGHT.',
		button: 'BUY',
		tickerSpin: 'MYSTERY BUY ACTIVATED',
	}),
};
