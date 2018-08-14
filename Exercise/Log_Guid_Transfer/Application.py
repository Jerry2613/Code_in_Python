import os
import sys
import time
import functools
import logging
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QSplashScreen, QMessageBox
from PyQt5 import uic
#with open('BiosTool.ui', 'rb') as ui, open('Ui_BiosTool.py', 'w') as py:
#    uic.compileUi(ui, py)
from Ui_BiosTool import Ui_BiosTool
from Transfer_Guid_To_Name import FileLocation, GuidAction

cwd = os.getcwd()
sys.path.append(cwd + '\\Setup_Item')
from Gset_analysis import Gset
import xlrd
import xlwt
from xlutils.copy import copy


class MessageConsole(object):
#    def __init__(self, edit):
#        self.out = sys.stdout
#        self.plainTextEdit = edit
#
#    def write(self, message):
#        self.out.write(message)
#        self.plainTextEdit.textCursor().insertText(message)
#
#    def flush(self):
#        self.out.flush()
    @staticmethod
    def err_message_window(message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setInformativeText("Stop running!!!")
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


class MyHandler(logging.Handler):
    def __init__(self, widget):
        super(MyHandler, self).__init__()
        self._widget = widget

    def emit(self, record):
        msg = self.format(record)
        cursor = self._widget.textCursor()
        cursor.insertText(msg)
        cursor.insertText('\n')


class ImageDialog(QDialog):
    def __init__(self):
        super(ImageDialog, self).__init__()
        self.allguidtamplefile = 'Guid_all.txt'
        self.uniqueguidtamplefile = 'Guid_Unique.txt'
        self.loading_sequence_file = 'loading_sequence.txt'

        # Set up the user interface from Designer.
        self.ui = Ui_BiosTool()
        self.ui.setupUi(self)

        # Make some local modifications.
        self.ui.plainTextEdit.setReadOnly(True)
        # page 2 Gset analysis
        self.ui.plainTextEdit_2.setReadOnly(True)
#        sys.stdout = MessageConsole(self.ui.plainTextEdit)  # redirect stdout to self.ui.plainTetxEdit

        # Connect up the buttons.
        self.ui.e_refresh_guid_template.clicked.connect(self.refresh_guid_template)
        self.ui.e_replace_logfile_guid.clicked.connect(self.replace_logfile_guid)
        self.ui.e_produce_driver_loading_sequence.clicked.connect(self.produce_driver_loading_sequence)
        self.ui.folder_browser.clicked.connect(functools.partial(self.selectfolderfile, self.ui.root_path, True))
        self.ui.file_browser.clicked.connect(functools.partial(self.selectfolderfile, self.ui.logfile_name, False))
        # page 2 Gset analysis
        self.ui.folder_browser_2.clicked.connect(functools.partial(self.selectfolderfile, self.ui.root_path_2, True))
        self.ui.folder_browser_3.clicked.connect(functools.partial(self.selectfolderfile, self.ui.root_path_3, True))
        self.ui.folder_browser_4.clicked.connect(functools.partial(self.selectfolderfile, self.ui.root_path_4, True))
        self.ui.folder_browser_5.clicked.connect(functools.partial(self.selectfolderfile, self.ui.root_path_5, True))
        self.ui.e_produce_gset_items_excel.clicked.connect(self.produce_gset_items_excel)

    def selectfolderfile(self, response_ui, folder):
        dlg = QFileDialog()
        chosen = dlg.getExistingDirectory() if folder else dlg.getOpenFileName()[0]
        response_ui.setText(chosen)

    def refresh_guid_template(self):
        if self.ui.root_path.text() == ''or not os.path.isdir(self.ui.root_path.text()):
            MessageConsole.err_message_window("Input: Project Location is empty or wrong")
            return
        logger.info("Gather guids")
        pj = FileLocation()
        pj.root_path = self.ui.root_path.text()
        pj.gather_target_files('.dec')
        dec_num = len(pj.target_files)
        pj.gather_target_files('.inf')
        if os.path.isfile(self.allguidtamplefile):
            os.remove(self.allguidtamplefile)
        # Find out unique GUID and save to file
        for index, file in enumerate(pj.target_files):
            if index <= dec_num:
                GuidAction.produce_guidfile_from_file(file, self.allguidtamplefile, 'a+')
            else:
                GuidAction.build_driver_guid_from_inf(file, self.allguidtamplefile, 'a+')
        GuidAction.remove_duplicated_line(self.allguidtamplefile, self.uniqueguidtamplefile)
        logger.info("Refresh Guid template done")

    def replace_logfile_guid(self):
        if self.ui.logfile_name.text() == '' or not os.path.isfile(self.ui.logfile_name.text()):
            MessageConsole.err_message_window("Input: POST LogFile is empty or wrong")
            return
        if not os.path.isfile(self.uniqueguidtamplefile):
            MessageConsole.err_message_window("Input: No Guid template file")
            return
        p = GuidAction()
        p.target_log_file = self.ui.logfile_name.text()
        filename_list = p.target_log_file.split('.')
        filename_list.insert(1, '_New.')
        p.output_log_file = ''.join(filename_list)
        p.merge_guidfile_to_guidtable_list(self.uniqueguidtamplefile)
        p.transfer_logfile_guid()
        logger.info("Replace logfile done")

    def produce_driver_loading_sequence(self):
        if self.ui.logfile_name.text() == '' or not os.path.isfile(self.ui.logfile_name.text()):
            MessageConsole.err_message_window("Input: POST LogFile is empty or wrong")
            return
        with open(self.ui.logfile_name.text(), "r", encoding='mbcs') as logfile, open(self.loading_sequence_file, "a+", encoding='mbcs') as loading:
            for line in logfile:
                if 1 == line.count('.Entry'):
                    para = line.split('.Entry')
                    loading.write(para[0] + '\n')
        logger.info("Produce driver loading sequence done")

    def produce_gset_items_excel(self):
        if self.ui.root_path_2.text() == '' or not os.path.isdir(self.ui.root_path_2.text()):
            MessageConsole.err_message_window("Input: Source Code Location is empty or wrong")
            return
        if self.ui.root_path_3.text() == '' or not os.path.isdir(self.ui.root_path_3.text()):
            MessageConsole.err_message_window("Input: Platform folder Location is empty or wrong")
            return
        if self.ui.root_path_4.text() == '' or not os.path.isdir(self.ui.root_path_4.text()):
            MessageConsole.err_message_window("Input: Output Location is empty or wrong")
            return
        if self.ui.checkBox.isChecked():
            if self.ui.root_path_5.text() == '' or not os.path.isdir(self.ui.root_path_5.text()):
                MessageConsole.err_message_window("Setup Variable: Input Location is empty or wrong")
                return
            if not os.path.isfile(self.ui.root_path_5.text() + '/setup.bin'):
                MessageConsole.err_message_window("setup.bin don't exist on Setup Variable - Input Location folder")
                return
            if not os.path.isfile(self.ui.root_path_5.text() + '/BootManager.bin'):
                MessageConsole.err_message_window("BootManager.bin don't exist on Setup Variable - Input Location folder")
                return
        gset = Gset(self.ui.root_path_2.text(), self.ui.root_path_3.text(), self.ui.root_path_4.text(),
                    self.ui.root_path_5.text(), self.ui.checkBox.isChecked(), logger2)
        gset.produce_gset_items_excel_file()
        logger2.info("produce_gset_items_excel done")

#if __name__ == '__main__':
app = QApplication(sys.argv)

# PyQt UI
window = ImageDialog()

# create logger
logger = logging.getLogger('PostLog')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

widget = window.ui.plainTextEdit
my = MyHandler(widget)
logger.addHandler(my)

# page 2 logger
logger2 = logging.getLogger('PostLog_2')
logger2.setLevel(logging.DEBUG)

ch2 = logging.StreamHandler()
ch2.setLevel(logging.INFO)
formatter2 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch2.setFormatter(formatter2)
logger2.addHandler(ch2)

widget_2 = window.ui.plainTextEdit_2
my_2 = MyHandler(widget_2)
logger2.addHandler(my_2)

# Loading splash screen before main dialog is shown
splash_pix = QPixmap("icon/dog-paw.png")
splash = QSplashScreen(splash_pix)
splash.show()
time.sleep(1)
splash.close()

#
window.show()
sys.exit(app.exec_())
