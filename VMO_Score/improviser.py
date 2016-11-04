from random import randint
import utils
import copy
from collections import defaultdict
import snakes.plugins
snakes.plugins.load('tpn', 'snakes.nets', 'nets')


class Improviser():
    """Class representing the off-line improviser"""
    time_unit = 1.0

    def __init__(self, pn, path_conf):
        self.__pn = copy.deepcopy(pn)
        configuration = utils.load_configuration(path_conf)
        self.__actions = self._get_actions(configuration)
        self.__pn.update_from_config(path_conf)
        self._add_environment_pn()
        self.restart()

    @property
    def pn(self):
        """PetriNet: the Petri net for improvisation"""
        return self.__pn

    @property
    def current_time(self):
        """float: the amount of time that has elapsed"""
        return self.__current_time

    def _get_actions(self, conf):
        """Return the user actions from the configuration file
        Args:

        """
        actions = conf['actions']
        new = defaultdict(list)
        for a in actions:
            new[a['time']].append(a)
        return new

    def _add_environment_pn(self):
        """Add the environment to a Petri Net

        Add a new place in a Petri net that denotes the interaction with the
        environment. This new place has arcs to transitions whose guards
        depends on values send by the environment.
        """
        pn = self.pn.pn
        pn.add_place(nets.Place('env', []))

        for t in pn.transition():
            if (t.guard != nets.Expression('True')):  # It's different to True
                pn.add_input('env',
                             t.name,
                             nets.Tuple((nets.Variable('a'),
                             nets.Variable('v'))))
                if t.max_time is not None:
                    t1_name = t.name + "_default"
                    pn.add_transition(nets.Transition(t1_name,
                                                      min_time=t.max_time,
                                                      max_time=t.max_time))
                    for (p, l) in t.input():
                        if p.name != 'env':
                            pn.add_input(p.name, t1_name, nets.Value(nets.dot))

                    for (p, l) in t.output():
                        pn.add_output(p.name, t1_name, nets.Value(nets.dot))

    def add_action(self, addr, value):
        """Add a user action to the Petri Net.

        Add a new token to the place that represents the actions sent by the
        environment,

        Args:
            addr (str): String representing the OSC address of the message
            value (str): String representing the OSC value of the message
        """
        if self.pn.pn.has_place('env'):
            place_env = self.pn.pn.place('env')
            place_env.add([(addr, value)])

    def delete_action(self, addr, value):
        """Remove a user action from the Petri Net

        Remove a token from the place that represents the actions sent by the
        environment.

        Args:
            addr (str): String representing the OSC address of the message
            value (str): String representing the OSC value of the message
        """
        if self.pn.pn.has_place('env'):
            place_env = self.pn.pn.place('env')
            place_env.remove([(addr, value)])

    def get_enabled_transitions(self):
        """Enabled transitions

        Return a list of enabled transitions with the current marking
        """
        return [t.name for t in self.pn.pn.transition()
                if len(t.modes()) > 0 and t.enabled(t.modes()[0])]

    def restart(self):
        """Restart to the initial marking of the Petri Net"""
        self.pn.pn.reset()
        self.current_time = 0.0

    def next_time_unit(self):
        """Increment the global clock and the transition time by one time-unit"""
        step = self.pn.pn.step()
        self.current_time += self.time_unit
        for trans in self.pn.pn.transition():
            if (step is None) or (step > 0.0):
                if trans.time is not None:
                    trans.time += self.time_unit
            else:
                if trans.time == trans.max_time:
                    trans.time = None

    def fire_transition(self, t_name):
        """Fire a transition

        Take randomly a mode of an enabled transition and fire it

        Args:
            t_name (str): Name of the transition to be fired
        """
        t = self.pn.pn.transition(t_name)
        modes = t.modes()
        n_modes = len(modes)
        if n_modes > 0:
            m = modes[randint(0, n_modes - 1)]
            print "Mode selected was ->", m
            t.fire(m)

    def make_step(self):
        """Make a step in a Petri Net

        Take a logical step in the Petri Net. That is, an enabled transition is
        taken randomly and then it is fired.
        """
        enabled_t = self.get_enabled_transitions()
        n_t = len(enabled_t)
        if n_t > 0:
            t = enabled_t[randint(0, n_t - 1)]
            print "Firing Transiion ->", t
            self.fire_transition(t)

    def is_final_marking(self):
        """Return if the current state of the Petri Net is a final state

        Returns:
            bool: The Petri Net is in a final state
        """
        return (self.pn.final_place in self.pn.pn.get_marking().keys())
