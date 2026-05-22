from dsl.lexer import tokenize
from dsl.parser import parse
from dsl.semantic import SemanticAnalyzer
from dsl.graph import build_graph
from dsl.scheduler import schedule
from dsl.executor import Executor


def run_dsl(code, nx=32, ny=32):
    tokens = tokenize(code)
    ast = parse(tokens)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    graph, _ = build_graph(ast)
    ordered = schedule(graph)
    executor = Executor(nx=nx, ny=ny)
    return executor.execute(ordered)
