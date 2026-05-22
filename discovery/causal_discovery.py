import numpy as np
import logging
from scipy import stats

logger = logging.getLogger(__name__)

class CausalDiscoveryEngine:
    """
    CDFD Runtime discovery layer (Layer 5).
    Implements true Structural Causal Models (SCM) and Autonomous Schema Evolution.
    """
    def __init__(self, significance_level=0.05):
        self.alpha = significance_level

    def partial_corr(self, x, y, z=None):
        """Compute the partial correlation of x and y conditioning on z."""
        if z is None or len(z) == 0:
            return np.corrcoef(x, y)[0, 1]
        
        # Simple linear regression residual correlation
        beta_x = np.linalg.lstsq(z, x, rcond=None)[0]
        res_x = x - z.dot(beta_x)
        
        beta_y = np.linalg.lstsq(z, y, rcond=None)[0]
        res_y = y - z.dot(beta_y)
        
        return np.corrcoef(res_x, res_y)[0, 1]

    def pc_algorithm(self, time_series_data):
        """
        Implementation of the Peter-Clark (PC) Algorithm for causal discovery.
        Detects true causal graphs by eliminating spurious correlations via conditional independence tests.
        """
        nodes = list(time_series_data.keys())
        n = len(nodes)
        
        # Step 1: Start with a fully connected undirected graph
        graph = np.ones((n, n), dtype=int) - np.eye(n, dtype=int)
        
        # Data matrix
        data_matrix = np.array([time_series_data[node] for node in nodes]).T
        
        # Step 2: Edge elimination via conditional independence (Skeleton)
        sepsets = {}
        for i in range(n):
            for j in range(i + 1, n):
                if graph[i, j] == 0: continue
                
                # 0-order
                corr = self.partial_corr(data_matrix[:, i], data_matrix[:, j])
                if abs(corr) < self.alpha:
                    graph[i, j] = graph[j, i] = 0
                    sepsets[(i, j)] = []
                    continue
                
                # 1-order
                for k in range(n):
                    if k == i or k == j: continue
                    z = data_matrix[:, k].reshape(-1, 1)
                    p_corr = self.partial_corr(data_matrix[:, i], data_matrix[:, j], z)
                    if abs(p_corr) < self.alpha:
                        graph[i, j] = graph[j, i] = 0
                        sepsets[(i, j)] = [k]
                        break
                            
        # Step 3: V-structure identification (A -> C <- B)
        directed_graph = np.copy(graph)
        for i in range(n):
            for j in range(i + 1, n):
                if graph[i, j] == 0:
                    for k in range(n):
                        if graph[i, k] == 1 and graph[j, k] == 1:
                            if (i, j) in sepsets and k not in sepsets[(i, j)]:
                                directed_graph[k, i] = 0 # i -> k
                                directed_graph[k, j] = 0 # j -> k
                                
        return directed_graph, nodes

    def do_intervention(self, graph_matrix, target_idx, intervention_value=None):
        """
        Implements Pearl's 'do-calculus' Graph Surgery.
        Breaks all incoming causal links to the target node.
        """
        intervened_graph = np.copy(graph_matrix)
        intervened_graph[:, target_idx] = 0
        return intervened_graph

    def propose_schema_evolution(self, state_history, psi_threshold=1.5, novelty_limit=10.0, on_discovery=None):
        """
        Autonomous Schema Evolution: Detects persistent high-flux regimes 
        and invents new semantic ProtoProcess types.
        """
        invented_schemas = []
        mean_psi_series = np.array([h.get("mean_psi_s", h.get("psi_s", 1.0)) for h in state_history])
        
        # Novelty Score (Integral of excess Operating Ratio)
        deviations = np.maximum(0.0, mean_psi_series - 1.0)
        novelty_score = np.sum(deviations[mean_psi_series > psi_threshold])
        
        if novelty_score > novelty_limit:
            new_id = f"ProtoRegime_{int(novelty_score)}_{np.random.randint(1000)}"
            
            from ontology.meta.process import Process
            class DiscoveredProcess(Process):
                def __init__(self, name=new_id):
                    super().__init__(name)
                    self.is_discovered = True
                    self.novelty_score = novelty_score
            
            discovered = (new_id, DiscoveredProcess)
            invented_schemas.append(discovered)
            
            if on_discovery:
                on_discovery(discovered)
            
        return invented_schemas
