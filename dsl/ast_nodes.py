class Node:
    pass


class DefineNode(Node):
    def __init__(self, type_, name):
        self.type = type_
        self.name = name


class SetNode(Node):
    def __init__(self, key, value):
        self.key = key
        self.value = value


class PatientNode(Node):
    def __init__(self, name, data):
        self.name = name
        self.data = data


class ApplyNode(Node):
    def __init__(self, condition, target):
        self.condition = condition
        self.target = target


class ModifyNode(Node):
    def __init__(self, target, data):
        self.target = target
        self.data = data


class RunNode(Node):
    def __init__(self, params):
        self.params = params


class ScenarioNode(Node):
    def __init__(self, name, steps):
        self.name = name
        self.steps = steps


class ObserveNode(Node):
    def __init__(self, metrics):
        self.metrics = metrics


class SweepNode(Node):
    def __init__(self, param, values):
        self.param = param
        self.values = values


class DiscoverNode(Node):
    def __init__(self, params):
        self.params = params


class LinkNode(Node):
    def __init__(self, source, target):
        self.source = source
        self.target = target


class AnalyzeNode(Node):
    """ANALYZE {} — runs causal graph + emergence report on last state."""
    def __init__(self, params=None):
        self.params = params or {}


class BifurcateNode(Node):
    """BIFURCATE { param_a: alpha, param_b: beta, resolution: 6 }"""
    def __init__(self, params=None):
        self.params = params or {}


class EmergeNode(Node):
    """EMERGE {} — classifies field structures in current Ψ."""
    def __init__(self, params=None):
        self.params = params or {}


class AttractorNode(Node):
    """ATTRACTOR {} — detects fixed point / limit cycle / chaos."""
    def __init__(self, params=None):
        self.params = params or {}


class InfoFlowNode(Node):
    """INFOFLOW {} — entropy, mutual info, transfer entropy report."""
    def __init__(self, params=None):
        self.params = params or {}


class VacuumNode(Node):
    """DEFINE Vacuum { m_e: 0.51099, alpha: 0.007297 }"""
    def __init__(self, constants=None):
        self.constants = constants or {}


class KnotNode(Node):
    """SPAWN Knot { n: 5 }"""
    def __init__(self, properties=None):
        self.properties = properties or {}


class ResolveNode(Node):
    """RESOLVE Spectrum"""
    def __init__(self, target):
        self.target = target


class SystemNode(Node):
    """SYSTEM Name { flux: X constraint: Y state: psi = flux/constraint }"""
    def __init__(self, name, flux_expr, constraint_expr, state_expr):
        self.name = name
        self.flux_expr = flux_expr
        self.constraint_expr = constraint_expr
        self.state_expr = state_expr


class RuleNode(Node):
    """RULE Name { if psi > threshold action action_name }"""
    def __init__(self, name, condition_psi, threshold, action):
        self.name = name
        self.condition_psi = condition_psi   # e.g. "psi"
        self.threshold = threshold           # float
        self.action = action                 # e.g. "reduce_flux"
