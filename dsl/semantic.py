from dsl.ast_nodes import DefineNode, PatientNode, ScenarioNode, SetNode


class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.symbols = {}
        self.domain = None

    def analyze(self, ast):
        errors = []
        for node in ast:
            try:
                self._visit(node)
            except SemanticError as e:
                errors.append(str(e))
        return errors

    def _visit(self, node):
        if isinstance(node, DefineNode):
            self.symbols[node.name] = node.type

        elif isinstance(node, SetNode):
            if node.key == "domain":
                self.domain = node.value

        elif isinstance(node, PatientNode):
            self.symbols[node.name] = "Patient"

        elif isinstance(node, ScenarioNode):
            for step in node.steps:
                self._visit(step)
