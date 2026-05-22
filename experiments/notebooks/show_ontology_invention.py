import sys
import os
import numpy as np

# Ensure the cdfd_runtime module can be imported from the current repo layout.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'cdfd_runtime'))

from discovery.causal_discovery import CausalDiscoveryEngine
from ontology.engine import CDFLOntologyEngine

def run_demo():
    print("=====================================================")
    print("   CDFD Runtime: Autonomous Ontology Invention Demo  ")
    print("=====================================================\n")

    # 1. Synthesize some time series data (A -> B -> C)
    # A is an independent driver (e.g., external flux)
    # B is driven by A
    # C is driven by B
    print("[1] Simulating 3-Node System (True Causal Chain: A -> B -> C)")
    np.random.seed(42)
    n_steps = 500
    A = np.sin(np.linspace(0, 10, n_steps)) + np.random.normal(0, 0.1, n_steps)
    B = 0.8 * A + np.random.normal(0, 0.1, n_steps)
    C = 0.8 * B + np.random.normal(0, 0.1, n_steps)

    time_series = {"Node_A": A, "Node_B": B, "Node_C": C}

    # 2. Run Causal Discovery (PC Algorithm)
    print("\n[2] Running Peter-Clark (PC) Algorithm for Causal Discovery...")
    discovery = CausalDiscoveryEngine(significance_level=0.1)
    cpdag, nodes = discovery.pc_algorithm(time_series)
    
    print("\nDiscovered Causal Adjacency Matrix (Row -> Col):")
    print(f"Nodes: {nodes}")
    print(cpdag)
    print("Notice how the spurious correlation (A to C) is eliminated by conditioning on B!")

    # 3. Do-Calculus Intervention
    print("\n[3] Performing 'do-calculus' Graph Surgery: do(Node_B = x)")
    idx_B = nodes.index("Node_B")
    intervened_graph = discovery.do_intervention(cpdag, target_idx=idx_B)
    print("Post-Intervention Matrix:")
    print(intervened_graph)
    print("All incoming causal arrows to Node_B have been severed.")

    # 4. Schema Evolution / Invention
    print("\n[4] Triggering Autonomous Schema Evolution...")
    # Simulate a history where Psi_s was constantly overloaded (Anomaly)
    mock_history = [{"mean_psi_s": 2.5 + np.random.normal(0, 0.2)} for _ in range(100)]
    
    invented_schemas = discovery.propose_schema_evolution(mock_history, psi_threshold=1.5, novelty_limit=50.0)
    
    if invented_schemas:
        new_id, new_process_class = invented_schemas[0]
        print(f"   -> SUCCESS: Engine invented new semantic schema '{new_id}'")
        
        # 5. Dynamic Registration
        print("\n[5] Injecting invented schema into CDFLOntologyEngine registry...")
        CDFLOntologyEngine.register_discovered_type(new_id, new_process_class)
        
        engine = CDFLOntologyEngine()
        
        # 6. Evaluation using the new "invented" language
        print("\n[6] Evaluating state using the autonomously invented ontology...")
        label = engine.evaluate_semantic_node(domain_key=new_id, node_id="Anomaly_Region_1", phi=150.0, c=20.0)
        print("   Result:", label)
    else:
        print("   -> No new schemas invented (Novelty score too low).")

    print("\n=====================================================")
    print("                    DEMO COMPLETE                    ")
    print("=====================================================")

if __name__ == "__main__":
    run_demo()
