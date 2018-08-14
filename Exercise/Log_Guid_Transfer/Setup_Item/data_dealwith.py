import re


class DictHandle(object):
    def __init__(self):
        pass

    @staticmethod
    def extract_items(dictionary):
        items_touple = list(dictionary.items())
        items_list = [list(item) for item in items_touple]
        return items_list


class FlowControl(object):
    def __init__(self):
        self.control_flow = []

    def tag_one(self, line):
        s_line = line.strip()
        for key in ['#if ', '#ifdef', '#ifndef']:
            if re.match(key, s_line, re.IGNORECASE):
                self.control_flow.append(s_line)

    def delete_one(self):
        key = 'Unknown'
        if len(self.control_flow) != 0:
            key = self.control_flow[-1].split(' ')[0]
            del self.control_flow[-1]
        return key

    def get_record(self):
        return self.control_flow


class SkipAction(object):
    def __init__(self):
        pass

    @staticmethod
    def row(line, re_match_rule=['//'], re_search_rule=None):
        if line.isspace():
            return True
        for i in re_match_rule:
            if re.match(i, line.strip(), re.IGNORECASE):
                return True
        if re_search_rule is not None:
            for i in re_search_rule:
                if re.search(i, line, re.IGNORECASE):
                    return True
        return False

    @staticmethod
    def comment(iter_infile, line):
        line = line.replace('/*', '/* ').replace('*/', ' */ ')
        if re.match('/\*', line.strip(), re.IGNORECASE):
            if re.search('\*/', line.strip(), re.IGNORECASE):
                return True
            for next_line in iter_infile:
                next_line = next_line.replace('*/', ' */')
                if re.search('\*/', next_line.strip(), re.IGNORECASE):
                    return True
        return False

    # return: 'True', 'False'
    @staticmethod
    def check_condition_para(used_token_dict, line):
        condition_value = False
        zero_nokey_list = ['0', '0x0', 'Unknown']
        logical_list = ['==', '!=', '>=', '<=']
        s_line = line.strip()
        s_line_list = s_line.split(' ')
        # print(s_line_list)
        if len(s_line_list) == 1:
            if re.search('!', s_line, re.IGNORECASE):
                new_line = s_line.replace('!', '').strip()
                data = used_token_dict.get(new_line, 'Unknown')
                condition_value = True if data in zero_nokey_list else False
            else:
                data = used_token_dict.get(s_line, 'Unknown')
                condition_value = True if data not in zero_nokey_list else False

        if len(s_line_list) == 2:
            data = used_token_dict.get(s_line_list[1], 'Unknown')
            if re.match('!defined ', s_line, re.IGNORECASE):
                condition_value = True if data == 'Unknown' else False
            if re.match('defined ', s_line, re.IGNORECASE):
                condition_value = True if data != 'Unknown' else False

        if len(s_line_list) == 3:
            for ll in logical_list:
                if re.search(ll, s_line, re.IGNORECASE):
                    s_line_n3_list = s_line.split(ll)
                    # print('s_line_n3_list', s_line_n3_list)
                    data = used_token_dict.get(s_line_n3_list[0].strip(), 'Unknown')
                    right_data = used_token_dict.get(s_line_n3_list[1].strip(), 'Unknown')
                    if ll == '==':
                        condition_value = True if data == right_data else False
                    if ll == '!=':
                        condition_value = True if data != right_data else False
                    if ll == '>=':
                        condition_value = True if data >= right_data else False
                    if ll == '<=':
                        condition_value = True if data <= right_data else False
        return condition_value

    # return: 'No_Condition' , 'True', 'False'
    @staticmethod
    def check_line_if_status(used_token_dict, line):
        condition_value = 'No_Condition'
        line = line.replace('==', ' == ').replace('!=', ' != ').replace('>=', ' >= ').replace('<=', ' <= ')
        line = line.replace('&&', ' && ').replace('||', ' || ')
        s_line = line.strip()
        if re.match('#if ', s_line, re.IGNORECASE):
            data = s_line.replace('#if', ' ').replace('(', ' ').replace(')', ' ')
            new_line = ' '.join(data.split())

            extra_condition = new_line.count('||') + new_line.count('&&')
            # print("s_line", s_line, "extra_condition: ", extra_condition)
            if extra_condition == 0:
                condition_value = SkipAction.check_condition_para(used_token_dict, new_line)

            if extra_condition == 1:
                if re.search('\|\|', new_line, re.IGNORECASE):
                    new_line_list = new_line.split('||')
                    condition_value = False
                    for index in range(extra_condition + 1):
                        condition_value |= SkipAction.check_condition_para(used_token_dict, new_line_list[index])
                if re.search('&&', new_line, re.IGNORECASE):
                    new_line_list = new_line.split('&&')
                    condition_value = True
                    for index in range(extra_condition + 1):
                        condition_value &= SkipAction.check_condition_para(used_token_dict, new_line_list[index])

            if extra_condition == 2:
                if new_line.count('||') == 1:
                    location_1 = new_line.index('||')
                    location_2 = new_line.index('&&')
                    new_line_list = new_line.replace('||', '').replace('&&', '').split(' ')
                    if location_1 < location_2:
                        condition_value = SkipAction.check_condition_para(used_token_dict, new_line_list[0])
                        condition_value |= SkipAction.check_condition_para(used_token_dict, new_line_list[1])
                        condition_value &= SkipAction.check_condition_para(used_token_dict, new_line_list[2])
                    else:
                        condition_value = SkipAction.check_condition_para(used_token_dict, new_line_list[0])
                        condition_value &= SkipAction.check_condition_para(used_token_dict, new_line_list[1])
                        condition_value |= SkipAction.check_condition_para(used_token_dict, new_line_list[2])

                if new_line.count('||') == 2:
                    new_line_list = new_line.split('||')
                    condition_value = False
                    for index in range(extra_condition + 1):
                        condition_value |= SkipAction.check_condition_para(used_token_dict, new_line_list[index])

                if new_line.count('&&') == 2:
                    new_line_list = new_line.split('&&')
                    condition_value = True
                    for index in range(extra_condition + 1):
                        condition_value &= SkipAction.check_condition_para(used_token_dict, new_line_list[index])
        # print('condition_value', condition_value)
        return condition_value

    @staticmethod
    def none_enabled_area_if_else(iter_scope, line, used_token_dict, ext_control_flow=0):
        switch_value = 'No_Condition'
        end_line = line
        # print('skip 0', line)
        if ext_control_flow == 0:
            flow = FlowControl()
        else:
            flow = ext_control_flow
        if re.match('#if ', line.strip(), re.IGNORECASE):
            # print('skip 1', line)
            switch_value = SkipAction.check_line_if_status(used_token_dict, line)
            if not switch_value:
                local_need_endif = 0
                for next_line in iter_scope:
                    flow.tag_one(next_line)
                    if re.match('#if ', next_line.strip(), re.IGNORECASE):
                        local_need_endif += 1
                    if re.match('#else', next_line.strip(), re.IGNORECASE) and local_need_endif == 0:
                        break
                    if re.match('#endif', next_line.strip(), re.IGNORECASE):
                        flow.delete_one()
                        if local_need_endif == 0:
                            break
                        local_need_endif -= 1
                end_line = " "
        if re.search('#else', line.strip(), re.IGNORECASE) and switch_value:
            # print('skip 2', line)
            local_need_endif = 0
            for next_line in iter_scope:
                flow.tag_one(next_line)
                if re.match('#if ', next_line.strip(), re.IGNORECASE):
                    local_need_endif += 1
                if re.match('#endif', next_line.strip(), re.IGNORECASE):
                    flow.delete_one()
                    if local_need_endif == 0:
                        break
                    local_need_endif -= 1
            end_line = " "
        # print('skip 3', line)
        return end_line

    @staticmethod
    def detect_compare_type(line):
        compare_type = ['==', '>=', '<=', '!=', '>', '<']
        for c_type in compare_type:
            if re.search(c_type, line, re.IGNORECASE):
                return c_type

    @staticmethod
    def do_compare(l_value, r_value, not_flag, compare_type):
        condition_value = False
        if compare_type == '==':
            if l_value == r_value:
                condition_value = False if not_flag else True
            else:
                condition_value = True if not_flag else False
        elif compare_type == '>=':
            if l_value >= r_value:
                condition_value = False if not_flag else True
            else:
                condition_value = True if not_flag else False
        elif compare_type == '<=':
            if l_value <= r_value:
                condition_value = False if not_flag else True
            else:
                condition_value = True if not_flag else False
        elif compare_type == '!=':
            if l_value != r_value:
                condition_value = False if not_flag else True
            else:
                condition_value = True if not_flag else False
        elif compare_type == '>':
            if l_value > r_value:
                condition_value = False if not_flag else True
            else:
                condition_value = True if not_flag else False
        elif compare_type == '<':
            if l_value < r_value:
                condition_value = False if not_flag else True
            else:
                condition_value = True if not_flag else False
        return condition_value

    # return: 'True', 'False'
    @staticmethod
    def check_condition_para_suppressif(line, efi_variable, token_dict):
        compare_type = SkipAction.detect_compare_type(line)
        not_flag = False
        condition_value = False
        s_line = line.strip()
        if re.search('NOT ', s_line, re.IGNORECASE):
            not_flag = True
        if re.search('ideqval ', s_line, re.IGNORECASE):
            new_line = s_line.replace('ideqval', ' ').replace('NOT ', ' ')
            new_line = ' '.join(new_line.split())
            if re.match('SETUP_DATA.', new_line, re.IGNORECASE):
                variable_type = 0
            elif re.match('AMITSEMODE', new_line, re.IGNORECASE) or \
                    re.match('BOOT_MANAGER', new_line, re.IGNORECASE) or \
                    re.match('SETUP_AMT_FEATURES', new_line, re.IGNORECASE):
                variable_type = 1
            else:
                variable_type = 9
            new_line_2 = new_line.replace('SETUP_DATA.', ' ').replace('\\', ' ')
            new_line_2 = ' '.join(new_line_2.split())
            new_line_2_list = new_line_2.split(compare_type)
            # print('=====', new_line_2)
            if variable_type == 0:
                l_value_list = efi_variable.get_field_value(new_line_2_list[0].strip())
                l_value = str(l_value_list[0])
            elif variable_type == 1:
                other_variable_dict = efi_variable.get_other_variable_dict()
                l_value = other_variable_dict[new_line_2_list[0].strip()]
            else:
                return False
            r_value = new_line_2_list[1].strip()
            r_value = token_dict.get(r_value, 'N/A')
            condition_value = SkipAction.do_compare(l_value, r_value, not_flag, compare_type)

        if re.search('ideqvallist ', s_line, re.IGNORECASE):
            new_line = s_line.replace('ideqvallist', ' ').replace('NOT ', ' ')
            new_line = ' '.join(new_line.split())
            if re.match('SETUP_DATA.', new_line, re.IGNORECASE):
                variable_type = 0
            elif re.match('AMITSEMODE', new_line, re.IGNORECASE) or \
                    re.match('BOOT_MANAGER', new_line, re.IGNORECASE) or \
                    re.match('SETUP_AMT_FEATURES', new_line, re.IGNORECASE):
                variable_type = 1
            else:
                variable_type = 9
            new_line_2 = new_line.replace('SETUP_DATA.', ' ')
            new_line_2 = ' '.join(new_line_2.split())
            new_line_2_list = new_line_2.split('==')
            if variable_type == 0:
                l_value_list = efi_variable.get_field_value(new_line_2_list[0].strip())
                l_value = str(l_value_list[0])
            elif variable_type == 1:
                other_variable_dict = efi_variable.get_other_variable_dict()
                l_value = other_variable_dict[new_line_2_list[0].strip()]
            else:
                return False
            r_value_list = new_line_2_list[1].strip().split(' ')
            if l_value in r_value_list:
                condition_value = False if not_flag else True
                # print('=====3 condition_value=', condition_value, '***not_flag:', not_flag)
            else:
                condition_value = True if not_flag else False
                # print('=====4 condition_value=', condition_value, '***not_flag:', not_flag)
        if re.match('TRUE', s_line, re.IGNORECASE):
            condition_value = True
        # print('=====5: condition_value=', condition_value, '***not_flag:', not_flag)
        return condition_value

    @staticmethod
    def handle_and_or_link_para(link_list, para_list, link_type, new_line_copy):
        link_list.append(link_type)
        new_line_copy_list = new_line_copy.split(' ' + link_type + ' ', 1)
        para_list.append(new_line_copy_list[0])
        new_line_copy = new_line_copy_list[1]
        return link_list, para_list, new_line_copy

    # return: 'No_Condition' , 'True', 'False'
    @staticmethod
    def check_line_suppressif_status(line, efi_variable, token_dict):
        condition_value = 'No_Condition'
        link_list = []
        para_list = []
        line = line.replace('==', ' == ').replace('!=', ' != ').replace('>=', ' >= ').replace('<=', ' <= ')
        line = line.replace('&&', ' && ').replace('||', ' || ')
        s_line = line.strip()
        if re.match('suppressif ', s_line, re.IGNORECASE):
            # print('!!! go 1', s_line)
            data = s_line.replace('suppressif', ' ').replace('(', ' ').replace(')', ' ').replace(';', ' ')
            new_line = ' '.join(data.split())

            find_index = 0
            new_line_copy = new_line
            while find_index < len(new_line):
                # print('new_line_copy:', new_line_copy)
                or_location = new_line.find(' OR ', find_index)
                and_location = new_line.find(' AND ', find_index)
                if or_location == -1 and and_location != -1:
                    SkipAction.handle_and_or_link_para(link_list, para_list, 'AND', new_line_copy)
                    find_index = and_location + 1
                    continue
                elif or_location != -1 and and_location == -1:
                    SkipAction.handle_and_or_link_para(link_list, para_list, 'OR', new_line_copy)
                    find_index = or_location + 1
                    continue
                elif and_location != -1 and or_location != -1:
                    if or_location > and_location:
                        SkipAction.handle_and_or_link_para(link_list, para_list, 'AND', new_line_copy)
                        find_index = and_location + 1
                    else:
                        SkipAction.handle_and_or_link_para(link_list, para_list, 'OR', new_line_copy)
                        find_index = or_location + 1
                    continue
                else:
                    break
            if len(link_list) == 0:
                para_list.append(new_line)

            # print('link_list:', link_list)
            # print('para_list:', para_list)
            for i in range(len(para_list)):
                if i == 0:
                    condition_value = SkipAction.check_condition_para_suppressif(para_list[0], efi_variable, token_dict)
                else:
                    if link_list[i - 1] == 'OR':
                        condition_value |= SkipAction.check_condition_para_suppressif(para_list[i], efi_variable,
                                                                                      token_dict)
                    else:
                        condition_value &= SkipAction.check_condition_para_suppressif(para_list[i], efi_variable,
                                                                                      token_dict)
        # print('condition_value', condition_value)
        return condition_value

    @staticmethod
    def none_enabled_area_suppressif(target, line, efi_variable, token_dict):
        end_line = line

        if re.match('suppressif', line.strip(), re.IGNORECASE):
            # print('### enter', line.strip())
            if not re.search(';', line.strip(), re.IGNORECASE):
                for next_line in target:
                    # print(next_line)
                    line = line + ' ' + next_line.strip()
                    if re.search(';', line.strip(), re.IGNORECASE):
                        end_line = line  # merge suppressif multi lines to one line
                        break
            switch_value = SkipAction.check_line_suppressif_status(line, efi_variable, token_dict)
            # print('### switch_value', switch_value)

            if switch_value == True:    # switch can be True/False/No_Condition
                # print('### skip', line.strip())
                endif_number = 1
                for next_line in target:
                    # print(next_line)
                    if re.match('suppressif', next_line.strip(), re.IGNORECASE):
                        endif_number += 1
                    if re.match('grayoutif', next_line.strip(), re.IGNORECASE):
                        endif_number += 1
                    if re.match('endif', next_line.strip(), re.IGNORECASE):
                        endif_number -= 1
                    if re.match('SUPPRESS_GRAYOUT_ENDIF', next_line.strip(), re.IGNORECASE):
                        endif_number -= 2
                    if endif_number == 0:
                        end_line = " "
                        break
        # print('### leave', end_line)
        return end_line


class SdDealWith(object):
    def __init__(self, sd_file_list, token_dict):
        self.file_list = sd_file_list
        self.token_dict = token_dict
        self.active_information = []
        self.define_list = []
        self.formid_list = []
        self.buildup_active_information()

    def get_active_information(self):
        return self.active_information

    def get_define_formid_list(self):
        return self.define_list, self.formid_list

    def buildup_active_information(self):
        flow_control = FlowControl()
        self.active_information = []
        re_match_skip = ['//', 'SEPARATOR']
        for sd_file in self.file_list:
            with open(sd_file, "r") as infile:
                iter_infile = iter(infile)
                for line in iter_infile:
                    if SkipAction.row(line, re_match_skip) or SkipAction.comment(iter_infile, line):
                        continue
                    # Clear comment //
                    line = line.replace('//', ' // ').split('//')[0]
                    line = line.replace('#if(', '#if (')

                    flow_control.tag_one(line)
                    line = SkipAction.none_enabled_area_if_else(iter_infile, line, self.token_dict, flow_control)
                    if re.match('#if ', line.strip(), re.IGNORECASE):
                        continue
                    if re.match('#else', line.strip(), re.IGNORECASE):
                        continue
                    if re.match('#endif', line.strip(), re.IGNORECASE):
                        key = flow_control.delete_one()
                        if key == '#if':
                            continue
                    if re.search('AUTO_ID', line.strip(), re.IGNORECASE):
                        line = line.replace('AUTO_ID', '').replace('(', '').replace(')', '')
                    line = line.replace('\n', '').replace('\\', ' ').replace(',', '')
                    self.active_information.append(line)

    def renew_active_information_with_new_token_dict(self, token_dict):
        self.token_dict = token_dict
        self.buildup_active_information()

    def information_renew_with_suppressif(self, efi_variable):
        new_info = []
        target_info_iter = iter(self.active_information)
        for line in target_info_iter:
            if SkipAction.row(line.strip()):
                continue
            line = SkipAction.none_enabled_area_suppressif(target_info_iter, line, efi_variable, self.token_dict)
            new_info.append(line)
        self.active_information = new_info

    def buildup_define_and_formid(self):
        self.gather_all_define_or_formid('define')
        self.gather_all_define_or_formid('formid')
        self.transfer_include_node_file()

    def gather_all_define_or_formid(self, key='define'):
        record = False
        focus_key = 'form formid'
        stop_key = 'endform'
        if key == 'define':
            focus_key = '#define'
            stop_key = '#'
            focus_key_list = self.define_list
        else:
            focus_key_list = self.formid_list

        for line in self.active_information:
            if SkipAction.row(line.strip()):
                continue
            if re.match(stop_key, line.strip(), re.IGNORECASE):
                if stop_key == 'endform':
                    focus_key_list.append(line)
                record = False
            if re.match(focus_key, line.strip(), re.IGNORECASE):
                record = True
            if record:
                focus_key_list.append(line)
        return focus_key_list

    def gather_focus_one_ifdef(self, focus_key='DELL_SETUP_GENERAL_BATTERY_INFO'):
        key_context_list = []
        iter_target = iter(self.active_information)
        for line in iter_target:
            if not re.match('#ifdef ', line.strip(), re.IGNORECASE):
                continue
            line = ' '.join(line.split())
            line_list = line.split(' ')
            if re.search(focus_key, line_list[1], re.IGNORECASE) and len(focus_key) == len(line_list[1]):
                local_control_flow = FlowControl()
                local_control_flow.tag_one(line)
                for next_line in iter_target:
                    local_control_flow.tag_one(next_line)
                    if re.match('#endif', next_line.strip(), re.IGNORECASE):
                        key = local_control_flow.delete_one()
                        if key == '#if':
                            continue
                        if len(local_control_flow.get_record()) == 0:
                            return key_context_list
                    key_context_list.append(next_line.replace('\n', ''))
        return key_context_list

    def transfer_include_node_file(self):
        new_target = []
        for index, line in enumerate(self.formid_list):
            if re.match("#define", line.strip(), re.IGNORECASE):
                line_2 = self.formid_list[index + 1]  # line.isspace()
                if re.match("#include", line_2.strip(), re.IGNORECASE):
                    line_3 = self.formid_list[index + 2]
                    if re.match("#undef", line_3.strip(), re.IGNORECASE):
                        new_line_3 = " ".join(line_3.split())
                        key = new_line_3.split(' ')[1]
                        sub_p = self.gather_focus_one_ifdef(key)
                        del self.formid_list[index + 2]
                        del self.formid_list[index + 1]
                        del self.formid_list[index]
                        for i in reversed(sub_p):
                            self.formid_list.insert(index, i)
                        self.formid_list.insert(index, ' ')
                        continue
            new_target.append(line)
        self.formid_list = new_target
