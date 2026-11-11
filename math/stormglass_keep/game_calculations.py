"""Stormglass Keep cluster evaluation with charged-cell multipliers."""

from src.executables.executables import Executables
from src.calculations.cluster import Cluster


class GameCalculations(Executables):
    """Cluster wins are multiplied by the sum of the multipliers (2+) under the cluster."""

    def evaluate_clusters_with_grid(self, clusters: dict) -> dict:
        """Mark winning symbols to explode and return SDK-shaped win data."""
        return_data = {"totalWin": 0, "wins": []}
        paytable = self.config.paytable
        grid = self.position_multipliers
        for sym in clusters:
            for cluster in clusters[sym]:
                size = len(cluster)
                if (size, sym) not in paytable:
                    continue
                cluster_mult = 0
                for reel, row in cluster:
                    if grid[reel][row] >= 2:
                        cluster_mult += grid[reel][row]
                cluster_mult = max(cluster_mult, 1)
                sym_win = paytable[(size, sym)]
                win = sym_win * cluster_mult * self.global_multiplier
                positions = [{"reel": p[0], "row": p[1]} for p in cluster]
                central = Cluster.get_central_cluster_position(positions)
                return_data["wins"].append(
                    {
                        "symbol": sym,
                        "clusterSize": size,
                        "win": win,
                        "positions": positions,
                        "meta": {
                            "globalMult": self.global_multiplier,
                            "clusterMult": cluster_mult,
                            "winWithoutMult": sym_win,
                            "overlay": {"reel": central[0], "row": central[1]},
                        },
                    }
                )
                return_data["totalWin"] += win
                for reel, row in cluster:
                    self.board[reel][row].explode = True
        return return_data
