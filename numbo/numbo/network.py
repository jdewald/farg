import functools
import math

import numpy


class LinkDirection:
    UNIDIRECTIONAL = 1
    BIDIRECTIONAL = 2

class ActivationLevel:
    MAX = 10
    HIGH = 4
    MID = 2
    LOW = 1


def sigmoid(act_level):
    return 1.0 / (1.0 + numpy.exp(-act_level))


def shifted_sigmoid(act_level):
    return sigmoid(act_level - 2.0)

class NetworkNode:
    def __init__(self, label, activation=1, parent_type=None, long_desc=None, fixed=False):
        self.activation = activation
        self.fixed_activation = fixed
        self.label = label
        self.long_desc = long_desc if long_desc else label

        self.links = []
        self.codelets = []
        self.child_codelets = []
        self.parent = parent_type
        self.ga = None
        self.ga_added = False

        if parent_type is not None:
            inherit = NetworkLink(self, parent_type, LinkDirection.UNIDIRECTIONAL, relationship="inherits")
            self.add_link(inherit)
            # parent_type.add_link(NetworkLink(parent_type, self, LinkDirection.UNIDIRECTIONAL, relationship="subtype"))

    def __str__(self):
        return self.label

    def get_level(self):
        return shifted_sigmoid(self.activation)

    def add_ga(self, if_level=0.8):
        if self.get_level() >= if_level:
            if not self.ga_added:
                self.ga_added = True
                self.ga.add_node(self)

            if self.ga_added:
                self.ga.label_node(self, self.label)
                for l in self.links:
                    l.ga = self.ga
                    l.add_ga(from_node=self, if_level=if_level)

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
        if self.ga and not link.ga:
            link.ga = self.ga
            link.ga_added = False
        # if self.ga:
        #    link.add_ga(from_node=self, if_level=0)
        if link.direction == LinkDirection.BIDIRECTIONAL:
            bidi = NetworkLink(link.node2, self,
                               relationship=link.inverse if link.inverse else link.relationship,
                               weight=link.weight)
            # TODO: This seems fragile, as we may add new fields
            link.node2.links.append(bidi)
            if self.ga:
                bidi.ga = self.ga
                #    bidi.add_ga(from_node=link.node2, if_level=0)

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

    def activate(self, level=1, visited=None, depth=0):
        """
        Activating a node will increase the activation level of this node
        as well as some links. Additionally, it may optionally return a list of
        codelets that should also get activated
        TODO: the activation energy of a node should decay over time
        """
        if not visited:
            visited = []
        if self in visited:
            return []

        visited.append(self)

        if not self.fixed_activation:
            self.activation += level

        # if self.activation > ActivationLevel.HIGH:
        #    self.activation = ActivationLevel.HIGH

        sig = self.get_level()


        print(('\t' * depth) + "[" + self.long_desc + "]" + str(id(self)) + ": ACTIVATION@" + str(level) + "->" + str(
            self.activation) + "=" + str(sig))

        if sig > 0.5 and self.ga:
            # if self.activation >= ActivationLevel.LOW and self.ga:
            self.add_ga(if_level=0.7)
            self.ga.label_node(self, self.long_desc)
            # if depth == 0:
            if sig >= 0.8:
                self.ga.highlight_node(self)


        returned_codelets = []
        if self.get_level() >= 0.9 and len(self.all_codelets()) > 0:
            # TODO: How do we prevent this from deliverying codelets every time?
            self.ga.highlight_node(self)
            print "Yay, got codelets out of " + str(self)
            print "Urgency will be" + str(90 * self.get_level())
            for c in self.all_codelets():
                returned_codelets.append(
                    [functools.partial(c, target_node=self), math.ceil(90 * (self.get_level()))])

        # No matter what, we lose some as we propagate through
        sub_act = level - 1
        if sub_act > 0:
            for l in self.links:
                if l not in visited:
                    returned_codelets.extend(l.transmit(level=sub_act, visited=visited, depth=depth + 1))
                else:
                    print str(l) + "in visited"

        if self.ga and depth == 0:
            self.ga.next_step()
        return returned_codelets


class NetworkLink:
    def __init__(self, node1, node2, direction=LinkDirection.BIDIRECTIONAL, weight=1, relationship=None, inverse=None):
        self.node1 = node1
        self.node2 = node2
        self.direction = direction
        self.inverse = inverse

        # the "relationship" is an option NetworkNode element 
        # which tell us the meaning of the link
        self.relationship = relationship

        self.weight = weight
        self.ga = None
        self.ga_added = False

    def add_ga(self, from_node=None, if_level=3):
        assert from_node == self.node1
        if self.ga:
            if not self.node1.ga_added:
                self.node1.ga = self.ga
                self.node1.add_ga(if_level=if_level)
            if not self.node2.ga_added:
                self.node2.ga = self.ga
                self.node2.add_ga(if_level=if_level)
            if self.node2.ga_added and not self.ga_added:
                self.ga.add_edge(self.node1, self.node2)
                self.ga_added = True

    def transmit(self, level=1.0, depth=0, visited=None):
        """
        Probabilisticly transmit the activation
        :param level: source activation level
        :param depth: debugging level for how far we've travelled to get here
        :param visited: list of already visited nodes
        :return:
        """
        if not visited:
            visited = []
        if self in visited:
            return []
        visited.append(self)

        end = self.node2
        act_level = level

        returned_codelets = []

        # if str(self.relationship) is not "requires":
        # The activation of a relationship temporarily increases
        # the weight of that link for carrying the activation
        # energy.
        # TODO: How best to implement that?

        # if not type(self.relationship) is str:
        #    print(('\t' * depth) + str(self.relationship) + "[" + str(self.relationship.activation) + "]" + " transmitting " + str(level))
        # if type(
        #        self.relationship) is not str and self.relationship not in visited and not self.relationship.fixed_activation:
        #    returned_codelets.extend(self.relationship.activate(level=act_level, visited=visited, depth=depth + 1))
        if end not in visited:
            if str(self.relationship) in ["subtype", "inherits"]:
                act_level = level * 0.5
            else:
                act_level = level * self.relationship.get_level()
            if act_level > 0:
                print(('\t' * depth) + str(act_level) + "/" + str(level) + " via " + self.node1.label + "-" + str(
                    self.relationship) + "->" + self.node2.label)
                returned_codelets.extend(end.activate(level=act_level, visited=visited, depth=depth + 1))
        else:
            print "TRANSMIT: " + str(end) + " in visited"

        return returned_codelets


class Network:
    def __init__(self):
        self.topNodes = dict()
        self.nodes = []
        self.ga = None

    def addNode(self, label, top=False, activation=0, fixed=False):
        if type(label) is str:
            n = NetworkNode(label, activation=activation, fixed=fixed)
        else:
            n = label
        if top:
            self.topNodes[label] = n
        self.nodes.append(n)
        if self.ga:
            n.ga = self.ga

        return n

    # add creae method?

    def getNode(self, label, create=False):
        if label in self.topNodes:
            return self.topNodes[label]
        elif create:
            return self.addNode(label, top=True)
        else:
            return None

    def activate(self, label, level=10):
        node = self.getNode(label)
        if node is not None:
            if self.ga and not node.ga:
                node.ga = self.ga
                #self.ga.add_node(node)
            return node.activate(level=level, visited=[])
        else:
            print("WARNING: Have no node [" + label + "] in network")
            return []

    def codelets(self):
        pass

    def step_activation(self):
        for n in self.nodes:
            if not n.fixed_activation and n.activation > 0:
                n.activation -= 1
