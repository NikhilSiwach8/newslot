"""Stormglass Keep optimizer targets.

Each mode's criteria RTP shares must sum to the mode RTP (0.963).
`hr` is "one in N bets"; for a criteria with `rtp` and `hr` the average win in base-bet
multiples is rtp * hr * cost. Target bonus values used throughout:
    Keeper's Watch ~96x, Eye of the Storm ~289x, The Drowned Light ~810x.
These are first-pass targets and must be re-derived from simulation results.
"""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    verify_optimization_input,
)


def _parameters(test_spins, test_weights):
    return ConstructParameters(
        num_show=5000,
        num_per_fence=10000,
        min_m2m=4,
        max_m2m=8,
        pmb_rtp=1.0,
        sim_trials=5000,
        test_spins=test_spins,
        test_weights=test_weights,
        score_type="rtp",
    ).return_dict()


class OptimizationSetup:
    """Attach optimizer conditions for every bet mode to the game config."""

    def __init__(self, game_config):
        self.game_config = game_config
        wincaps = {bm.get_name(): bm.get_wincap() for bm in game_config.bet_modes}

        def wincap(mode, rtp):
            return ConstructConditions(
                rtp=rtp, av_win=wincaps[mode], search_conditions=wincaps[mode]
            ).return_dict()

        zero = ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict()
        no_scaling = ConstructScaling([]).return_dict()
        spin_params = _parameters([50, 100, 200], [0.3, 0.4, 0.3])
        buy_params = _parameters([10, 20, 50], [0.6, 0.2, 0.2])

        self.game_config.opt_params = {
            # 0.005 + 0.0135 + 0.095 + 0.24 + 0.6095 = 0.963
            "base": {
                "conditions": {
                    "wincap": wincap("base", 0.005),
                    "drowned": ConstructConditions(rtp=0.0135, hr=60000).return_dict(),
                    "eye": ConstructConditions(rtp=0.095, hr=3000).return_dict(),
                    "watch": ConstructConditions(rtp=0.24, hr=400).return_dict(),
                    "0": zero,
                    "basegame": ConstructConditions(rtp=0.6095, hr=3.6).return_dict(),
                },
                "scaling": no_scaling,
                "parameters": spin_params,
            },
            # Bonuses about 6.4x as frequent as base. 0.005 + 0.034 + 0.207 + 0.516 + 0.201 = 0.963
            "surge": {
                "conditions": {
                    "wincap": wincap("surge", 0.005),
                    "drowned": ConstructConditions(rtp=0.034, hr=7940).return_dict(),
                    "eye": ConstructConditions(rtp=0.207, hr=465).return_dict(),
                    "watch": ConstructConditions(rtp=0.516, hr=62).return_dict(),
                    "0": zero,
                    "basegame": ConstructConditions(rtp=0.201, hr=3.6).return_dict(),
                },
                "scaling": no_scaling,
                "parameters": spin_params,
            },
            # 0.003 + 0.96 = 0.963
            "beam": {
                "conditions": {
                    "wincap": wincap("beam", 0.003),
                    "0": zero,
                    "basegame": ConstructConditions(rtp=0.96, hr=1.25).return_dict(),
                },
                "scaling": no_scaling,
                "parameters": spin_params,
            },
            # 0.005 + 0.958 = 0.963
            "bonus": {
                "conditions": {
                    "wincap": wincap("bonus", 0.005),
                    "watch": ConstructConditions(rtp=0.958, hr="x").return_dict(),
                },
                "scaling": no_scaling,
                "parameters": buy_params,
            },
            # 0.01 + 0.953 = 0.963
            "super": {
                "conditions": {
                    "wincap": wincap("super", 0.01),
                    "eye": ConstructConditions(rtp=0.953, hr="x").return_dict(),
                },
                "scaling": no_scaling,
                "parameters": buy_params,
            },
            # Mystery Buy: 65% no bonus / 25% Eye of the Storm / 10% The Drowned Light.
            # 0.003 + 0.5055 + 0.452 + 0.0025 = 0.963
            "mystery": {
                "conditions": {
                    "wincap": wincap("mystery", 0.003),
                    "drowned": ConstructConditions(rtp=0.5055, hr=10).return_dict(),
                    "eye": ConstructConditions(rtp=0.452, hr=4).return_dict(),
                    # hr = av_win / (rtp * cost) = 0.615 / (0.0025 * 160) = 1.54, i.e. 65% of buys
                    "nobonus": ConstructConditions(rtp=0.0025, hr=1.5385).return_dict(),
                },
                "scaling": no_scaling,
                "parameters": buy_params,
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)
