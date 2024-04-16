import logging 

def print_tree(g, root, msg="", markerStr="+- ", levelMarkers=[], seen=[]):
    """
    Recursive function that prints the hierarchical structure of a tree including markers that indicate
    parent-child relationships between nodes.

    Parameters:
    - g: igraph graph instance
    - root: Node instance, possibly containing children Nodes
    - markerStr: String to print in front of each node  ("+- " by default)
    - levelMarkers: Internally used by recursion to indicate where to
                    print markers and connections (see explanations below)

    Example output:

    1
    +- 1.1
    |  +- 1.1.1
    |  |  +- 1.1.1.1
    |  |  +- 1.1.1.2
    |  +- 1.1.2
    |  |  +- 1.1.2.1
    |  |  +- 1.1.2.2
    |  |  +- 1.1.2.3
    |  |     +- 1.1.2.3.1
    |  +- 1.1.3
    +- 1.2
    |  +- 1.2.1
    |  +- 1.2.2
    +- 1.3
    +- 1.4
       +- 1.4.1
       +- 1.4.2
    """

    # Printed in front of nodes when there should be no connection or marker
    # See for example nodes 1.1.2.3.1, 1.4.1 and 1.4.2 above
    emptyStr = " " * len(markerStr)

    # Printed in front of nodes that are connected by a parent that is
    # not the direct parent.
    # See for example nodes 1.2.1 and 1.2.2. The "|  " in front of them
    # indicates that their parent 1.2 has a sibling (1.3) and they are
    # connected. This string is NOT drawn for the last child of a node.
    # For example, node 1.4 is the last child of node 1 and it has two
    # children (1.4.1 and 1.4.2). Drawing the connection string in front
    # of 1.4.1 and 1.4.2 would be wrong as it would indicate that there
    # is another child of node 1 coming after 1.4.2.
    connectionStr = "|" + emptyStr[:-1]

    level = len(levelMarkers)  # recursion level
    # levelMarkers indicates for each level if the empty string or the
    # connection string should be printed. The last element of levelMarkers
    # is ignored in this recursion step because we know that a new
    # node has to be drawn (root). The last levelMarker will be used in
    # deeper recursions.
    mapper = lambda draw: connectionStr if draw else emptyStr
    markers = "".join(map(mapper, levelMarkers[:-1]))
    markers += markerStr if level > 0 else ""
    # print(f"{markers}{g.vs[root]['name']}")
    msg = msg + f"{markers}{g.vs[root]['name']} {g.vs[root]['team']}\n"

    # After root has been printed, recurse down (depth-first) the child nodes.
    for i, child in enumerate(g.neighbors(root, mode="in")):
        # print(i, child)
        # The last child will not need connection markers on the current level
        # (see example above)
        if child == root:
            continue
        isLast = i == len(g.neighbors(root, mode="in")) - 1
        msg = print_tree(g, child, msg, markerStr, [*levelMarkers, not isLast])

    return msg


def print_msg_box(msg, indent=1, width=None, title=None):
    """Print message-box with optional title."""
    lines = msg.split("\n")
    space = " " * indent
    if not width:
        width = max(map(len, lines))
    box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border
    if title:
        box += f"║{space}{title:<{width}}{space}║\n"  # title
        box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
    box += "".join([f"║{space}{line:<{width}}{space}║\n" for line in lines])
    box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
    print(box)
