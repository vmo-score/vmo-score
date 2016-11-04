import Tkinter
import tkFileDialog
import tkMessageBox
import ttk
from PIL import Image

import matplotlib
matplotlib.use('TkAgg')

from segmentation import Segmentation
from petri_net import PetriNet
import utils


class GraphicalInterface(Tkinter.Tk):

    def initUI(self):
        # variables
        self.segmentation = None
        self.pn = None
        self.pn_prev = None
        self.petri_png_prev = "/tmp/pn-preview.png"

        # widgets
        nb = ttk.Notebook(self.parent, name='notebook')
        nb.pack(fill=Tkinter.BOTH, expand=Tkinter.Y)
        self._create_segmentation_tab(nb)
        self._create_petri_tab(nb)

        # options
        self.resizable(False, False)

    def _create_segmentation_tab(self, nb):
        frame = Tkinter.Frame(nb)

        # widgets for load audio file
        self.audio_path = Tkinter.StringVar()
        audio_path_entry = Tkinter.Entry(frame, textvariable=self.audio_path)
        audio_path_entry.grid(column=0, row=0, sticky='EW',
                              columnspan=3)
        audio_btn = Tkinter.Button(frame, text='Load', command=self.showDialog)
        audio_btn.grid(column=3, row=0, sticky='EW')

        self.output_path = Tkinter.StringVar()
        output_path_entry = Tkinter.Entry(frame, textvariable=self.output_path)
        output_path_entry.grid(column=0, row=1, sticky='EW',
                               columnspan=3)
        output_btn = Tkinter.Button(frame, text='Output',
                                    command=lambda: self.showDialogFolder(1))
        output_btn.grid(column=3, row=1, sticky='EW')

        # buttons for actions
        seg_btn = Tkinter.Button(frame, text='Segmentation',
                                 command=self.create_segmentation)
        seg_btn.grid(column=0, row=2)
        draw_seg_btn = Tkinter.Button(frame, text='View Segmentation',
                                      command=self.visualize_segmentation)
        draw_seg_btn.grid(column=1, row=2)
        pn_btn = Tkinter.Button(frame, text='Generate PN',
                                command=self.petri_net)
        pn_btn.grid(column=2, row=2)
        draw_pn_btn = Tkinter.Button(frame, text='View PN',
                                     command=self.visualize_petri_net)
        draw_pn_btn.grid(column=3, row=2)

        # add to notebook
        nb.add(frame, text='Segmentation')

    def _create_petri_tab(self, nb):
        frame = Tkinter.Frame(nb)

        for i in range(4):
            Tkinter.Grid.columnconfigure(frame, i, weight=1)

        # widget for looking for the petri net path
        self.pn_path = Tkinter.StringVar()
        pn_path_entry = Tkinter.Entry(frame, textvariable=self.pn_path)
        pn_path_entry.grid(column=0, row=0, sticky='EW', columnspan=3)
        pn_path_btn = Tkinter.Button(frame, text='Search',
                                     command=lambda: self.showDialogFolder(2))
        pn_path_btn.grid(column=3, row=0, sticky='EW')

        # button to load the petri net
        load_pn_btn = Tkinter.Button(frame, text='Load',
                                     command=self.load_petri_net)
        load_pn_btn.grid(column=0, row=1, sticky='EW')

        # button to update the petri net
        update_pn_btn = Tkinter.Button(frame, text='Update',
                                       command=self.update_petri_net)
        update_pn_btn.grid(column=1, row=1, sticky='EW')

        # show petri net
        show_pn_btn = Tkinter.Button(frame, text='Show',
                                     command=self.preview_petri_net)
        show_pn_btn.grid(column=2, row=1, sticky='EW')

        # save to update the petri net
        save_pn_btn = Tkinter.Button(frame, text='Save',
                                     command=self.save_petri_net)
        save_pn_btn.grid(column=3, row=1, sticky='EW')

        # add to notebook
        nb.add(frame, text='Configuration')

    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def showDialog(self):
        audio_path = tkFileDialog.askopenfilename(title="Open file")
        if audio_path:
            self.audio_path.set(audio_path)

    def showDialogFolder(self, option):
        folder_path = tkFileDialog.askdirectory(title="Output folder")
        if folder_path:
            if option == 1:
                self.output_path.set(folder_path)
                self.segmentation_png = folder_path + "/segmentation.png"
                self.oracle_path = folder_path + "/audio-oracle"
            elif option == 2:
                self.pn_path.set(folder_path)

            self.petri_png = folder_path + "/petri-net.png"
            self.petri_json = folder_path + "/petri-net.json"
            self.configuration_yml = folder_path + "/configuration.yml"
            self.petri_pnml = folder_path + "/petri-net"

    def messageError(self, error_msg):
        tkMessageBox.showerror('Message', error_msg)

    def messageInfo(self, msg):
        tkMessageBox.showinfo('Message', msg)

    def petri_net(self):
        if self.segmentation is not None:
            if self.output_path:
                self.pn = PetriNet(s=self.segmentation)
                self.pn.output_png(self.petri_png)
                self.pn.to_json(self.petri_json)
                self.pn.to_pnml(self.petri_pnml)
                utils.generate_configuration(self.configuration_yml, self.pn)

                self.messageInfo("Petri Net created")
            else:
                self.messageError("Set output path")
        else:
            self.messageError("Missing segmentation")

    def visualize_petri_net(self):
        if self.pn is not None and self.output_path:
            self.viewer(self.petri_png)
        else:
            self.messageError("Missing Petri Net")

    def load_petri_net(self):
        if self.pn_path.get() != "":
            self.pn_prev = PetriNet(pnml=self.petri_pnml)
            self.pn_prev.output_png(self.petri_png_prev)
            self.messageInfo("Petri Net loaded")
        else:
            self.messageError("Set output path")

    def update_petri_net(self):
        if self.pn_prev is not None and self.pn_path.get() != "":
            self.pn_prev.update_from_config(self.configuration_yml)
            self.pn_prev.output_png(self.petri_png_prev)
            self.messageInfo("Petri Net updated")
        else:
            self.messageError("Missing Petri Net")

    def preview_petri_net(self):
        if self.pn_prev is not None:
            self.viewer(self.petri_png_prev)
        else:
            self.messageError("Missing Petri Net")

    def save_petri_net(self):
        if self.pn_prev is not None and self.pn_path.get() != "":
            self.pn_prev.to_json(self.petri_json)
            self.pn_prev.to_pnml(self.petri_pnml)
            self.pn_prev.output_png(self.petri_png)
            self.messageInfo("Petri Net saved")
        else:
            self.messageError("Missing Petri Net")

    def visualize_segmentation(self):
        if self.segmentation is not None and self.output_path:
            self.viewer(self.segmentation_png)
        else:
            self.messageError("Missing Segmentation")

    def create_segmentation(self):
        if self.audio_path.get():
            if self.output_path.get():
                self.segmentation = Segmentation(self.audio_path.get())
                self.segmentation.output_png(self.segmentation_png)
                self.segmentation.save_oracle(self.oracle_path)
                self.messageInfo("Segmentation done")
            else:
                self.messageError("Set output path")
        else:
            self.messageError("Set the audio file path")

    def viewer(self, path):
        load = Image.open(path)
        load.show()
