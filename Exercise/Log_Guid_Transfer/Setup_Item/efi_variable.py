import re
import os
import sys
from data_dealwith import DataSave
sys.path.append(os.path.dirname(os.getcwd()))
from Transfer_Guid_To_Name import FileLocation


class EfiVariable:

    def __init__(self, input_dict, token_dict):
        #
        #  [Local_dict]
        #    [Input_dict]
        #      root
        #      p_folder
        #      used_runtime_variable
        #      ext_files_folder
        #      enable_debug
        #      o_folder
        #      o_folder_data
        #    [Extend fields]
        #      setup_definition_file
        #      bootmanager_definition_file
        #      amitsemode_definition_file
        #
        #      bios_default_binary_file (Option for *emulator)
        #      setup_binary_file
        #      bootmanager_binary_file
        #      amitseMode variable under UEFI shell (???)
        #      setupamtfeatures_binary_file
        #
        #    *emulator: We need to dump and save some variables under shell.
        #               No this, some information may not correct.
        #
        self.var_dump_file = 'VariableDump.xlsx'
        self.local_dict = input_dict
        self.token_dict = token_dict

        # Fill variable definition files
        d_file = FileLocation(root=self.local_dict['p_folder'], filename_extension='HardcodedSetupData.h')
        self.local_dict['setup_definition_file'] = d_file.target_files[0]
        self.local_dict['amitsemode_definition_file'] = input_dict['root'] + '\DellPkg\Include\SetupPrep.h'
        self.local_dict['bootmanager_definition_file'] = input_dict['root'] + '\AmiTsePkg\Include\AMIVfr.h'

        # Fill variable value files
        if input_dict['used_runtime_variable']:
            self.local_dict['setup_binary_file'] = input_dict['ext_files_folder'] + '\setup.bin'
        else:
            d_file = FileLocation(root=self.local_dict['root'] + '\Build', filename_extension='Defaults.bin')
            self.local_dict['bios_default_binary_file'] = d_file.target_files[0]
            self.local_dict['setup_binary_file'] = input_dict['o_folder'] + '\data\setup_default.bin'
            self.extract_variable_from_bios_default_file()
        if os.path.isfile(input_dict['ext_files_folder'] + '\BootManager.bin'):
            self.local_dict['bootmanager_binary_file'] = input_dict['ext_files_folder'] + '\BootManager.bin'
        if os.path.isfile(input_dict['ext_files_folder'] + '\SetupAmtFeatures.bin'):
            self.local_dict['setupamtfeatures_binary_file'] = input_dict['ext_files_folder'] + \
                                                              '\SetupAmtFeatures.bin'

        self.setup_variable_dict = {}
        self.other_variable_dict = {}

        self.buildup_setup_dict()
        self.buildup_other_variable_dict()

    def buildup_setup_dict(self):
        setup_variable_data_list = EfiVariable.extract_data_from_binary_file(self.local_dict['setup_binary_file'], 0x28)
        # (1) Build/GenericSetupDataDefinition.h insert a field: Numlock
        index = 0
        data = [setup_variable_data_list[0]]
        self.setup_variable_dict['Numlock'] = data
        index += 1

        # (2) HardcodedSetupData.h
        with open(self.local_dict['setup_definition_file'], "r") as field_define:
            for line in field_define:
                new_line = line.replace(';', '').replace('//', ' // ').split('//')[0]
                new_line_2 = " ".join(new_line.split())
                if re.match('UINT', new_line_2, re.IGNORECASE) or re.match('CHAR', new_line_2, re.IGNORECASE):
                    field_size = EfiVariable.get_field_size(new_line_2)
                    if re.search('\[', new_line_2, re.IGNORECASE):
                        line_3_list = new_line_2.replace('[', ' ').replace(']', ' ').split(' ')
                        line_4_list = [x for x in line_3_list if x is not '']
                        array_number = line_4_list[2]
                        if re.search('0x', array_number, re.IGNORECASE):
                            array_number = int(array_number, 16)  # int(STRING, BASE)
                        else:
                            array_number = int(array_number)
                        # print('##array_number:', array_number, '##index', hex(0x28 + index))
                        data = ['ARRAY']
                        for j in range(array_number):
                            sub_data = [setup_variable_data_list[index + i] for i in range(field_size)]
                            index += field_size
                            data.append(sub_data)
                    else:
                        line_4_list = new_line_2.split(' ')
                        # print('@@index', hex(0x28 + index))
                        data = [setup_variable_data_list[index+i] for i in range(field_size)]
                        index += field_size
                    key = line_4_list[1]
                    # print('@@key', key, '@@data', data)
                    self.setup_variable_dict[key] = data
        if self.local_dict['enable_debug']:
            self.show_setup_variable_dict()
            print('### setup_variable_dict: data size',  len(setup_variable_data_list), ' data used:', index)

    def buildup_other_variable_dict(self):
        # 1.0 AMITSEMODE
        # I can't find AmiTseMode variable under UEFI shell
        # Current i set all fields' value to 0 (default value)
        field_structure = self.get_focus_data_struct('AMITSEMODE', self.local_dict['amitsemode_definition_file'])
        index = 0
        for index in range(0, len(field_structure), 2):
            self.other_variable_dict['AMITSEMODE.' + field_structure[index]] = '0'

        # 1.1 BOOT_MANAGER
        #   if self.local_dict['bootmanager_binary_file'] is not None:
        if 'bootmanager_binary_file' in self.local_dict.keys():
            field_structure = self.get_focus_data_struct('BOOT_MANAGER', self.local_dict['bootmanager_definition_file'])
            data = EfiVariable.extract_data_from_binary_file(self.local_dict['bootmanager_binary_file'], 0x34)
            for index in range(0, len(field_structure), 2):
                if field_structure[index+1] == 2:
                    a0 = int(str(data[0]), 16)
                    a1 = int(str(data[1]), 16)
                    value = a1 + a0
                else:
                    value = int(str(data[0]), 16)
                self.other_variable_dict['BOOT_MANAGER.' + field_structure[index]] = value

        # 1.2 SETUP_AMT_FEATURES
        # Structure is under chipset folder KabylakePlatSamplePkg\Setup\MeSetup.h'
        # this tool is cross platform. so i just copy the structure from this file
        if 'setupamtfeatures_binary_file' in self.local_dict.keys():
            field_structure = ['GrayOut', 1]
            data = EfiVariable.extract_data_from_binary_file(self.local_dict['setupamtfeatures_binary_file'], 0x3e)
            self.other_variable_dict['SETUP_AMT_FEATURES.' + field_structure[index]] = int(str(data[0]), 16)
            if self.local_dict['enable_debug']:
                print('### other_variable_dict:', self.other_variable_dict.items())

    def get_field_value(self, field):
        value = 'N/A'
        if re.search('\[', field, re.IGNORECASE):
            data_list = field.replace('[', ' ').replace(']', ' ').strip().split(' ')
            field_value = self.setup_variable_dict.get(data_list[0], 'N/A')
            if field_value != 'N/A':
                index = self.token_dict.get(data_list[1], 'N/A')
                if index != 'N/A':
                    if field_value[0] == 'ARRAY':
                        index = int(index, 0) + int(1)
                    value = field_value[int(index)]
        else:
            value = self.setup_variable_dict.get(field, 'N/A')
        return value

    @staticmethod
    def extract_data_from_binary_file(file_name, start_index):
        with open(file_name, "rb") as binary_file:
            binary_file.seek(start_index)
            b_data = binary_file.read()
            data = bytearray(b_data)
        return data

    def extract_variable_from_bios_default_file(self):
        with open(self.local_dict['bios_default_binary_file'], "rb") as binary_file:
            variable_number = 0
            binary_file.seek(0, 2)            # Seek to the end
            num_bytes = binary_file.tell()    # Get the file size
            for i in range(num_bytes):
                binary_file.seek(i)
                compare_data = binary_file.read(4)
                if compare_data == b"\x4e\x56\x41\x52":
                    variable_number += 1
                    if variable_number == 3:    # setup variable on #2
                        setup_variable_end_location = binary_file.tell()-4
                        print("Reach setup data end:", setup_variable_end_location)
                        with open(self.local_dict['setup_binary_file'], "wb") as outfile:
                            binary_file.seek(0)
                            data = binary_file.read(setup_variable_end_location)
                            outfile.write(data)
                        break

    @staticmethod
    def get_field_size(line):
        f_size = 0
        line_unit = line.split(' ')[0]
        if re.match('UINT', line, re.IGNORECASE) or re.match('CHAR', line, re.IGNORECASE):
            f_size = line_unit.replace('UINT', '').replace('CHAR', '').strip()
        size = int(int(f_size) / int(8))
        # print('===line:', line, ', line_unit:', line_unit, 'size', size)
        return size

    def get_focus_data_struct(self, struct_name, struct_location):
        field_structure = []
        with open(struct_location, "r") as target_file:
            for line in target_file:
                if re.search('typedef', line, re.IGNORECASE) and re.search('struct', line, re.IGNORECASE):
                    data_structure = []
                    next_line_leave_flag = False
                    record_flag = False
                    new_line = 0
                    for next_line in target_file:
                        next_line = next_line.replace(';', '').strip()
                        new_line = ' '.join(next_line.split())
                        if next_line_leave_flag:
                            break
                        if re.match('}', new_line, re.IGNORECASE):
                            if re.search(struct_name, new_line, re.IGNORECASE):
                                break
                            else:
                                next_line_leave_flag = True
                                continue
                        if re.match('{', new_line, re.IGNORECASE):
                            new_line = new_line.replace('{', '')
                            record_flag = True
                        if record_flag and new_line != '':
                            data_structure.append(new_line)
                    if re.search(struct_name, new_line, re.IGNORECASE):
                        for data in data_structure:
                            data_list = data.split(' ')
                            field_structure.append(data_list[1])
                            field_structure.append(self.get_field_size(data_list[0]))
                        break
        return field_structure

    def show_setup_variable_dict(self):
        print('~~~~~~~~~~setup_variable_dict~~~~~~~~~~~~~~~~~~')
        for i in self.setup_variable_dict.keys():
            print('Field:', i)
            value = self.setup_variable_dict[i]
            if value[0] == 'ARRAY':
                for array_index in range(1, len(value)):
                    print('Value_' + str(array_index) + ':', value[array_index])
            else:
                print('Value:', value)

    def save_efivariable_to_file(self):
        o_folder = self.local_dict['o_folder_data']
        DataSave.dict_to_xlsx(self.local_dict, o_folder, self.var_dump_file, sheet='local_dict')
        DataSave.dict_to_xlsx(self.setup_variable_dict, o_folder, self.var_dump_file, sheet='setup_var')
        DataSave.dict_to_xlsx(self.other_variable_dict, o_folder, self.var_dump_file, sheet='other_var')


if __name__ == '__main__':
    E_input_dict = dict()
    E_input_dict['root'] = 'c:\BIOS\Rugged2\99.0.50_Rev0803'
    E_input_dict['p_folder'] = 'c:\BIOS\Rugged2\99.0.50_Rev0803\OEMBOARD\Rugged2'
    E_input_dict['used_runtime_variable'] = False
    E_input_dict['ext_files_folder'] = os.getcwd() + '\external_files'
    E_input_dict['enable_debug'] = True
    E_input_dict['o_folder'] = os.getcwd()
    E_input_dict['o_folder_data'] = os.getcwd() + '\data'
    E_token_dict = {}
    efi_variable = EfiVariable(E_input_dict, E_token_dict)
    efi_variable.save_efivariable_to_file()
