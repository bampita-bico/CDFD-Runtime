class ExecutionGraph:
    def __init__(self):
        self.nodes = []
        self.edges = {}

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, a, b):
        self.edges.setdefault(id(a), []).append(b)

    def dependencies(self, node):
        return self.edges.get(id(node), [])

    def topological_order(self):
        visited = set()
        order = []

        def visit(n):
            if id(n) in visited:
                return
            visited.add(id(n))
            for dep in self.dependencies(n):
                visit(dep)
            order.append(n)

        for n in self.nodes:
            visit(n)
        return order


def build_graph(ast):
    graph = ExecutionGraph()
    node_map = {}
    for node in ast:
        graph.add_node(node)
        node_map[getattr(node, "name", id(node))] = node
    return graph, node_map
