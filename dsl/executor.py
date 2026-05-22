from dsl.ast_nodes import (
    PatientNode, RunNode, ScenarioNode, ObserveNode,
    ModifyNode, ApplyNode, SetNode, DefineNode,
    AnalyzeNode, BifurcateNode, EmergeNode, AttractorNode, InfoFlowNode,
    VacuumNode, KnotNode, ResolveNode, SystemNode, RuleNode
)
from engine.state import State
from engine.kernel import Kernel
from engine.config import DEFAULT_NX, DEFAULT_NY, DEFAULT_DT
from ontology.actions.gateway import ActionGateway
from ontology.engine import CDFLOntologyEngine


class Executor:
    def __init__(self, nx=DEFAULT_NX, ny=DEFAULT_NY):
        self.nx = nx
        self.ny = ny
        self.context = {}
        self.results = []
        self.domain = None
        self.ontology = CDFLOntologyEngine()
        self.action_gateway = ActionGateway()

    def execute(self, ordered_nodes):
        for node in ordered_nodes:
            try:
                self._exec_node(node)
            except Exception as e:
                self.results.append({"error": str(e), "node": type(node).__name__})
        return self.results

    def _exec_node(self, node):
        if isinstance(node, SetNode):
            self.context[node.key] = node.value
            if node.key == "domain":
                self.domain = node.value

        elif isinstance(node, DefineNode):
            self.context[f"def_{node.name}"] = node.type

        elif isinstance(node, PatientNode):
            self.context[node.name] = dict(node.data)

        elif isinstance(node, ApplyNode):
            if node.target in self.context:
                self.context[node.target][f"condition_{node.condition}"] = True

        elif isinstance(node, ModifyNode):
            if node.target in self.context:
                self.context[node.target].update(node.data)

        elif isinstance(node, RunNode):
            result = self._run_engine(node.params)
            self.results.append({"type": "run", "result": result})

        elif isinstance(node, ScenarioNode):
            saved = {k: dict(v) if isinstance(v, dict) else v
                     for k, v in self.context.items()}
            for step in node.steps:
                self._exec_node(step)
            scenario_results = list(self.results)
            self.context.update(saved)
            self.results.append({"type": "scenario", "name": node.name,
                                  "results": scenario_results})

        elif isinstance(node, ObserveNode):
            self.results.append({"type": "observe", "data": self._observe(node.metrics)})

        elif isinstance(node, AnalyzeNode):
            self.results.append({"type": "analyze", "data": self._analyze(node.params)})

        elif isinstance(node, BifurcateNode):
            self.results.append({"type": "bifurcate", "data": self._bifurcate(node.params)})

        elif isinstance(node, EmergeNode):
            self.results.append({"type": "emerge", "data": self._emerge(node.params)})

        elif isinstance(node, AttractorNode):
            self.results.append({"type": "attractor", "data": self._attractor(node.params)})

        elif isinstance(node, InfoFlowNode):
            self.results.append({"type": "infoflow", "data": self._infoflow(node.params)})

        elif isinstance(node, VacuumNode):
            from engine.quantum_vacuum import QuantumVacuum
            constants = node.constants
            m_e = float(constants.get("m_e", 0.51099895))
            alpha = float(constants.get("alpha", 1/137.035999177))
            self.context["vacuum"] = QuantumVacuum(m_e=m_e, alpha=alpha)
            self.results.append({"type": "vacuum_defined", "m_e": m_e, "alpha": alpha})

        elif isinstance(node, KnotNode):
            props = node.properties
            n = int(props.get("n", 3))
            self.context["_last_knot_n"] = n
            self.results.append({"type": "knot_spawned", "n": n})

        elif isinstance(node, ResolveNode):
            vacuum = self.context.get("vacuum")
            if not vacuum:
                from engine.quantum_vacuum import QuantumVacuum
                vacuum = QuantumVacuum()
                self.context["vacuum"] = vacuum

            n = self.context.get("_last_knot_n", 3)
            knot = vacuum.spawn_knot(n)
            eos_check = vacuum.verify_vacuum_eos(n)

            self.results.append({
                "type": "spectrum_resolved",
                "n": n,
                "theta_n_deg": knot["theta_n_deg"],
                "M_n": knot["M_n"],
                "masses": knot["masses"],
                "sum_masses": knot["sum_masses"],
                "predicted_sum": knot["predicted_sum"],
                "n_pos": knot["n_pos"],
                "n_neg": knot["n_neg"],
                "split_formula_neg": knot["split_formula_neg"],
                "eos_check": eos_check
            })

        elif isinstance(node, SystemNode):
            self._exec_system(node)

        elif isinstance(node, RuleNode):
            self._exec_rule(node)

    # ------------------------------------------------------------------ system / rule

    def _exec_system(self, node: SystemNode):
        """Resolve flux and constraint from context, compute Ψ, store on system."""
        ctx = self.context
        # pull scalar values — support direct numbers or named patient biomarkers
        def resolve(expr):
            if expr is None:
                return 1.0
            try:
                return float(expr)
            except (TypeError, ValueError):
                pass
            
            if "." in expr:
                patient_name, key = expr.split(".", 1)
                if patient_name in ctx and isinstance(ctx[patient_name], dict) and key in ctx[patient_name]:
                    try:
                        return float(ctx[patient_name][key])
                    except (TypeError, ValueError):
                        pass
            
            # search all patient/dict entries for the key
            matches = []
            for k, v in ctx.items():
                if isinstance(v, dict) and expr in v:
                    try:
                        matches.append(float(v[expr]))
                    except (TypeError, ValueError):
                        pass
            
            if len(matches) > 1:
                raise ValueError(f"Ambiguous variable resolution for '{expr}'. Multiple patients contain this key. Use 'PatientName.{expr}' to disambiguate.")
            elif len(matches) == 1:
                return matches[0]
                
            return 1.0

        phi = resolve(node.flux_expr)
        C   = resolve(node.constraint_expr)
        C   = max(C, 1e-9)
        psi = phi / C

        # get recommendation — domain-agnostic
        try:
            from webapp.ontology import recommend
            rec = recommend(psi, domain=ctx.get("domain", "generic"))
        except Exception:
            rec = {"state": "unknown", "actions": []}


        domain_key = self.domain if self.domain else "generic"
        try:
            semantic_label = self.ontology.evaluate_semantic_node(
                domain_key=domain_key,
                node_id=node.name,
                phi=phi,
                c=C,
                s=1.0,
                ms=1.0
            )
        except Exception as e:
            semantic_label = f"Ontology Error: {e}"
        entry = {
            "name": node.name,
            "phi": phi,
            "C": C,
            "psi": psi,
            "recommendation": rec,
            "semantic_regime": semantic_label,
        }
        ctx.setdefault("_systems", {})[node.name] = entry
        self.results.append({"type": "system", **entry})

    def _exec_rule(self, node: RuleNode):
        """Evaluate rule against any named system or last-run Ψ."""
        systems = self.context.get("_systems", {})
        last_state = self.context.get("_last_state")

        triggered = []
        for sys_name, sys_entry in systems.items():
            psi = sys_entry["psi"]
            if node.condition_psi and node.threshold is not None:
                if psi > node.threshold:
                    action_result = self.action_gateway.execute_action(node.action, sys_name, psi)
                    triggered.append({"system": sys_name, "psi": psi, "action": node.action, "gateway_result": action_result})

        # also check last engine state if no named systems
        if not triggered and last_state is not None and node.threshold is not None:
            psi = float(last_state.mean_psi())
            if psi > node.threshold:
                action_result = self.action_gateway.execute_action(node.action, "_engine", psi)
                triggered.append({"system": "_engine", "psi": psi, "action": node.action, "gateway_result": action_result})

        self.results.append({
            "type": "rule",
            "rule": node.name,
            "threshold": node.threshold,
            "triggered": triggered,
        })

    # ------------------------------------------------------------------ engine

    def _run_engine(self, params):
        steps = int(params.get("duration", 10) / params.get("dt", DEFAULT_DT))
        dt = float(params.get("dt", DEFAULT_DT))
        kernel = Kernel(dt=dt)
        state = State(nx=self.nx, ny=self.ny)
        self._apply_domain_mapping(state)
        history = kernel.run(state, steps=min(steps, 1000))
        self.context["_last_state"] = state
        self.context["_last_history"] = history
        return history

    def _apply_domain_mapping(self, state):
        if not self.domain:
            return
        try:
            from domains.registry import DomainRegistry
            registry = DomainRegistry.default()
            adapter = registry.get(self.domain)
            patient_data = next(
                (v for v in self.context.values() if isinstance(v, dict) and "eGFR" in v),
                None,
            )
            if patient_data:
                phi_val, c_val = adapter.map_to_engine(patient_data)
                state.phi[:] = phi_val
                state.C[:] = c_val
        except Exception:
            pass

    # ------------------------------------------------------------------ observe

    def _observe(self, metrics):
        state = self.context.get("_last_state")
        history = self.context.get("_last_history", [])
        obs = {}
        if state is not None:
            if "psi" in metrics:
                obs["psi"] = state.mean_psi()
            if "eGFR" in metrics:
                obs["eGFR"] = state.mean_psi() * self.context.get(
                    list(self.context.keys())[0], {}).get("eGFR", 35)
        obs["history_len"] = len(history)
        return obs

    # ------------------------------------------------------------------ analysis nodes

    def _analyze(self, params):
        state = self.context.get("_last_state")
        history = self.context.get("_last_history", [])
        result = {}
        try:
            from engine.emergence import emergence_report
            result["emergence"] = emergence_report(state) if state else {}
        except Exception as e:
            result["emergence_error"] = str(e)
        try:
            from engine.causal_graph import build_causal_graph
            cg = build_causal_graph(history)
            result["causal_graph"] = cg.summary()
        except Exception as e:
            result["causal_error"] = str(e)
        return result

    def _bifurcate(self, params):
        try:
            from engine.bifurcation import map_phase, regime_summary
            resolution = int(params.get("resolution", 5))
            steps = int(params.get("steps", 10))
            pm = map_phase(
                param_a_name=params.get("param_a", "alpha"),
                param_b_name=params.get("param_b", "beta"),
                resolution=resolution,
                steps=steps,
                nx=max(4, self.nx // 4),
                ny=max(4, self.ny // 4),
            )
            return {"summary": regime_summary(pm), "param_a": pm["param_a"],
                    "param_b": pm["param_b"], "resolution": resolution}
        except Exception as e:
            return {"error": str(e)}

    def _emerge(self, params):
        state = self.context.get("_last_state")
        if state is None:
            return {"error": "no simulation run yet"}
        try:
            from engine.emergence import emergence_report
            return emergence_report(state)
        except Exception as e:
            return {"error": str(e)}

    def _attractor(self, params):
        state = self.context.get("_last_state")
        if state is None:
            return {"error": "no simulation run yet"}
        try:
            from engine.attractor import attractor_report
            steps = int(params.get("steps", 30))
            return attractor_report(state, steps=steps)
        except Exception as e:
            return {"error": str(e)}

    def _infoflow(self, params):
        state = self.context.get("_last_state")
        if state is None:
            return {"error": "no simulation run yet"}
        try:
            from engine.information_flow import information_report
            return information_report(state)
        except Exception as e:
            return {"error": str(e)}
