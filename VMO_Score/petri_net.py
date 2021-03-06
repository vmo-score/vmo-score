"""Module implementing the methods for the construction of a petri net from a
segmentation analysis."""

import collections
import utils
import json
import snakes.plugins
snakes.plugins.load(['tpn', 'gv'], 'snakes.nets', 'nets')


class ExpressionError(Exception):
    """Class representing an error raised during the conversion to Expressions.

    Attributes:
        arg (str): String representing the information of the error.
    """
    def __init__(self, arg):
        self.msg = arg


class PetriNet(object):
    """Class that represents a Petri Net"""

    def __init__(self, s=None, pnml=None):
        """Initialization of the Petri Net Class
        Args:
            s (Segmentation): Initial segmentation
            pnml (str): Path to a PNML file
        """
        if s is not None:
            self.from_segmentation(s)
        elif pnml is not None:
            self.from_pnml(pnml)
        else:
            self._pn = None
            self._data = None

    @property
    def pn(self):
        """Object representing the Petri Net model.

        Returns:
            PetriNet: the Petri net
        """
        return self._pn

    @property
    def data(self):
        """Dictionary representing the regions belonging to each place.

        Returns:
            dict: Dictionary where keys are petri net places and values are
            their segmentation regions
        """
        return self._data

    @property
    def initial_place(self):
        """Returns the initial place of the Petri Net

        Returns:
            str: id of the initial place
        """
        initial_place = (p.name for p in self._pn.place()
                         if len(p.pre) == 0).next()
        return str(initial_place)

    @property
    def final_place(self):
        """Returns the final place of the Petri Net.

        Returns:
            str: id of the final place
        """
        final_place = (p.name for p in self._pn.place()
                       if len(p.post) == 0).next()
        return str(final_place)

    def __repr__(self):
        return 'PetriNet({})'.format(self.pn)

    def __str__(self):
        return str(self.pn)

    def print_transitions(self):
        """Print the information of the transitions of a Petri Net

        Print the name, the minimum and maximum duration and the current time of
        all transitions of a Petri Net
        """
        print "\n".join(
            "{}[{},{}]={}".format(
                t, t.min_time, t.max_time, "#" if t.time is None else t.time)
            for t in sorted(self._pn.transition()))

    def from_segmentation(self, segmentation):
        """Build a Petri Net representing the segmentation of an audio file.

        Args:
            segmentation (Segmentation): Segmentation
        """

        # initialize Petri net
        pn = nets.PetriNet('petri-net')

        # Grouping section by labels
        seg_labels = []
        seg_intrlvs = []
        for l, i in segmentation:
            seg_labels.append(l)
            seg_intrlvs.append(i)

        # adding final and initial place
        ulabels = list(set(seg_labels))
        id_initial = len(ulabels)
        id_final = id_initial + 1
        ulabels.append(id_initial)
        ulabels.append(id_final)
        seg_labels.insert(0, id_initial)
        seg_labels.append(id_final)

        # Add places using the labels of the segmentation
        for id_node in ulabels:
            # tokens = group_intevals[id_node]
            tokens = []
            if id_node == id_initial:
                tokens = [nets.dot]
            pn.add_place(nets.Place(str(id_node), tokens))

        # Add transitions using the segmentation list
        transitions = list(set(zip(seg_labels, seg_labels[1:])))
        for (i, j) in transitions:
            if i == j:  # avoid loops with the same place
                continue
            name_trans = 't_{0}_{1}'.format(i, j)
            pn.add_transition(nets.Transition(name_trans))
            pn.add_input(str(i), name_trans, nets.Value(nets.dot))
            pn.add_output(str(j), name_trans, nets.Value(nets.dot))

        # Setting attributes
        self._pn = pn
        self._data = self._group_intervals(segmentation)

    @staticmethod
    def _group_intervals(segmentation):
        """Classify intervals depending on their labels.

        Function that takes the intervals generated by the segmentation and
        classifies them depending on the label in the segmentation.

        Args:
            segmentation (Segmentation): Segmentation

        Returns:
            dict: Dictionary with the the section identifier as keys and the
                  list of intervals belonging to the section as value
        """
        result_dict = collections.defaultdict(list)
        for label, intervals in segmentation:
            result_dict[label].append(intervals)
        return result_dict

    def output_png(self, filename):
        """Save the Petri Net as a PNG file

        Args:
            filename (str): String representing the path of the output file
        """
        self._pn.draw(filename)

    def to_json(self, filename):
        """Save the Petri Net to a json file readily by i-score

        Args:
            filename (str): String representing the output file
        """
        output = collections.defaultdict(list)

        # places
        places = []
        for place in self._pn.place():
            p = {'name': place.name,
                 'tokens': [str(token) for token in place],
                 'pre': [pre for pre in place.pre.keys()],
                 'post': [post for post in place.post.keys()],
                 'data': map(list, self.data.get(int(place.name), []))
                 }
            places.append(p)
        output['places'] = places

        # transitions
        transitions = []
        for transition in self._pn.transition():
            t = {'name': transition.name,
                 'guard': str(transition.guard),
                 'min_time': transition.min_time,
                 'max_time': transition.max_time,
                 'input': [{'place': p_pre.name, 'label': str(l)}
                           for (p_pre, l) in transition.input()],
                 'output': [{'place': p_post.name, 'label': str(l)}
                            for (p_post, l) in transition.output()]
                 }
            transitions.append(t)
        output['transitions'] = transitions

        # writing JSON data
        with open(filename, 'w') as f:
            json.dump(output, f, indent=4, separators=(',', ': '))

    def to_pnml(self, filename):
        """Save the Petri Net as a PNML file

        Args:
            filename (str): String representing the path of the output file
        """
        with open(filename+".xml", 'w') as f:
            f.write(nets.dumps(self.pn))

        utils.save_shelf(filename+'-info', 'info', self.data)

    def from_pnml(self, filepath):
        """Load a Petri Net from a PNML file

        Args:
            filepath (str): Path of the PNML file
        """
        self._pn = nets.loads(filepath+".xml", ['tpn', 'gv'])

        self._data = utils.load_shelve(filepath+'-info', 'info')

    @staticmethod
    def _str_to_expression(label):
        """Translate a condition into a transition expression

        Translate a string representing a condition into a valid expression for
        transitions

        Args:
            label (str): String representing the condition to be translated

        Returns:
            Expression: A valid transition expression

        Raises:
            ExpressionError: Error raised when the string does not correspond
                             to a valid condition
        """
        expr = label.split()

        if len(expr) == 1:  # it's a predicate
            return nets.Expression(label)
        elif len(expr) == 3:  # it's a binary condition
            address, op, value = expr
            expr_address = nets.Expression("a=='{}'".format(address))
            expr_value = nets.Expression("v {} {}".format(op, value))
            return expr_address & expr_value
        else:
            raise ExpressionError("Impossible to translate str into Expression")

    def update_transition(self, t_name, new_min, new_max, new_guard):
        """Update a timed transition of a Petri Net

        Update a timed transition with new minimum and maximum durations and a
        guard.

        Args:
            t_name (str): Name of the transition to be changed
            new_min (float): Minimum duration of the transition
            new_max (float): Maximum duration of the transition
            new_guard (Expression): Condition of the transition
        """

        tmp_name = t_name + "_bk"
        self._pn.rename_node(t_name, tmp_name)
        t = self._pn.transition(tmp_name)

        t_new = nets.Transition(t_name,
                                new_guard,
                                min_time=new_min,
                                max_time=new_max)

        self._pn.add_transition(t_new)

        # copy inputs of t
        for (p, l) in t.input():
            self._pn.add_input(p.name, t_name, l)
            # t_new.add_input(p, l)

        # copy outputs of t
        for (p, l) in t.output():
            self._pn.add_output(p.name, t_name, l)
            # t_new.add_output(p, l)

        self._pn.remove_transition(tmp_name)

    def update_from_config(self, filename):
        """Update a Petri Net with a configuration file

        Read a configuration file and update the transition parameters with the
        values specifies on it.

        Args:
            filename (str): String representing the path of the configuration
                            file
        """

        config_file = utils.load_configuration(filename)
        config = config_file['conditions']

        for t_conf in config:
            t_name = t_conf.get('transition', None)
            t_min = t_conf.get('time-min', None)
            t_max = t_conf.get('time-max', None)
            t_guard = t_conf.get('condition', None)

            # transition doesn't exist
            if not self._pn.has_transition(t_name):
                continue

            # there are no modifications
            t = self._pn.transition(t_name)
            if [t.min_time, t.max_time, str(t.guard)] == [t_min, t_max, t_guard]:
                continue

            self.update_transition(t_name,
                                   t_min,
                                   t_max,
                                   self._str_to_expression(t_guard))
