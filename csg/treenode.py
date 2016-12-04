

class TreeNode:
    def __init__(self, name):
        self._node_name = name
        self._nodes = []
        self._node_parent = None
        self._can_have_nodes = True

    def __str__(self):
        return 'TreeNode("%s")' % self._node_name

    def __repr__(self):
        return self.__str__()

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
    @property
    def can_have_nodes(self):
        return self._can_have_nodes

    def add_node(self, node):
        if not self._can_have_nodes:
            raise ValueError("Can not add nodes to %s" % repr(self))
        if not isinstance(node, TreeNode):
            raise TypeError("Can not add non-TreeNode object %s" % type(node))
        this_nodes = self.node_root.nodes_as_set()
        if node in this_nodes:
            raise ValueError("Can not add the same node twice: %s" % repr(node))
        if this_nodes & node.node_root.nodes_as_set():
            raise ValueError("Can not add the node because it's tree contains a mutual node")
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

    def render_node_tree(self, name_func=None):
        """
        Returns a multi-line string with the whole tree rendered in ascii
        :param name_func: An optional function called for each node to get it's textual representation
        If omitted, the node_name property is used.
        :return: str
        """
        #a = name_func(self)
        #print(a)
        return self._render_node_tree(prefix="", name_func=name_func)

    def _render_node_tree(self, prefix, name_func):
        s = "%s%s\n" % (prefix, name_func(self) if name_func else self.node_name)
        prefix = prefix.replace('-', ' ').replace('\\', ' ').replace('+', '|')
        for i in range(len(self.nodes)):
            if i+1 < len(self.nodes):
                subprefix = "%s+-" % prefix
            else:
                subprefix = "%s\\-" % prefix
            s += self.nodes[i]._render_node_tree(subprefix, name_func)
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

