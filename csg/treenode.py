

class TreeNode:
    def __init__(self, name):
        self._node_name = name
        self._nodes = []
        self._node_parent = None
        self._can_have_nodes = True

    def __repr__(self):
        return 'TreeNode("%s")' % self._node_name

    @property
    def node_name(self):
        return self._node_name
    @property
    def nodes(self):
        return self._nodes
    @property
    def node_parent(self):
        return self._node_parent
    @property
    def node_root(self):
        return self if not self._node_parent else self._node_parent.node_root

    def add_node(self, node):
        if not self._can_have_nodes:
            raise ValueError("Can not add nodes to %s" % repr(self))
        if not isinstance(node, TreeNode):
            raise TypeError("Can not add non-TreeNode object %s" % type(node))
        this_nodes = self.node_root.nodes_as_set()
        if node in this_nodes:
            raise ValueError("Can not add the same node twice: %s" % repr(node))
        if this_nodes & node.node_root.nodes_as_set():
            raise ValueError("Can not add the node because it contains a mutual node")
        self._nodes.append(node)
        node._node_parent = self

    def contains_node(self, node):
        if node in self._nodes:
            return True
        for o in self._nodes:
            if o.contains_node(node):
                return True
        return False

    def nodes_as_set(self):
        s = {self}
        for o in self._nodes:
            s |= o.nodes_as_set()
        return s

    def nodes_as_level_dict(self, level=0):
        d = {level: [self,]}
        for n in self.nodes:
            sub = n.nodes_as_level_dict(level+1)
            for l in sub.keys():
                if not l in d:
                    d[l] = sub[l]
                else:
                    d[l] += sub[l]
        return d

    def render_node_tree(self, prefix=""):
        s = "%s%s\n" % (prefix, self.node_name)
        prefix = prefix.replace('-', ' ').replace('\\', ' ').replace('+', '|')
        for i in range(len(self.nodes)):
            if i+1 < len(self.nodes):
                subprefix = "%s+-" % prefix
            else:
                subprefix = "%s\\-" % prefix
            s += self.nodes[i].render_node_tree(subprefix)
        return s


class TreeNodeVisitor:

    def traverse_depth_first(self, node):
        for n in node.nodes:
            self.traverse_depth_first(n)
        self.visit(node)

    def traverse_breath_first(self, node):
        self.visit(node)
        self._traverse_breath_first(node)

    def _traverse_breath_first(self, node):
        for n in node.nodes:
            self.visit(n)
        for n in node.nodes:
            self._traverse_breath_first(n)

    def traverse(self, node):
        d = node.nodes_as_level_dict()
        for lvl in d:
            for n in d[lvl]:
                self.visit(n)

    def traverse_reverse(self, node):
        d = node.nodes_as_level_dict()
        for lvl in reversed(list(d)):
            for n in reversed(d[lvl]):
                self.visit(n)

    def visit(self, node):
        raise NotImplementedError

