import os
import sys
import logging
import re
import pandas as pd
sys.path.append(os.path.dirname(os.getcwd()))
from Transfer_Guid_To_Name import FileLocation
from excel_rw import ExcelRw
from efi_variable import EfiVariable
from setup_tree_data import SetupTreeData
from gset_tree_branch_node import GsetTree, GsetNode
from setup_switch_string_piddatoken import SetupSwitch, SetupString, PidDaToken
from data_dealwith import SdDealWith, FlowControl, SkipAction, DictHandle
from file_dealwith import FileDealWith


class Gset(object):

    def __init__(self, project_folder, platform_folder, output_folder, external_files_folder,
                 runtime_variable_enable, logger=False):
        self.setup_dict = dict()
        self.setup_dict['project_folder'] = project_folder
        self.setup_dict['platform_folder'] = platform_folder
        self.setup_dict['used_runtime_variable'] = runtime_variable_enable
        self.setup_dict['enable_debug'] = False
        self.setup_dict['output_folder'] = output_folder
        self.setup_dict['output_folder_data'] = output_folder + '\data'
        self.setup_dict['cwd_setup_item_folder'] = os.getcwd()
        self.setup_dict['logger2'] = logger
        if not re.search('Setup_Item', os.getcwd(), re.IGNORECASE):
            self.setup_dict['cwd_setup_item_folder'] = os.getcwd() + '\Setup_Item'
        if external_files_folder == '':
            self.setup_dict['external_files_folder'] = self.setup_dict['cwd_setup_item_folder'] + '\external_files'
        else:
            self.setup_dict['external_files_folder'] = external_files_folder

        self.setup_dict['dpf_expertkeystrings_file'] = self.setup_dict['cwd_setup_item_folder'] + '\dpf_files\ExpertKeyStrings.uni'
        self.setup_dict['dpf_expertkeyvfr_file'] = self.setup_dict['cwd_setup_item_folder'] + '\dpf_files\ExpertKeyVfr.vfr'

    def show_message_on_logger(self, message):
        if self.setup_dict['logger2']:
            self.logger2.info(message)

    def produce_gset_items_excel_file(self):
        # create logger
        logger = logging.getLogger('PostLog')
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        if not os.path.exists(self.setup_dict['output_folder_data']):
            os.makedirs(self.setup_dict['output_folder_data'])
        FileDealWith.update_output_folder(self.setup_dict['output_folder_data'], self.setup_dict['platform_folder'])

        # (0) build up token dictionary
        self.show_message_on_logger('Build up the token dictionary')
        setup_switch = SetupSwitch(self.setup_dict['project_folder'], self.setup_dict['platform_folder'])
        token_dict = setup_switch.get_token_dict()
        FileDealWith.write_list_to_file(DictHandle.extract_items(token_dict), 'token_dict.txt')

        # (0.1) build up PID, DaToken, PID_DaToken dictionary
        self.show_message_on_logger('Build up PID, DaToken, PID_DaToken dictionaries')
        pid_token = PidDaToken(self.setup_dict['project_folder'])
        pid_dict, datoken_dict, pid_token_dict = pid_token.get_pid_datoken_dict()
        FileDealWith.write_list_to_file(DictHandle.extract_items(pid_dict), 'pid_dict.txt')
        FileDealWith.write_list_to_file(DictHandle.extract_items(datoken_dict), 'datoken_dict.txt')
        FileDealWith.write_list_to_file(DictHandle.extract_items(pid_token_dict), 'pid_token_dict.txt')

        # (0.2) build up string_dict
        self.show_message_on_logger('Build up the string_dict')
        uni = FileLocation(root=self.setup_dict['project_folder'], filename_extension='.uni')
        uni.target_files.append(self.setup_dict['dpf_expertkeystrings_file'])

        uni_list = FileDealWith(uni.target_files, 'uni_origin.txt', 'uni_override.txt', 'uni_del.txt', 'uni_final.txt')
        setup_string = SetupString(uni_list.get_active_file_list())
        string_dict = setup_string.get_string_dict()
        FileDealWith.write_list_to_file(DictHandle.extract_items(string_dict), 'string_dict.txt', 'utf_16_le')

        # (1) build up sd define template
        self.show_message_on_logger('Build up the sd define template')
        sd = FileLocation(root=self.setup_dict['project_folder'], filename_extension='.sd')
        sd.target_files.append(self.setup_dict['dpf_expertkeyvfr_file'])

        sd_list = FileDealWith(sd.target_files, 'sd_origin.txt', 'sd_override.txt', 'sd_del.txt', 'sd_final.txt')
        sd_dealwith = SdDealWith(sd_list.get_active_file_list(), token_dict)
        FileDealWith.write_list_to_file(sd_dealwith.get_active_information(), 'sd_active_information_b.txt')
        # 1.1 some define is existed on *.sd. we need to renew token_dict
        token_dict = setup_switch.renew(sd_dealwith.get_active_information())
        FileDealWith.write_list_to_file(DictHandle.extract_items(token_dict), 'token_renew.txt')

        # 1.2 base on new token_dict, renew sd_active_information
        sd_dealwith.renew_active_information_with_new_token_dict(token_dict)
        FileDealWith.write_list_to_file(sd_dealwith.get_active_information(), 'sd_active_information.txt')

        # 1.3 build up setup variable field value dictionary
        self.show_message_on_logger('Build up the setup_variable_dict')
        efi_variable = EfiVariable(self.setup_dict, token_dict)
        df_local_dict = pd.DataFrame.from_dict(efi_variable.get_local_dict(), orient='index')
        df_setup_var = pd.DataFrame.from_dict(efi_variable.get_efi_variable_dict(setup=True), orient='index')
        df_other_var = pd.DataFrame.from_dict(efi_variable.get_efi_variable_dict(setup=False), orient='index')
        # Pandas writeExcel with Xlwt:xls and openpyxl:xlsx
        writer = pd.ExcelWriter(self.setup_dict['output_folder_data'] + '\\Z_DumpVariable.xlsx')
        df_local_dict.to_excel(writer, sheet_name='local_dict')
        df_setup_var.to_excel(writer, sheet_name='setup_var')
        df_other_var.to_excel(writer, sheet_name='other_var')
        writer.save()

        # 1.4 handle suppressif
        self.show_message_on_logger('Handle suppressif')
        sd_dealwith.information_renew_with_suppressif(efi_variable)
        FileDealWith.write_list_to_file(sd_dealwith.get_active_information(), 'sd_active_information_suppressif.txt')

        # 1.5 Build up sd_define_list, sd_formid_list
        self.show_message_on_logger('Build up sd_define_list, sd_formid_list')
        sd_dealwith.buildup_define_and_formid()
        sd_define_list, sd_formid_list = sd_dealwith.get_define_formid_list()
        FileDealWith.write_list_to_file(sd_define_list, 'sd_define_list.txt')
        FileDealWith.write_list_to_file(sd_formid_list, 'sd_formid_list.txt')

        # 2.0 walk through layer
        self.show_message_on_logger('Walk through setup')
        setup = GsetTree(self.setup_dict['project_folder'], token_dict, efi_variable, sd_formid_list, sd_define_list)
        gset_dict, layer_list = setup.get_gsetdict_layerlist()
        total_key = list(gset_dict.keys())
        FileDealWith.write_list_to_file(total_key, 'total_key.txt')
        FileDealWith.write_list_to_file(layer_list, 'layer_list.txt')
        FileDealWith.write_list_to_file(DictHandle.extract_items(gset_dict), 'gset_dict.txt')

        # 3
        self.show_message_on_logger('Write data to excel')
        setup_data = SetupTreeData(token_dict, string_dict, gset_dict, pid_dict, pid_token_dict, datoken_dict)
        setup_table = setup_data.output_in_list(layer_list, total_key)
        # print('===setup_table===')
        # for i in setup_table:
        #    print(i)

        # write to excel
        directory = self.setup_dict['output_folder'] + '\Release'
        if not os.path.exists(directory):
            os.makedirs(directory)
        p = ExcelRw(self.setup_dict['output_folder'] + '\Release\DA_Token_Setup.xls')
        p.write_table_and_save('Gset', setup_table)
        self.show_message_on_logger('Finish')


if __name__ == '__main__':
    #   gset = Gset('c:\BIOS\Rugged2\Liv2_99.0.41_Rev0901_BT',
    #               'c:\BIOS\Rugged2\Liv2_99.0.41_Rev0901_BT\OEMBOARD\LivingStone2',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item',
    #               '', False)
    gset = Gset('c:\BIOS\Rugged2\99.0.50_Rev0803',
                'c:\BIOS\Rugged2\99.0.50_Rev0803\OEMBOARD\Rugged2',
                'C:\Code_in_Python\Exercise\Log_Guid_Transfer\Setup_Item',
                'C:\Code_in_Python\Exercise\Log_Guid_Transfer\Setup_Item\external_files', False)
    #   gset = Gset('c:\BIOS\STL-010200',
    #               'c:\BIOS\STL-010200\OEMBOARD\Louis',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item\external_files', True)
    #   gset = Gset('c:\BIOS\STL-010900',
    #               'c:\BIOS\STL-010900\OEMBOARD\Louis',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item\external_files', False)
    #   gset = Gset('c:\BIOS\Rugged2\99.0.67_Rev1016',
    #               'c:\BIOS\Rugged2\99.0.67_Rev1016\OEMBOARD\Rugged2',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item\external_files', False)
    #   gset = Gset('c:\BIOS\Rugged2\99.0.54_Rev0839',
    #               'c:\BIOS\Rugged2\99.0.54_Rev0839\OEMBOARD\Rugged2',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item\external_files', False)
    #   gset = Gset('c:\BIOS\Rugged2\99.0.41_Rev0719',
    #               'c:\BIOS\Rugged2\99.0.41_Rev0719\OEMBOARD\Rugged2',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item\external_files', False)
    #   gset = Gset('c:\BIOS\Ford',
    #               'c:\BIOS\Ford\OEMBOARD\Ford',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item\external_files', False)
    ### fail , defaults.bin
    #   gset = Gset('c:\BIOS\Matira3\\1.2.1',
    #               'c:\BIOS\Matira3\\1.2.1\OEMBOARD\Matira3',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item\external_files', False)
    #   gset = Gset('c:\BIOS\G7_W99_Rev35734_U7',
    #               'c:\BIOS\G7_W99_Rev35734_U7\OEMBOARD\BeaverCreek',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item\external_files', False)
    #   gset = Gset('c:\BIOS\G8_BR99115_rev36200',
    #               'c:\BIOS\G8_BR99115_rev36200\OEMBOARD\BerlinettaMLK',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item\external_files', False)
    #   gset = Gset('c:\BIOS\G9_BR_MLK_R9975_rev35916',
    #               'c:\BIOS\G9_BR_MLK_R9975_rev35916\OEMBOARD\BreckenridgeMLK',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item',
    #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item\external_files', False)
    gset.produce_gset_items_excel_file()
