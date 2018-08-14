import os
import sys
import logging
import re

cwd = os.getcwd()
cwd_parent = os.path.dirname(os.getcwd())
sys.path.append(cwd_parent)
sys.path.append(cwd)
from Transfer_Guid_To_Name import FileLocation
from excel_rw import ExcelRw
from efi_variable import EfiVariable
from setup_tree_data import SetupTreeData
from gset_tree_branch_node import GsetTree, GsetNode
from setup_switch_string_piddatoken import SetupSwitch, SetupString, PidDaToken
from data_dealwith import SdDealWith, FlowControl, SkipAction, DictHandle
from file_dealwith import FileDealWith


class Gset(object):

    def __init__(self, project_folder, platform_folder, output_folder):
        self.p_folder = project_folder
        self.platform_folder = platform_folder
        self.output_folder = output_folder
        self.output_folder_media = output_folder + '\media'
        cwd = os.getcwd()
        self.cwd_setup_item_folder = cwd
        if not re.search('Setup_Item', cwd, re.IGNORECASE):
            self.cwd_setup_item_folder = cwd + '\Setup_Item'

    def produce_gset_items_excel_file(self):
        # create logger
        logger = logging.getLogger('PostLog')
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        if not os.path.exists(self.output_folder_media):
            os.makedirs(self.output_folder_media)
        FileDealWith.update_output_folder(self.output_folder_media)

        # (0) build up token dictionary
        setup_switch = SetupSwitch(self.p_folder)
        token_dict = setup_switch.get_token_dict()
        FileDealWith.write_list_to_file(DictHandle.extract_items(token_dict), 'token_dict.txt')

        # (0.1) build up PID, DaToken, PID_DaToken dictionary
        pid_token = PidDaToken(self.p_folder)
        pid_dict, datoken_dict, pid_token_dict = pid_token.get_pid_datoken_dict()
        FileDealWith.write_list_to_file(DictHandle.extract_items(pid_dict), 'pid_dict.txt')
        FileDealWith.write_list_to_file(DictHandle.extract_items(datoken_dict), 'datoken_dict.txt')
        FileDealWith.write_list_to_file(DictHandle.extract_items(pid_token_dict), 'pid_token_dict.txt')

        # (0.2) build up string_dict
        uni = FileLocation()
        uni.root_path = self.p_folder
        uni.gather_target_files('.uni')
        uni.target_files.append(self.cwd_setup_item_folder + '\ExpertKeyStrings.uni')

        uni_list = FileDealWith(uni.target_files, 'uni_original.txt', 'uni_override.txt', 'uni_remove.txt', 'uni_final.txt')
        setup_string = SetupString(uni_list.get_active_file_list())
        string_dict = setup_string.get_string_dict()
        FileDealWith.write_list_to_file(DictHandle.extract_items(string_dict), 'string_dict.txt', 'utf_16_le')

        # (1) build up sd define template
        sd = FileLocation()
        sd.root_path = self.p_folder
        sd.gather_target_files('.sd')
        sd.target_files.append(self.cwd_setup_item_folder + '\ExpertKeyVfr.vfr')

        sd_list = FileDealWith(sd.target_files, 'sd_original.txt', 'sd_override.txt', 'sd_remove.txt', 'sd_final.txt')
        sd_dealwith = SdDealWith(sd_list.get_active_file_list(), token_dict)
        FileDealWith.write_list_to_file(sd_dealwith.get_active_information(), 'sd_active_information_b.txt')
        # 1.1 some define is existed on *.sd. we need to renew token_dict
        token_dict = setup_switch.renew(sd_dealwith.get_active_information())
        FileDealWith.write_list_to_file(DictHandle.extract_items(token_dict), 'token_renew.txt')

        # 1.2 build up setup variable field value dictionary
        efi_variable = EfiVariable(self.cwd_setup_item_folder, self.p_folder, self.platform_folder, token_dict, False)
        FileDealWith.write_list_to_file(DictHandle.extract_items(efi_variable.get_setup_variable_dict()),
                                    'setup_variable_dict.txt')

        # 1.3 base on new token_dict, renew sd_active_information
        sd_dealwith.renew_active_information_with_new_token_dict(token_dict)
        FileDealWith.write_list_to_file(sd_dealwith.get_active_information(), 'sd_active_information.txt')
        # 1.4 handle suppressif
        sd_dealwith.information_renew_with_suppressif(efi_variable)
        FileDealWith.write_list_to_file(sd_dealwith.get_active_information(), 'sd_active_information_suppressif.txt')
        # 1.5 Build up sd_define_list, sd_formid_list
        sd_dealwith.buildup_define_and_formid()
        sd_define_list, sd_formid_list = sd_dealwith.get_define_formid_list()
        FileDealWith.write_list_to_file(sd_define_list, 'sd_define_list.txt')
        FileDealWith.write_list_to_file(sd_formid_list, 'sd_formid_list.txt')

        # 2.0 walk through layer
        setup = GsetTree(self.p_folder, token_dict, efi_variable, sd_formid_list, sd_define_list)
        gset_dict, layer_list = setup.get_gsetdict_layerlist()
        total_key = list(gset_dict.keys())
        FileDealWith.write_list_to_file(total_key, 'total_key.txt')
        FileDealWith.write_list_to_file(layer_list, 'layer_list.txt')
        FileDealWith.write_list_to_file(DictHandle.extract_items(gset_dict), 'gset_dict.txt')

        # 3.0 transfer data to list
        setup_data = SetupTreeData(token_dict, string_dict, gset_dict, pid_dict, pid_token_dict, datoken_dict)
        setup_table = setup_data.output_in_list(layer_list, total_key)
        # write to excel
        p = ExcelRw(self.output_folder + '\DA_Token_Setup.xls')
        p.write_table_and_save('Gset', setup_table)


if __name__ == '__main__':
 #   gset = Gset('c:\BIOS\STL-010200',
 #               'c:\BIOS\STL-010200\OEMBOARD\Louis',
 #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item')
    gset = Gset('c:\BIOS\Rugged2\Liv2_99.0.41_Rev0901_BT',
                'c:\BIOS\Rugged2\Liv2_99.0.41_Rev0901_BT\OEMBOARD\LivingStone2',
                'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item')
    gset.produce_gset_items_excel_file()
