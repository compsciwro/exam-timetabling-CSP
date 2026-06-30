# Builds a Graphviz DOT diagram from search tree node data.


import graphviz


# Visual constants 

NODE_FILL = {
    "success":   "#00897B",   # teal   
    "fail":      "#4527A0",   # indigo 
    "backtrack": "#0277BD",   # blue   
}
NODE_FONT_COLOR = "#cfe8ff"   # light blue text 
EDGE_COLOR      = "#2979ff"   # main dashboard blue accent
GRAPH_BG        = "transparent"   # Streamlit dark theme 


# Public API 

def build_graph(nodes, title="Search Tree", max_nodes=120):
    """
    Converts a list of tree node dicts into a Graphviz Digraph.

    Parameters
    ----------
    nodes     : list of dicts produced by TreeLogger.get_nodes() or loaded from JSON.
                Required keys per node: id, parent, exam, value, step, status, depth
    title     : string shown as the graph title/label
    max_nodes : safety cap — trees beyond this size are trimmed for readability.

    Returns
    -------
    graphviz.Digraph  — pass .source to st.graphviz_chart()
    """
    display_nodes = nodes[:max_nodes]
    trimmed = len(nodes) > max_nodes
    visible_ids = {n["id"] for n in display_nodes}

    dot = graphviz.Digraph(comment=title)
    dot.attr(
        rankdir="TB",
        bgcolor=GRAPH_BG,
        label=f"{title}{'  [first ' + str(max_nodes) + ' nodes shown]' if trimmed else ''}",
        labelloc="t",
        fontcolor="white",
        fontsize="13",
        fontname="Courier New",
    )
    dot.attr("node",
        shape="box",
        style="filled,rounded",
        fontname="Courier New",
        fontsize="9",
        fontcolor=NODE_FONT_COLOR,
        margin="0.15,0.08",
    )
    dot.attr("edge", color=EDGE_COLOR, arrowsize="0.7")

    for node in display_nodes:
        fill  = NODE_FILL.get(node["status"], "#555555")
        label = _make_label(node)
        dot.node(str(node["id"]), label=label, fillcolor=fill)

        if node["parent"] is not None and node["parent"] in visible_ids:
            dot.edge(str(node["parent"]), str(node["id"]))

    return dot


def build_legend():
    """
    Returns a small standalone Graphviz Digraph showing the colour legend.
    Render this separately below the main tree in the dashboard.
    """
    dot = graphviz.Digraph(comment="Legend")
    dot.attr(rankdir="LR", bgcolor=GRAPH_BG,
             label="Legend", labelloc="t",
             fontcolor="white", fontsize="11")
    dot.attr("node", shape="box", style="filled,rounded",
             fontname="Courier New", fontsize="9", fontcolor="white")

    dot.node("s", label="success\n(assignment accepted)", fillcolor=NODE_FILL["success"],  fontcolor=NODE_FONT_COLOR)
    dot.node("f", label="fail\n(constraint violated)",   fillcolor=NODE_FILL["fail"],     fontcolor=NODE_FONT_COLOR)
    dot.node("b", label="backtrack\n(later undone)",     fillcolor=NODE_FILL["backtrack"],fontcolor=NODE_FONT_COLOR)

    # Invisible edges to control layout order
    dot.edge("s", "f", style="invis")
    dot.edge("f", "b", style="invis")

    return dot


def get_divergence_info(nodes_basic, nodes_advanced):
    """
    Finds the first node where the two strategies differ — i.e. the first
    step where they choose a different exam or value.

    Returns a dict with keys: step, basic_exam, basic_value, advanced_exam,
    advanced_value, explanation. Returns None if no divergence found.
    """
    for i, (nb, na) in enumerate(zip(nodes_basic, nodes_advanced)):
        if nb["exam"] != na["exam"] or nb["value"] != na["value"]:
            return {
                "step":            i + 1,
                "basic_exam":      nb["exam"],
                "basic_value":     nb["value"],
                "basic_status":    nb["status"],
                "advanced_exam":   na["exam"],
                "advanced_value":  na["value"],
                "advanced_status": na["status"],
                "explanation": (
                    f"At step {i+1}, Simple Backtracking tries {nb['exam']} = {nb['value']} "
                    f"({nb['status']}), while MRV selects {na['exam']} = {na['value']} "
                    f"({na['status']}). MRV chose {na['exam']} because it had the fewest "
                    f"remaining valid domain values at that point in the search, making it "
                    f"the most constrained variable."
                ),
            }
    return None


# Private helpers 

def _make_label(node):
    """Formats a node's display label."""
    # value is stored as a string like "('T1', 'HallA')" 
    value_clean = (
        node["value"]
        .replace("(", "").replace(")", "").replace("'", "")
        .replace(", ", "\n")
    )
    return f"{node['exam']}\n{value_clean}\nstep {node['step']}"
