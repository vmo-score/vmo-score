from petri_net import PetriNet
from improviser import Improviser

path = "/Users/himito/Dropbox/work_Shlomo/Cycles_2016/output-vmo-score/vmo-basset/"

imprv = Improviser(PetriNet(pnml=path+"petri-net"), path+'configuration.yml')

imprv.add_action('', 0)


def debug():
    print "------------------------------------------------------------------"
    print "Current time: {}".format(imprv.current_time)
    print "\nTransitions:"
    imprv.pn.print_transitions()
    print "\nMarking:\n{}".format(imprv.pn.pn.get_marking())
    print "\nEnabled transitions:\n{}".format(imprv.get_enabled_transitions())
    print "\nNext step: {}".format(imprv.pn.pn.step())
    imprv.pn.output_png('impro-pn.png')
    print "------------------------------------------------------------------"

while (raw_input('Continue [y/n]') == 'y' and not imprv.is_final_marking()):
    # imprv.add_action('/dev/sound',11)
    debug()
    imprv.make_step()
    imprv.next_time_unit()
