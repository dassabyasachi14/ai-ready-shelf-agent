from langgraph.graph import StateGraph, START, END

from graph.state import DigitalShelfState
from graph.nodes.shelf_scanner import shelf_scanner_node
from graph.nodes.compliance_agent import compliance_agent_node
from graph.nodes.recovery_generator import recovery_generator_node


def build_graph():
    builder = StateGraph(DigitalShelfState)

    builder.add_node("shelf_scanner", shelf_scanner_node)
    builder.add_node("compliance_agent", compliance_agent_node)
    builder.add_node("recovery_generator", recovery_generator_node)

    builder.add_edge(START, "shelf_scanner")
    builder.add_edge("shelf_scanner", "compliance_agent")
    builder.add_edge("compliance_agent", "recovery_generator")
    builder.add_edge("recovery_generator", END)

    return builder.compile()


compiled_graph = build_graph()
