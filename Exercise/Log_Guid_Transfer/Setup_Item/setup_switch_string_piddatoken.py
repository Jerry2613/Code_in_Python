import re
from data_dealwith import SkipAction
from Transfer_Guid_To_Name import FileLocation
from file_dealwith import FileDealWith


class SetupSwitch(object):

    def __init__(self, o_folder, root, p_folder):
        self.o_folder = o_folder
        self.root = root
        self.p_folder = p_folder
        self.DellPkg_Include = root + '\DellPkg\Include'
        self.DPFPkg_Include = root + '\DPFPkg\DellClientLibPkgs\DellPublicProductionPkg\Include'
        self.switch_files = []
        self.token_dict = {}
        self.reference_files()
        self.buildup()

    def reference_files(self):
        h_files = FileLocation()
        h_files.target_files.append(self.root + '\Build\Token.h')
        h_files.root_path = self.p_folder
        h_files.gather_target_files('.h')
        h_files.root_path = self.DellPkg_Include
        h_files.gather_target_files('.h')
        h_files.root_path = self.DPFPkg_Include
        h_files.gather_target_files('.h')
        h_files_list = FileDealWith(self.o_folder, self.p_folder, h_files.target_files, o_file_name='h')
        self.switch_files = h_files_list.active_file_list

    def buildup(self):
        re_search_skip = ['_TOKEN_SDL_H', '__DELL_GSET_ITEM_CFG_H__', '_DELL_SETUP_FIELD_ATTRIB_H']
        for h_file in self.switch_files:
            with open(h_file, "r") as tfile:
                # iterate it. then pass the iterator to another function. it will output the data from last point.
                iter_tfile = iter(tfile)
                for line in iter_tfile:
                    if SkipAction.row(line, re_search_skip) or SkipAction.comment(iter_tfile, line):
                        continue
                    new_line = " ".join(line.split())
                    new_line = SkipAction.none_enabled_area_if_else(iter_tfile, new_line, self.token_dict)
                    if re.search('//', new_line, re.IGNORECASE):
                        new_line_2 = new_line.split("//")[0]
                    else:
                        new_line_2 = new_line
                    new_line_list = new_line_2.split(' ', 2)
                    if len(new_line_list) <= 2:
                        new_line_list.append(' ')

                    if re.match('#define', new_line_2, re.IGNORECASE):
                        self.token_dict[new_line_list[1]] = new_line_list[2]
                    if re.match('#undef', new_line_2, re.IGNORECASE):
                        switch_exist = self.token_dict.get(new_line_list[1], 'Not_Found')
                        if switch_exist != 'Not_Found':
                            del self.token_dict[new_line_list[1]]
        for i in range(0, 100):
            self.token_dict[str(i)] = str(i)
        for i in ['0x0', '0x1', '0x2', '0x3', '0x4', '0x5', '0x6', '0x7', '0x8', '0x9']:
            self.token_dict[i] = i

    def renew(self, new_information):
        for line in new_information:
            if re.match('#define', line.strip(), re.IGNORECASE):
                if re.search('SUPPRESS_GRAYOUT_ENDIF', line.strip(), re.IGNORECASE):
                    continue
                new_line = ' '.join(line.split())
                line_list = new_line.split(' ')
                if re.search('\(', line_list[1], re.IGNORECASE) and not re.search('\)', line_list[1], re.IGNORECASE):
                    continue
                if len(line_list) == 3:
                    self.token_dict[line_list[1]] = line_list[2]
        return self.token_dict


class SetupString(object):

    def __init__(self, string_files_list):
        self.string_files_list = string_files_list
        self.string_dict = {}
        self.buildup('eng')

    def buildup(self, language):
        if language == 'eng' or language == 'en-US':
            lang = [' eng ', ' en-US ']
        else:
            lang = ['No support', 'No support']

        string_list = []
        for string_file in self.string_files_list:
            with open(string_file, "r", encoding='utf_16_le') as s_file:
                try:
                    for line in s_file:
                        line.encode('utf_8', 'ignore')
                        new_line = line.split('//')[0].strip()
                        if re.match('#string', new_line, re.IGNORECASE) and re.search('#language', new_line, re.IGNORECASE):
                            # check the same row
                            if re.search(lang[0], new_line, re.IGNORECASE) or re.search(lang[1], new_line, re.IGNORECASE):
                                string_list.append(new_line.replace('\n', ''))
                                continue
                        if re.match('"', new_line.strip()):
                            string_list.append(new_line.replace('\n', ''))
                except UnicodeDecodeError:
                    print('*** except string file:', string_file)
                    continue
        for index, element in enumerate(string_list):
            string_data = []
            if re.match('#string', element, re.IGNORECASE):
                new_element = " ".join(element.split())
                new_element_list = new_element.split(' ', 2)
                if re.search(' eng ', new_element_list[2]):
                    s_data = new_element_list[2].split('eng', 1)[1]
                else:
                    s_data = new_element_list[2].split('en-US', 1)[1]
                string_data.append(s_data.replace('"', '').replace("\\n", '').strip())
                if index < len(string_list):
                    for i in range(1, 10):
                        if index + i == len(string_list):
                            break
                        next_s_data = string_list[index + i].replace('"', '').replace('\\n', '').strip()
                        #    print(index+i, next_s_data)
                        if re.match('#string', next_s_data, re.IGNORECASE):
                            break
                        string_data.append(next_s_data)
                if len(string_data) == 1:
                    self.string_dict[new_element_list[1]] = string_data[0]
                else:
                    combined_data = string_data[0]
                    for i in range(1, len(string_data)):
                        combined_data += ' ' + string_data[i]
                    self.string_dict[new_element_list[1]] = combined_data


class PidDaToken(object):

    def __init__(self, p_folder):
        self.folder = p_folder
        self.Dell_Include = p_folder + '\DPFPkg\DellClientLibPkgs\DellPublicProductionPkg\Include'
        self.pid_file = self.Dell_Include + '\Guid\DellPropertyIds.h'
        self.datoken_file = self.Dell_Include + '\Guid\DaTokenIDs.h'
        self.pid_datoekn_file = self.Dell_Include + '\AllPossibleSMBiosDaTokens.h'
        self.pid_dict = {}
        self.datoken_dict = {}
        self.pid_datoken_dict = {}
        self.buildup('PID')
        self.buildup('DaToken')
        self.buildup_pid_token_dict()

    # Support to build dictionary: "PID" "DaToken"
    def buildup(self, dict_type):
        re_search_skip = ['_DELL_PROPERTY_IDS_H_']
        if dict_type == 'PID':
            dell_file = self.pid_file
            p_dict = self.pid_dict
        elif dict_type == 'DaToken':
            dell_file = self.datoken_file
            p_dict = self.datoken_dict
        else:
            print("No support")
            return

        with open(dell_file, "r") as pfile:
            for line in pfile:
                if SkipAction.row(line, re_search_skip) or SkipAction.comment(pfile, line):
                    continue
                new_line = " ".join(line.split())
                if re.match('#define', new_line, re.IGNORECASE):
                    if re.search('//', new_line, re.IGNORECASE):
                        new_line_2 = new_line.split("//")[0]
                    else:
                        new_line_2 = new_line
                    new_line_list = new_line_2.split(' ', 2)
                    if len(new_line_list) <= 2:
                        new_line_list.append(' ')
                    p_dict[new_line_list[1]] = new_line_list[2]

    def buildup_pid_token_dict(self):
        pid_token_list = []
        with open(self.pid_datoekn_file, "r") as pfile:
            for line in pfile:
                if SkipAction.comment(pfile, line):
                    continue
                line = line.translate({ord('{'): None, ord('}'): None, ord(','): None})
                new_line = " ".join(line.split())
                if re.match('TOKEN_', new_line, re.IGNORECASE):
                    if re.search('//', new_line, re.IGNORECASE):
                        new_line_2 = new_line.split("//")[0]
                    else:
                        new_line_2 = new_line
                    new_line_2_list = new_line_2.split(' ')
                    if len(new_line_2_list) >= 3:
                        token = new_line_2_list[0]
                        pid = new_line_2_list[2]
                        pid_already_exist = False
                        for index, cell in enumerate(pid_token_list):
                            if re.fullmatch(pid, cell):
                                pid_already_exist = True
                                break
                        if pid_already_exist:
                            pid_token_list.insert(index + 1, token)
                        else:
                            pid_token_list.append(pid)
                            pid_token_list.append(token)
        # print('+++++++++++++', pid_token_list)
        record_flag = False
        data_token = []
        for cell in pid_token_list:
            if re.match('PID_', cell, re.IGNORECASE):
                # print('&&&Pid', cell, 'record_flag', record_flag)
                if record_flag:
                    self.pid_datoken_dict[data_pid] = data_token
                record_flag = False
                data_token = []
                data_pid = cell
            if re.match('TOKEN_', cell, re.IGNORECASE):
                record_flag = True
                data_token.append(cell)
                # print('&&&token', cell, 'record_flag', record_flag)

    def get_pid_datoken_dict(self):
        return self.pid_dict, self.datoken_dict, self.pid_datoken_dict
