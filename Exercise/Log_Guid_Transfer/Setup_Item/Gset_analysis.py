import os
import sys
import logging
import re
sys.path.append(os.path.dirname(os.getcwd()))
from Transfer_Guid_To_Name import FileLocation
from excel_rw import ExcelRw
from efi_variable import EfiVariable
from setup_tree_data import SetupTreeData
from gset_tree_branch_node import GsetTree, GsetNode
from setup_switch_string_piddatoken import SetupSwitch, SetupString, PidDaToken
from data_dealwith import SdDealWith, FlowControl, SkipAction, DataSave
from file_dealwith import FileDealWith


class Gset(object):

    def __init__(self, root, p_folder, o_folder, ext_files_folder, use_runtime_variable, logger=''):
        self.setup_d = dict()
        self.setup_d['root'] = root
        self.setup_d['p_folder'] = p_folder
        self.setup_d['used_runtime_variable'] = use_runtime_variable
        self.setup_d['enable_debug'] = False
        self.setup_d['o_folder'] = o_folder
        self.setup_d['o_folder_data'] = o_folder + '\data'
        self.setup_d['logger2'] = logger
        if re.search('Setup_Item', os.getcwd(), re.IGNORECASE):
            self.setup_d['setup_item_folder'] = os.getcwd()
        else:
            self.setup_d['setup_item_folder'] = os.getcwd() + '\Setup_Item'
        if ext_files_folder == '':
            self.setup_d['ext_files_folder'] = self.setup_d['setup_item_folder'] + '\external_files'
        else:
            self.setup_d['ext_files_folder'] = ext_files_folder
        self.setup_d['dpf_expertkeystrings'] = self.setup_d['setup_item_folder'] + '\dpf_files\ExpertKeyStrings.uni'
        self.setup_d['dpf_expertkeyvfr'] = self.setup_d['setup_item_folder'] + '\dpf_files\ExpertKeyVfr.vfr'

    def show_message_on_logger(self, message):
        if self.setup_d['logger2']:
            self.setup_d['logger2'].info(message)

    def produce_gset_items_excel_file(self):
        # create logger

        logger = logging.getLogger('PostLog')
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        if not os.path.exists(self.setup_d['o_folder_data']):
            os.makedirs(self.setup_d['o_folder_data'])

        # (0) build up token dictionary
        self.show_message_on_logger('Build up the token dictionary')
        setup_switch = SetupSwitch(self.setup_d['o_folder_data'], self.setup_d['root'], self.setup_d['p_folder'])
        token_dict = setup_switch.token_dict
        DataSave.dict_to_csv(token_dict, self.setup_d['o_folder_data'], 'token_dict.txt')

        # (0.1) build up PID, DaToken, PID_DaToken dictionary
        self.show_message_on_logger('Build up PID, DaToken, PID_DaToken dictionaries')
        pid_token = PidDaToken(self.setup_d['root'])
        pid_dict, datoken_dict, pid_token_dict = pid_token.get_pid_datoken_dict()
        DataSave.dict_to_csv(pid_dict, self.setup_d['o_folder_data'], 'pid_dict.txt')
        DataSave.dict_to_csv(datoken_dict, self.setup_d['o_folder_data'], 'datoken_dict.txt')
        DataSave.dict_to_csv(pid_token_dict, self.setup_d['o_folder_data'], 'pid_token_dict.txt')

        # (0.2) build up string_dict
        self.show_message_on_logger('Build up the string_dict')
        uni = FileLocation(root=self.setup_d['root'], filename_extension='.uni')
        uni.target_files.append(self.setup_d['dpf_expertkeystrings'])

        uni_list = FileDealWith(self.setup_d['o_folder_data'], self.setup_d['p_folder'], uni.target_files, o_file_name='uni')
        setup_string = SetupString(uni_list.active_file_list)
        string_dict = setup_string.string_dict
        DataSave.dict_to_csv(string_dict, self.setup_d['o_folder_data'], 'string_dict.txt', 'utf_16_le')

        # (1) build up sd define template
        self.show_message_on_logger('Build up the sd define template')
        sd = FileLocation(root=self.setup_d['root'], filename_extension='.sd')
        sd.target_files.append(self.setup_d['dpf_expertkeyvfr'])

        sd_list = FileDealWith(self.setup_d['o_folder_data'], self.setup_d['p_folder'], sd.target_files, o_file_name='sd')
        sd_handle = SdDealWith(sd_list.active_file_list, token_dict)
        DataSave.list_to_txt(sd_handle.active_information, self.setup_d['o_folder_data'], 'sd_active_info_b.txt')

        # 1.1 some define is existed on *.sd. we need to renew token_dict
        token_dict = setup_switch.renew(sd_handle.active_information)
        DataSave.dict_to_csv(token_dict, self.setup_d['o_folder_data'], 'token_renew.txt')

        # 1.2 base on new token_dict, renew sd_active_info
        sd_handle.renew_active_information_with_new_token_dict(token_dict)
        DataSave.list_to_txt(sd_handle.active_information, self.setup_d['o_folder_data'], 'sd_active_info.txt')

        # 1.3 build up setup variable field value dictionary
        self.show_message_on_logger('Build up the setup_variable_dict')
        efi_variable = EfiVariable(self.setup_d, token_dict)
        efi_variable.save_efivariable_to_file()

        # 1.4 handle suppressif
        self.show_message_on_logger('Handle suppressif')
        sd_handle.information_renew_with_suppressif(efi_variable)
        DataSave.list_to_txt(sd_handle.active_information, self.setup_d['o_folder_data'], 'sd_active_info_suppressif.txt')

        # 1.5 Build up sd_define_list, sd_formid_list
        self.show_message_on_logger('Build up sd_define_list, sd_formid_list')
        sd_handle.buildup_define_and_formid()
        sd_define_list, sd_formid_list = sd_handle.get_define_formid_list()
        DataSave.list_to_txt(sd_define_list, self.setup_d['o_folder_data'], 'sd_define_list.txt')
        DataSave.list_to_txt(sd_formid_list, self.setup_d['o_folder_data'], 'sd_formid_list.txt')

        # 2.0 walk through layer
        self.show_message_on_logger('Walk through setup')
        setup = GsetTree(self.setup_d['o_folder_data'], self.setup_d['root'], token_dict, efi_variable, sd_formid_list, sd_define_list)
        gset_dict, layer_list = setup.get_gsetdict_layerlist()
        total_key = list(gset_dict.keys())
        DataSave.list_to_txt(total_key, self.setup_d['o_folder_data'], 'total_key.txt')
        DataSave.list_to_txt(layer_list, self.setup_d['o_folder_data'], 'layer_list.txt')
        DataSave.dict_to_csv(gset_dict, self.setup_d['o_folder_data'], 'gset_dict.txt')

        # 3
        self.show_message_on_logger('Write data to excel')
        setup_data = SetupTreeData(token_dict, string_dict, gset_dict, pid_dict, pid_token_dict, datoken_dict)
        setup_table = setup_data.output_in_list(layer_list, total_key)
        # print('===setup_table===')
        # for i in setup_table:
        #    print(i)

        # write to excel
        # todo replace by panda
        directory = self.setup_d['o_folder'] + '\Release'
        if not os.path.exists(directory):
            os.makedirs(directory)
        p = ExcelRw(self.setup_d['o_folder'] + '\Release\DA_Token_Setup.xls')
        p.write_table_and_save('Gset', setup_table)
        self.show_message_on_logger('Finish')


if __name__ == '__main__':
    gs = Gset('c:\BIOS\Rugged2\99.0.50_Rev0803',
              'c:\BIOS\Rugged2\99.0.50_Rev0803\OEMBOARD\Rugged2',
              'C:\Code_in_Python\Exercise\Log_Guid_Transfer\Setup_Item',
              'C:\Code_in_Python\Exercise\Log_Guid_Transfer\Setup_Item\external_files', False)
    gs.produce_gset_items_excel_file()
