import functools
import math


class LinkDirection:
    UNIDIRECTIONAL = 1
    BIDIRECTIONAL = 2


class NetworkNode:
    def __init__(self, label, activation=0, parent_type=None, long_desc=None):
        self.activation = activation
        self.label = label
        self.long_desc = long_desc if long_desc else label

        self.links = []
        self.codelets = []
        self.child_codelets = []
        self.parent = parent_type

        if parent_type is not None:
            inherit = NetworkLink(self, parent_type, LinkDirection.UNIDIRECTIONAL, relationship="inherits")
            self.add_link(inherit)
            parent_type.add_link(NetworkLink(parent_type, self, LinkDirection.UNIDIRECTIONAL, relationship="subtype"))

    def __str__(self):
        return self.label

    def link_str(self):
        return str(list(map(lambda x: x.node2.label + "(" + str(x.relationship) + ")", self.links)))

    def add_codelet(self, codelet, children_only=False):
        """
        These are the codelets that are likely to execute when this node is activated
        """
        if children_only:
            self.child_codelets.append(codelet)
        else:
            self.codelets.append(codelet)

    def add_link(self, link):
        self.links.append(link)
        if link.direction == LinkDirection.BIDIRECTIONAL:
            # TODO: This seems fragile, as we may add new fields
            link.node2.links.append(NetworkLink(link.node2, self, relationship=link.relationship, weight=link.weight))

    def links(self):
        return self.links

    def find_links(self, relationship):
        """
        Find all nodes with the given link label from this one
        :param relationship:
        :return:
        """
        return [l for l in self.links if str(l.relationship) == str(relationship)]

    def has_link_to(self, label, relationship=None):
        """
        Return True if there is a link (optionally of a specific relationship) to a node with the given label
        :param label:
        :param relationship:
        :return:
        """
        if relationship:
            links = self.find_links(relationship)
        else:
            links = self.links

        # TODO: Switch to proper python filter type thing
        for l in links:
            if l.node2.label == label:
                return True
        return False

    def all_codelets(self):
        returned = []
        returned.extend(self.codelets)
        if self.parent and len(self.parent.child_codelets) > 0:
            returned.extend(self.parent.child_codelets)

        return returned

    def activate(self, level=4, visited=[], depth=0):
        """
        Activating a node will increase the activation level of this node
        as well as some links. Additionally, it may optionally return a list of
        codelets that should also get activated
        TODO: the activation energy of a node should decay over time
        """
        if self in visited:
            return []

        visited.append(self)

        self.activation += level
        # print(('\t' * depth) + "[" + self.long_desc + "]: ACTIVATION@" + str(level) + "->" + str(self.activation))

        # TODO: Use a better stepping formula here
        sub_act = math.floor(level / 2)

        returned_codelets = []
        if self.activation > 3 and len(self.all_codelets()) > 0:
            #print "\t Activating codelets"
            for c in self.all_codelets():
                returned_codelets.append(functools.partial(c, target_node=self))

        if sub_act > 0:
            for l in self.links:
                end = l.node2
                if str(l.relationship) is not "requires":
                    # The activation of a relationship temporarily increases
                    # the weight of that link for carrying the activation
                    # energy.
                    # TODO: How best to implement that?
                    if type(l.relationship) is not str and l.relationship not in visited:
                        l.relationship.activate(level=sub_act, visited=visited, depth=depth + 1)
                    if end not in visited:
                        returned_codelets.extend(end.activate(level=sub_act, visited=visited, depth=depth + 1))
        return returned_codelets


class NetworkLink:
    def __init__(self, node1, node2, direction=LinkDirection.BIDIRECTIONAL, weight=1, relationship=None):
        self.node1 = node1
        self.node2 = node2
        self.direction = direction

        # the "relationship" is an option NetworkNode element 
        # which tell us the meaning of the link
        self.relationship = relationship

        self.weight = weight


class Network:
    def __init__(self):
        self.topNodes = dict()
        self.nodes = []

    def addNode(self, label, top=False):
        if type(label) is str:
            n = NetworkNode(label)
        else:
            n = label
        if top:
            self.topNodes[label] = n
        self.nodes.append(n)

        return n

    # add creae method?

    def getNode(self, label):
        if label in self.topNodes:
            return self.topNodes[label]
        else:
            return None

    def activate(self, label, level=10):
        node = self.getNode(label)
        if node is not None:
            return node.activate(level=level, visited=[])
        else:
            print("WARNING: Have no node [" + label + "] in network")

    def codelets(self):
        pass
