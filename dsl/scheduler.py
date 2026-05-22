from dsl.ast_nodes import PatientNode, DefineNode, SetNode, ScenarioNode


_PRIORITY = {
    DefineNode: 0,
    SetNode: 1,
    PatientNode: 2,
    ScenarioNode: 10,
}


def schedule(graph):
    def priority(node):
        return _PRIORITY.get(type(node), 5)
    return sorted(graph.nodes, key=priority)
