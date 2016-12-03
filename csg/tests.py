from unittest import TestCase
from treenode import TreeNode, TreeNodeVisitor

class TestTreeNode(TestCase):

    class NameVisitor(TreeNodeVisitor):
        def __init__(self):
            self.s = ""

        def visit(self, node):
            self.s += node.node_name + ", "

    def create_tree_1(self):
        """
        A
        +-B
        | +-C
        | \-D
        \-E
          +-F
          | \-G
          \-H
            \-I
              \-J
        :return: TreeNode A
        """
        a = TreeNode("A")
        b = TreeNode("B")
        c = TreeNode("C")
        d = TreeNode("D")
        e = TreeNode("E")
        f = TreeNode("F")
        g = TreeNode("G")
        h = TreeNode("H")
        i = TreeNode("I")
        j = TreeNode("J")
        a.add_node(b)
        a.add_node(e)
        b.add_node(c)
        b.add_node(d)
        e.add_node(f)
        e.add_node(h)
        f.add_node(g)
        h.add_node(i)
        i.add_node(j)
        return a

    def create_tree_2(self):
        """
        A
        +-B
        | +-C
        | \-D
        |   +-K
        |   \-L
        |     \-M
        \-E
          +-F
          | \-G
          \-H
            \-I
              \-J
        :return: TreeNode A
        """
        a = TreeNode("A")
        b = TreeNode("B")
        c = TreeNode("C")
        d = TreeNode("D")
        e = TreeNode("E")
        f = TreeNode("F")
        g = TreeNode("G")
        h = TreeNode("H")
        i = TreeNode("I")
        j = TreeNode("J")
        k = TreeNode("K")
        l = TreeNode("L")
        m = TreeNode("M")
        a.add_node(b)
        a.add_node(e)
        b.add_node(c)
        b.add_node(d)
        d.add_node(k)
        d.add_node(l)
        l.add_node(m)
        e.add_node(f)
        e.add_node(h)
        f.add_node(g)
        h.add_node(i)
        i.add_node(j)
        return a

    def test_render_node_tree(self):
        a = self.create_tree_1()
        b = self.create_tree_2()
        a_str = """A
+-B
| +-C
| \-D
\-E
  +-F
  | \-G
  \-H
    \-I
      \-J
"""
        b_str = """A
+-B
| +-C
| \-D
|   +-K
|   \-L
|     \-M
\-E
  +-F
  | \-G
  \-H
    \-I
      \-J
"""
        self.assertEqual(a.render_node_tree(), a_str)
        self.assertEqual(b.render_node_tree(), b_str)


    def test_traversal_depth_first(self):
        v = self.NameVisitor()
        v.traverse_depth_first(self.create_tree_1())
        self.assertEqual("C, D, B, G, F, J, I, H, E, A, ", v.s)

        v = self.NameVisitor()
        v.traverse_depth_first(self.create_tree_2())
        self.assertEqual("C, K, M, L, D, B, G, F, J, I, H, E, A, ", v.s)

    def test_traversal_breath_first(self):
        v = self.NameVisitor()
        v.traverse_breath_first(self.create_tree_1())
        self.assertEqual("A, B, E, C, D, F, H, G, I, J, ", v.s)

        v = self.NameVisitor()
        v.traverse_breath_first(self.create_tree_2())
        self.assertEqual("A, B, E, C, D, K, L, M, F, H, G, I, J, ", v.s)

    def test_traversal(self):
        v = self.NameVisitor()
        v.traverse(self.create_tree_1())
        self.assertEqual("A, B, E, C, D, F, H, G, I, J, ", v.s)

        v = self.NameVisitor()
        v.traverse(self.create_tree_2())
        self.assertEqual("A, B, E, C, D, F, H, K, L, G, I, M, J, ", v.s)

    def test_traversal_reverse(self):
        v = self.NameVisitor()
        v.traverse_reverse(self.create_tree_1())
        self.assertEqual("J, I, G, H, F, D, C, E, B, A, ", v.s)

        v = self.NameVisitor()
        v.traverse_reverse(self.create_tree_2())
        self.assertEqual("J, M, I, G, L, K, H, F, D, C, E, B, A, ", v.s)
