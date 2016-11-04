import sys
import os
sys.path.append("/Users/himito/Projects/oracle/vmo_i-score_generator/VMO_Score")
import generator as g
import improviser as impro
import snakes.plugins
snakes.plugins.load(['tpn', 'gv'], 'snakes.nets', 'nets')
from nets import Place, Transition, Variable, PetriNet


if not os.path.exists("petri-net.xml"):
    filepath = os.path.abspath("../..//misc/Berio - Flute.wav")
    ulabel, invind, est_intervals, cqt_vmo, times = g.segmentation_vmo(
        filepath)
    pn, pn_data = g.build_petri_net(ulabel.tolist(), invind.tolist(),
                                    est_intervals)

    g.save_oracle(cqt_vmo, "oracle")
    g.save_petri_net(pn, pn_data, "petri_net.json")
    g.print_petri_net(pn, "petri-net.png")
    g.save_pnml(pn, pn_data, "petri-net")
    g.print_segmentation(invind, est_intervals, "segmentation.png")
    g.generate_configuration(pn, "configuration.yml")

else:
    # load petri net
    pn, pn_data = g.load_pnml('petri-net')
    print "Petri Net Intervals:\n", pn_data, "\n------------------------------"

    # load oracle
    oracle = g.load_oracle("oracle")

    # Load configuration
    conf = g.load_configuration('configuration.yml')
    impro.update_petri_net(conf['conditions'], pn)
    # print "Petri Net Configuration:\n", conf['conditions']

    # test
    # impro.set_region(pn_data[0][0])

    # Offline improvisation
    impro.add_environment_pn(pn)

    pn.draw('pn-modified.png')

    # Start simulation
    pn.reset()
    clock = 0.0  # global clock

    # while (len(impro.get_enabled_transitions(pn)) > 0):
    #     delay = pn.time()
    #     if delay is None:
    #         delay = 0.0
    #     clock += delay

    #     print "Current Time ->", clock
    #     print "Current Marking -> ", pn.get_marking()
    #     impro.show_transitions(pn)
    #     print "Enabled Transitions -> ", impro.get_enabled_transitions(pn)
    #     impro.make_step(pn)

    #     print "-------------------------------------------------------------"
    #     u = raw_input("Do you want to continue [y/n]: ")
    #     if not(u in ['y', 'Y']):
    #         break

    # if (len(impro.get_enabled_transitions(pn)) == 0):
    #     print "****** DEADLOCK REACHED ******"
