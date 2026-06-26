# tree_logger.py
# Records search tree nodes emitted by the solver log_fn callbacks.
# Produces a structured tree (with parent links) that tree_visualiser.py
# can render as a Graphviz diagram.

import json
import os


class TreeLogger:
    """
    Captures log events from a solver's log_fn callback and builds
    a node list suitable for Graphviz rendering.

    Usage:
        logger = TreeLogger()
        result, steps = S_backtracking(exams, overlaps, log_fn=logger.log)
        logger.save("simple_backtracking", "full", result is not None, steps)
    """

    def __init__(self):
        self.nodes = []
        self._node_id = 0
        # Stack tracks the current "parent" node ID as we go deeper.
        # None means root level.
        self._parent_stack = [None]
        # Track the last exam assigned at each depth level so we can
        # pop the stack correctly on backtrack events.
        self._depth_exam = {}

    def log(self, event):
        """
        Called once per search step by the solver.
        event keys: exam, value, step, status
        status values: "success" | "fail" | "backtrack"
        """
        self._node_id += 1
        node = {
            "id":     self._node_id,
            "parent": self._parent_stack[-1],
            "exam":   event["exam"],
            "value":  event["value"],
            "step":   event["step"],
            "status": event["status"],
            "depth":  len(self._parent_stack) - 1,
        }
        self.nodes.append(node)

        if event["status"] == "success":
            # Going deeper — push this node as the new parent
            self._parent_stack.append(self._node_id)
            self._depth_exam[len(self._parent_stack) - 1] = event["exam"]

        elif event["status"] == "backtrack":
            # Returning up — pop back to the grandparent level
            if len(self._parent_stack) > 1:
                self._parent_stack.pop()

        # "fail" events stay at the same depth (sibling attempt)

    def reset(self):
        """Call this between runs if reusing the logger for multiple strategies."""
        self.nodes = []
        self._node_id = 0
        self._parent_stack = [None]
        self._depth_exam = {}

    def get_nodes(self):
        """Returns the node list without saving."""
        return self.nodes

    def save(self, strategy, instance, solved, total_steps,
             path="output/search_logs.json"):
        """
        Appends this run's tree data to search_logs.json.
        Multiple runs accumulate in the same file.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)

        payload = {
            "strategy":    strategy,
            "instance":    instance,
            "solved":      solved,
            "total_steps": total_steps,
            "nodes":       self.nodes,
        }

        # Load existing entries if the file exists, then append
        existing = []
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    existing = json.load(f)
            except (json.JSONDecodeError, ValueError):
                existing = []  # corrupted file — start fresh

        # Remove any previous entry for the same strategy + instance combo
        existing = [
            e for e in existing
            if not (e["strategy"] == strategy and e["instance"] == instance)
        ]
        existing.append(payload)

        with open(path, "w") as f:
            json.dump(existing, f, indent=2)

        print(f"[tree_logger] Saved {len(self.nodes)} nodes — {path}")
        print(f"              strategy={strategy}, instance={instance}, "
              f"solved={solved}, steps={total_steps}")
