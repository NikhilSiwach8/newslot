import type { EmitterEventBoard } from '../components/Board.svelte';
import type { EmitterEventBoardFrame } from '../components/BoardFrame.svelte';
import type { EmitterEventTumbleBoard } from '../components/TumbleBoard.svelte';
import type { EmitterEventTumbleWinAmount } from '../components/TumbleWinAmount.svelte';
import type { EmitterEventGlobalMultiplier } from '../components/GlobalMultiplier.svelte';
import type { EmitterEventFreeSpinIntro } from '../components/FreeSpinIntro.svelte';
import type { EmitterEventFreeSpinCounter } from '../components/FreeSpinCounter.svelte';
import type { EmitterEventFreeSpinOutro } from '../components/FreeSpinOutro.svelte';
import type { EmitterEventWin } from '../components/Win.svelte';
import type { EmitterEventSound } from '../components/Sound.svelte';
import type { EmitterEventTransition } from '../components/Transition.svelte';
import type { EmitterEventHellSeals } from '../components/HellSeals.svelte';
import type { EmitterEventSoulsMeter } from '../components/SoulsMeter.svelte';
import type { EmitterEventFeatureOverlay } from '../components/FeatureOverlay.svelte';

export type EmitterEventGame =
	| EmitterEventBoard
	| EmitterEventBoardFrame
	| EmitterEventTumbleBoard
	| EmitterEventTumbleWinAmount
	| EmitterEventGlobalMultiplier
	| EmitterEventWin
	| EmitterEventFreeSpinIntro
	| EmitterEventFreeSpinCounter
	| EmitterEventFreeSpinOutro
	| EmitterEventSound
	| EmitterEventTransition
	| EmitterEventHellSeals
	| EmitterEventSoulsMeter
	| EmitterEventFeatureOverlay;
