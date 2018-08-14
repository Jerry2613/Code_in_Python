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

    def __init__(self, project_folder, platform_folder, output_folder, runtime_variable_enable=True):
        self.p_folder = project_folder
        self.platform_folder = platform_folder
        self.output_folder = output_folder
        self.used_runtime_variable = runtime_variable_enable
        self.output_folder_media = output_folder + '\media'
        cwd = os.getcwd()
        self.cwd_setup_item_folder = cwd
        if not re.search('Setup_Item', cwd, re.IGNORECASE):
            self.cwd_setup_item_folder = cwd + '\Setup_Item'

        self.dpf_expertkeystrings_file = self.cwd_setup_item_folder + '\dpf_files\ExpertKeyStrings.uni'
        self.dpf_expertkeyvfr_file = self.cwd_setup_item_folder + '\dpf_files\ExpertKeyVfr.vfr'

    def produce_gset_items_excel_file(self):
        # create logger
        print(' go 1 ')
        logger = logging.getLogger('PostLog')
        logger.setLevel(logging.DEBUG)
        print(' go 1.1 ')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        print(' go 1.2 ')
        if not os.path.exists(self.output_folder_media):
            os.makedirs(self.output_folder_media)
        print(' go 1.3 ')
        FileDealWith.update_output_folder(self.output_folder_media, self.platform_folder)

        # (0) build up token dictionary
        print(' go 2 ')
        setup_switch = SetupSwitch(self.p_folder, self.platform_folder)
        token_dict = setup_switch.get_token_dict()
        FileDealWith.write_list_to_file(DictHandle.extract_items(token_dict), 'token_dict.txt')

        # (0.1) build up PID, DaToken, PID_DaToken dictionary
        print(' go 3 ')
        pid_token = PidDaToken(self.p_folder)
        pid_dict, datoken_dict, pid_token_dict = pid_token.get_pid_datoken_dict()
        FileDealWith.write_list_to_file(DictHandle.extract_items(pid_dict), 'pid_dict.txt')
        FileDealWith.write_list_to_file(DictHandle.extract_items(datoken_dict), 'datoken_dict.txt')
        FileDealWith.write_list_to_file(DictHandle.extract_items(pid_token_dict), 'pid_token_dict.txt')

        # (0.2) build up string_dict
        print(' go 4 ')
        uni = FileLocation()
        uni.root_path = self.p_folder
        uni.gather_target_files('.uni')
        uni.target_files.append(self.dpf_expertkeystrings_file)

        uni_list = FileDealWith(uni.target_files, 'uni_origin.txt', 'uni_override.txt', 'uni_del.txt', 'uni_final.txt')
        setup_string = SetupString(uni_list.get_active_file_list())
        string_dict = setup_string.get_string_dict()
        FileDealWith.write_list_to_file(DictHandle.extract_items(string_dict), 'string_dict.txt', 'utf_16_le')

        # (1) build up sd define template
        print(' go 5 ')
        sd = FileLocation()
        sd.root_path = self.p_folder
        sd.gather_target_files('.sd')
        sd.target_files.append(self.dpf_expertkeyvfr_file)

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
        efi_variable = EfiVariable(self.cwd_setup_item_folder, self.p_folder, self.platform_folder, self.output_folder,
                                   token_dict, self.used_runtime_variable, False)
        FileDealWith.write_list_to_file(DictHandle.extract_items(efi_variable.get_setup_variable_dict()),
                                        'setup_variable_dict.txt')
        # 1.4 handle suppressif
        sd_dealwith.information_renew_with_suppressif(efi_variable)
        FileDealWith.write_list_to_file(sd_dealwith.get_active_information(), 'sd_active_information_suppressif.txt')

        # 1.5 Build up sd_define_list, sd_formid_list
        sd_dealwith.buildup_define_and_formid()
        sd_define_list, sd_formid_list = sd_dealwith.get_define_formid_list()
        FileDealWith.write_list_to_file(sd_define_list, 'sd_define_list.txt')
        FileDealWith.write_list_to_file(sd_formid_list, 'sd_formid_list.txt')
        print(' go 6 ')
        # 2.0 walk through layer
        setup = GsetTree(self.p_folder, token_dict, efi_variable, sd_formid_list, sd_define_list)
        gset_dict, layer_list = setup.get_gsetdict_layerlist()
        total_key = list(gset_dict.keys())
        FileDealWith.write_list_to_file(total_key, 'total_key.txt')
        FileDealWith.write_list_to_file(layer_list, 'layer_list.txt')
        FileDealWith.write_list_to_file(DictHandle.extract_items(gset_dict), 'gset_dict.txt')
        print(' go 7 ')
        # 3
        setup_data = SetupTreeData(token_dict, string_dict, gset_dict, pid_dict, pid_token_dict, datoken_dict)
        setup_table = setup_data.output_in_list(layer_list, total_key)
        # write to excel
        print(' go 8 ')
        directory = self.output_folder + '\Release'
        if not os.path.exists(directory):
            os.makedirs(directory)
        p = ExcelRw(self.output_folder + '\Release\DA_Token_Setup.xls')
        print(' go 9 ')
        p.write_table_and_save('Gset', setup_table)
        print(' go 10 ')

if __name__ == '__main__':
 #   gset = Gset('c:\BIOS\Rugged2\Liv2_99.0.41_Rev0901_BT',
 #               'c:\BIOS\Rugged2\Liv2_99.0.41_Rev0901_BT\OEMBOARD\LivingStone2',
 #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item', True)
 #   gset = Gset('c:\BIOS\Rugged2\Liv2_99.0.45_Rev1105',
 #               'c:\BIOS\Rugged2\Liv2_99.0.45_Rev1105\OEMBOARD\LivingStone2',
 #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item', True)
    gset = Gset('c:\BIOS\STL-010200',
                'c:\BIOS\STL-010200\OEMBOARD\Louis',
                'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item', False)
 #   gset = Gset('c:\BIOS\STL-010900',
 #               'c:\BIOS\STL-010900\OEMBOARD\Louis',
 #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item', False)
 #   gset = Gset('c:\BIOS\Rugged2\99.0.67_Rev1016',
 #               'c:\BIOS\Rugged2\99.0.67_Rev1016\OEMBOARD\Rugged2',
 #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item', False)
 #   gset = Gset('c:\BIOS\Rugged2\99.0.54_Rev0839',
 #               'c:\BIOS\Rugged2\99.0.54_Rev0839\OEMBOARD\Rugged2',
 #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item', False)
 #   gset = Gset('c:\BIOS\Rugged2\99.0.41_Rev0719',
 #               'c:\BIOS\Rugged2\99.0.41_Rev0719\OEMBOARD\Rugged2',
 #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item', False)
 #   gset = Gset('c:\BIOS\Ford',
 #               'c:\BIOS\Ford\OEMBOARD\Ford',
 #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item', False)
 ### fail , defaults.bin
 #   gset = Gset('c:\BIOS\Matira3\\1.2.1',
 #               'c:\BIOS\Matira3\\1.2.1\OEMBOARD\Matira3',
 #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item', False)
 #   gset = Gset('c:\BIOS\G7_W99_Rev35734_U7',
 #               'c:\BIOS\G7_W99_Rev35734_U7\OEMBOARD\BeaverCreek',
 #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item', False)
 #   gset = Gset('c:\BIOS\G8_BR99115_rev36200',
 #               'c:\BIOS\G8_BR99115_rev36200\OEMBOARD\BerlinettaMLK',
 #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item', False)
 #   gset = Gset('c:\BIOS\G9_BR_MLK_R9975_rev35916',
 #               'c:\BIOS\G9_BR_MLK_R9975_rev35916\OEMBOARD\BreckenridgeMLK',
 #               'C:\Python_road\MyPython\Exercise\Log_Guid_Transfer\Setup_Item', False)
    gset.produce_gset_items_excel_file()
