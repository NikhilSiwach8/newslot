"""Infernal Kingdom optimizer targets.

The optimizer re-weights books so each mode returns exactly its RTP. Each criteria's RTP
share below must sum to the mode RTP (0.96). `hr` is "one in N bets"; a criteria with rtp
and hr has an average win of rtp * hr * cost (base-bet multiples).

Base-game targets (both pacts), chosen from natural-play measurements (reports/):
    Hellfire Spins   1 in 370    avg ~74x   rtp 0.200
    Demon's Covenant 1 in 3,500  avg ~245x  rtp 0.070
    Abyssal Descent  1 in 14,000 avg ~350x  rtp 0.025
    The Soul Furnace 1 in 60,000 avg ~540x  rtp 0.009
    66,666x max win  1 in ~8.3M             rtp 0.008  (Stake asks for better than 1 in 10M)
    base game wins                          rtp 0.648
Targets sit close to the natural split (base game ~0.67 natural) so the optimizer does not
have to cut whole win ranges to hit the RTP.
Buy modes: max win rtp 0.004, the bonus itself 0.956.
"""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    verify_optimization_input,
)


def _parameters(test_spins, test_weights):
    return ConstructParameters(
        num_show=5000, num_per_fence=10000, min_m2m=4, max_m2m=8, pmb_rtp=1.0, sim_trials=5000,
        test_spins=test_spins, test_weights=test_weights, score_type="rtp",
    ).return_dict()


class OptimizationSetup:
    """Attach optimizer conditions for every bet mode to the game config."""

    def __init__(self, game_config):
        self.game_config = game_config
        cap = game_config.wincap

        def wincap(rtp):
            return ConstructConditions(rtp=rtp, av_win=cap, search_conditions=cap).return_dict()

        zero = ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict()
        no_scaling = ConstructScaling([]).return_dict()
        spin_params = _parameters([50, 100, 200], [0.3, 0.4, 0.3])
        buy_params = _parameters([10, 20, 50], [0.6, 0.2, 0.2])

        def base_targets():
            return {
                "conditions": {
                    "wincap": wincap(0.008),
                    "furnace": ConstructConditions(rtp=0.009, hr=60000, search_conditions={"bonus": "furnace"}).return_dict(),
                    "abyssal": ConstructConditions(rtp=0.025, hr=14000, search_conditions={"bonus": "abyssal"}).return_dict(),
                    "covenant": ConstructConditions(rtp=0.070, hr=3500, search_conditions={"bonus": "covenant"}).return_dict(),
                    "hellfire": ConstructConditions(rtp=0.200, hr=370, search_conditions={"bonus": "hellfire"}).return_dict(),
                    "0": zero,
                    "basegame": ConstructConditions(rtp=0.648, hr=2.6).return_dict(),
                },
                "scaling": no_scaling,
                "parameters": spin_params,
            }

        def buy_targets(tier):
            return {
                "conditions": {
                    "wincap": wincap(0.004),
                    tier: ConstructConditions(rtp=0.956, hr="x").return_dict(),
                },
                "scaling": no_scaling,
                "parameters": buy_params,
            }

        self.game_config.opt_params = {"base": base_targets(), "base_soul": base_targets()}
        for bm in game_config.bet_modes:
            if bm.get_buybonus():
                tier = [d.get_criteria() for d in bm.get_distributions() if d.get_criteria() != "wincap"][0]
                self.game_config.opt_params[bm.get_name()] = buy_targets(tier)

        verify_optimization_input(self.game_config, self.game_config.opt_params)
