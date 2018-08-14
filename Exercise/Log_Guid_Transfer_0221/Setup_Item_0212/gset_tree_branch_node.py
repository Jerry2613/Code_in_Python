import re
from Transfer_Guid_To_Name import FileLocation
from setup_tree_data import SetupTreeData
from data_dealwith import SdDealWith, FlowControl, SkipAction
from file_dealwith import FileDealWith


class GsetTree(object):

    def __init__(self, p_folder, token_dict, efi_variable, sd_formid_list, sd_define_list):
        self.folder = p_folder
        self.token_dict = token_dict
        self.efi_variable = efi_variable
        self.formid_list = sd_formid_list
        self.define_list = sd_define_list
        self.gset_dict = {}
        self.layer_list = []
        self.duplicate_item_account_dict = {}

        self.walk_through_setup()

    def get_gsetdict_layerlist(self):
        return self.gset_dict, self.layer_list

    def walk_through_setup(self):
        self.layer_list.append("Layer_L0")

        gset = FileLocation()
        gset.root_path = self.folder
        gset.gather_target_files('DellSetup.sd')
        main = FileDealWith(gset.target_files)
        target_file = main.get_active_file_list()

        with open(target_file[0], "r") as main_form:
            self.catch_mainform_goto(main_form, "SYS_INFO_FORM_ID")
        SetupTreeData.show_layer(self.gset_dict, "Layer_L0", 'main_form')

        # walk through all branch
        total_key = list(self.gset_dict.keys())
        for l_index in range(self.gset_dict["Layer_L0"]):
            t_index = total_key.index("Layer_L0") + l_index + 1
            self.dealwith_page(t_index, "Layer_L0_A" + str(l_index))

    def catch_mainform_goto(self, target, stop_flag='None'):
        gset_main = GsetNode(self.token_dict)
        iter_target = iter(target)

        for line in iter_target:
            s_line = line.strip()
            if SkipAction.row(s_line) or SkipAction.comment(iter_target, line):
                continue
            if stop_flag != 'None' and re.search(stop_flag, s_line, re.IGNORECASE):
                break
            SkipAction.none_enabled_area_if_else(iter_target, s_line, self.token_dict)
            SkipAction.none_enabled_area_suppressif(iter_target, s_line, self.efi_variable, self.token_dict)
            gset_main.has_go_prompt_inventory(s_line)

        m_id, m_prompt = gset_main.get_id_prompt()
        self.gset_dict["Layer_L0"] = len(m_id)
        for index in range(len(m_id)):
            self.gset_dict[m_id[index]] = m_prompt[index]

    def dealwith_page(self, t_index, layer_title):
        gset_node = GsetNode(self.token_dict)
        total_key = list(self.gset_dict.keys())
        m_id, m_prompt = self.dealwith_setupdefinitions(total_key[t_index], gset_node)

        self.layer_list.append(layer_title)
        self.gset_dict[layer_title] = len(m_prompt)
        for index in range(len(m_id)):
            self.gset_dict[m_id[index]] = m_prompt[index]
        total_key = list(self.gset_dict.keys())
        SetupTreeData.show_layer(self.gset_dict, layer_title, total_key[t_index])

        sub_layer = layer_title + '_B'
        for i in range(self.gset_dict[layer_title]):
            t_index = total_key.index(layer_title) + 1 + i
            print('***** ' + sub_layer + str(i) + ' =', total_key[t_index], 'Start *****')
            # If this is a node on layer A. code don't need to extend layer B node. 
            if re.search('~', total_key[t_index], re.IGNORECASE):
                # print('====', total_key[t_index])
                continue
            m_id, m_prompt = self.dealwith_setupdefinitions(total_key[t_index], gset_node)
            self.layer_list.append(sub_layer + str(i))
            self.gset_dict[self.layer_list[-1]] = len(m_prompt)
            length = len(m_id)
            for index in range(length):
                keys = self.gset_dict.keys()
                if m_id[index] in keys:
                    value = self.duplicate_item_account_dict.get(m_id[index], str(0))
                    value += str(1)
                    self.duplicate_item_account_dict[m_id[index]] = value
                    self.gset_dict[m_id[index] + '^' + value] = m_prompt[index]
                else:
                    self.gset_dict[m_id[index]] = m_prompt[index]
            total_key = list(self.gset_dict.keys())
            SetupTreeData.show_layer(self.gset_dict, sub_layer + str(i), total_key[t_index])

    def dealwith_setupdefinitions(self, form_id_key, gset_node):
        gset_node.reset_id_prompt()
        formid_list_iter = iter(self.formid_list)  # list is not iterator do this to make list sequencily output.
        for line in formid_list_iter:
            if re.search('form formid', line, re.IGNORECASE):
                line_list = " ".join(line.split()).split('=')
                if re.fullmatch(form_id_key, line_list[1].strip(), re.IGNORECASE):
                    # print(line)
                    # Todo
                    for next_line in formid_list_iter:
                        s_next_line = next_line.strip()
                        gset_node.has_go_prompt_inventory(s_next_line)
                        gset_node.has_interactive_text(formid_list_iter, s_next_line)
                        next_line = gset_node.has_text_node(formid_list_iter, s_next_line)
                        s_next_line = next_line.strip()
                        has_setup_node = self.has_setup_node(formid_list_iter, s_next_line, gset_node)
                        if has_setup_node == 'Yes':
                            continue
                        if re.match("endform", s_next_line, re.IGNORECASE):
                            return gset_node.get_id_prompt()
        return gset_node.get_id_prompt()

    def has_setup_node(self, formid_list_iter, line, gset_node):
        skip_string_list = ['#endif', 'endform', 'endif', 'endoneof', 'endcheckbox', 'endnumeric',
                            'SUPPRESS_GRAYOUT_ENDIF']
        type_list = ['oneof', 'checkbox', 'numeric', 'string', 'year', 'hour', 'password']
        new_line = line.replace('(', ' ').replace(')', ' ')
        new_line = " ".join(new_line.split())
        line_list = new_line.split(' ')
        raw_para_list = []
        has_setup_node = 'None'
        if SkipAction.row(line, skip_string_list):
            return has_setup_node

        # setup items declare with MACRO
        if len(line_list) == 1 and len(new_line) != 0:
            # print('!!!!', len(new_line), len(line_list), new_line)
            raw_para_list = self.get_focus_define(line_list[0])
            if len(raw_para_list) >= 1:
                raw_para_list.insert(0, 'node')
                has_setup_node = 'Yes'

        # print('$$$$$$$',new_line)
        if re.search('questionid', new_line, re.IGNORECASE):
            new_line = new_line.split('questionid')[0]

        # setup items directly declare
        for n_type in type_list:
            node_start = n_type + ' varid'
            if n_type == 'year':
                node_end = 'enddate'
            elif n_type == 'hour':
                node_end = 'endtime'
            else:
                node_end = 'end' + n_type

            if re.match(node_start, new_line, re.IGNORECASE):
                raw_para_list.append(new_line)
                raw_para_list = self.get_focus_node(formid_list_iter, raw_para_list, node_end)
                raw_para_list.insert(0, 'node')
                break

        if raw_para_list:
            para_list, n_type = gset_node.pure_node_list_and_get_type(raw_para_list)
            has_setup_node = 'Yes'
            # print("======================", type,  para_list)
            if n_type == 'oneof':
                gset_node.dealwith_oneof(para_list)
            if n_type == 'checkbox':
                gset_node.dealwith_checkbox(para_list)
            if n_type == 'year' or n_type == 'hour':
                gset_node.dealwith_date_time(para_list, n_type)
            if n_type == 'numeric':
                gset_node.dealwith_numeric(para_list)
            if n_type == 'password':
                gset_node.dealwith_password(para_list)
            if n_type == 'string':
                gset_node.dealwith_string(para_list)
        return has_setup_node

    def get_focus_define(self, focus_key):
        focus_key_list = []
        record = False
        for line in self.define_list:
            if SkipAction.row(line.strip()):
                continue
            if re.match('#define', line.strip(), re.IGNORECASE):
                if record:
                    break
                new_line = " ".join(line.split())
                key = new_line.split(' ')[1]
                if re.fullmatch(focus_key, key, re.IGNORECASE):
                    record = True
            if record:
                focus_key_list.append(line)
        return focus_key_list

    def get_focus_node(self, formid_list_iter, raw_para_list, stop_key):
        for line in formid_list_iter:
            line = " ".join(line.split())
            if SkipAction.row(line.strip()):
                continue
            raw_para_list.append(line)
            if re.match(stop_key, line.strip(), re.IGNORECASE):
                for next_line in formid_list_iter:
                    if not re.search('dell', next_line.strip(), re.IGNORECASE):
                        break
                    raw_para_list.append(next_line)
                break
        return raw_para_list


class GsetNode(object):

    def __init__(self, token_dict):
        self.token_dict = token_dict
        self.form_id = []
        self.form_prompt = []
        self.text_node_number = 0
        self.dell_special_key = ['dell_field_attrib', 'dell_suppress_pid', 'dell_grayout_pid', 'dell_ignore_default']
        self.prompt = 0
        self.help_s = 0
        self.pid = 'None'
        self.key = 0
        self.minsize = 0
        self.maxsize = 0
        self.minimum = 0
        self.maximum = 0
        self.ecoding = 0
        self.default = 0
        self.step = 0
        self.dell_special_items = []

    def reset_id_prompt(self):
        self.form_id = []
        self.form_prompt = []

    def get_id_prompt(self):
        return self.form_id, self.form_prompt

    def has_goto(self, line):
        if re.match('goto', line.strip(), re.IGNORECASE):
            return line.replace(',', '').split(' ')[1]
        return False

    def has_prompt(self, line):
        if re.match('prompt', line.strip(), re.IGNORECASE):
            new_line_1 = line.split('/*')[0]
            new_line_2 = new_line_1.replace(')', ' ').replace('(', ' ').replace(',', ' ')
            new_line_3 = " ".join(new_line_2.split())
            return new_line_3.split(' ')[-1]
        return False

    def has_inventory(self, line):
        node = []  # node[0]= Prompt, node[1]= value
        if re.match('INVENTORY', line, re.IGNORECASE):
            new_line = line.replace('STRING_TOKEN', ' ').replace('(', '').replace(')', '')
            new_line = " ".join(new_line.split())
            new_line_list = new_line.split(' ')
            node.append(new_line_list[1])
            node.append(new_line_list[2])
            return node
        return False

    def has_go_prompt_inventory(self, line):
        msg = self.has_goto(line)
        if msg != False:
            self.form_id.append(msg)
            return
        msg = self.has_prompt(line)
        if msg != False:
            self.form_prompt.append(msg)
            return
        data_list = self.has_inventory(line)
        if data_list != False:
            self.form_id.append('INVENTORY_' + str(data_list[0]))
            self.form_prompt.append(data_list[1])
            return

    def has_interactive_text(self, iter_scope, line):
        # i_node[0]= STR_BATTERY_TOTAL_COUNT_HELP, i_node[1]= STR_BATTERY_TOTAL_COUNT
        # i_node[2]= STR_BATTERY_TOTAL_COUNT_VALUE, i_node[2]= BATTERY_KEY_COUNT
        if re.match('INTERACTIVE_TEXT', line.strip(), re.IGNORECASE):
            line_list = self.pure_line(line).split(' ')
            i_node = [line_list[i] for i in range(len(line_list))]
            if len(i_node) == 4:
                self.form_id.append("INTERACTIVE_" + i_node[3])
                self.form_prompt.append(i_node[:3])
                return
            for next_line in iter_scope:
                line_list = self.pure_line(next_line).split(' ')
                for i in range(len(line_list)):
                    i_node.append(line_list[i])
                    if len(i_node) == 4:
                        self.form_id.append("INTERACTIVE_" + i_node[3])
                        self.form_prompt.append(i_node[:3])
                        return

    def has_text_node(self, iter_scope, line):
        if re.fullmatch('text', line.strip(), re.IGNORECASE):
            # print('##### text_node', text_node_number, line)
            self.form_id.append('TEXT~' + str(self.text_node_number))
            self.text_node_number += 1
            help_string = 'None'
            text_string = []

            for next_line in iter_scope:
                if not re.search('=', next_line.strip(), re.IGNORECASE):
                    break
                next_line = next_line.replace('STRING_TOKEN', ' ').replace('(', ' ').replace(')', ' ')
                new_next_line = " ".join(next_line.split())
                new_next_line_list = new_next_line.split(' ')
                # print(new_next_line_list)
                if re.match('help', new_next_line_list[0], re.IGNORECASE):
                    help_string = new_next_line_list[2]
                if re.match('text', new_next_line_list[0], re.IGNORECASE):
                    text_string.append(new_next_line_list[2])
            data = [help_string, text_string]
            self.form_prompt.append(data)
            line = next_line
            # print('####id prompt', form_id, form_prompt)
        return line

    def pure_line(self, line):
        removing_string = ['INTERACTIVE_TEXT', 'STRING_TOKEN', '(', ')']  # jdebug ';'
        for rs in removing_string:
            line = line.replace(rs, ' ')
        new_line = ' '.join(line.split())
        return new_line

    def pure_node_list_and_get_type(self, p_list):
        node_type = 'None'
        new_list = []
        type_list = ['oneof', 'checkbox', 'numeric', 'string', 'year', 'hour', 'password']
        for line in p_list:
            new_line = self.pure_line(line)
            new_list.append(new_line)
            for type_n in type_list:
                if re.match(type_n + ' varid', new_line, re.IGNORECASE):
                    node_type = type_n
        return new_list, node_type

    def dealwith_oneof(self, para_list):
        option = []
        value = 'None'
        second_varid = False
        self.dell_special_items = []
        for p_line in para_list:
            if re.match('oneof varid', p_line, re.IGNORECASE):
                if re.search('questionid', p_line, re.IGNORECASE):
                    p_line = p_line.split('questionid')[0].strip()
                self.form_id.append('ONEOF~' + p_line.split('=')[1].strip())
                if second_varid:
                    r_data = [self.prompt, self.help_s, self.pid, option]
                    self.form_prompt.append(self.insert_dell_s_pid(r_data))
                second_varid = True
            self.common_match(p_line)
            if re.match('option', p_line, re.IGNORECASE):
                p_line = p_line.replace('=', ' = ')
                p_line = " ".join(p_line.split())
                p_list = p_line.split(' ')
                option.append(p_list[3].strip())
                data = self.token_dict.get(p_list[6], 'None')
                option.append(data)
                option.append('DEFAULT') if value == p_list[6].strip() else option.append(p_list[9].strip())
            if re.match('default', p_line, re.IGNORECASE):
                key = p_line.split('=')[1].strip()
                value = self.token_dict.get(key, 'None').replace('0x', '').strip()
                if value != None:
                    for i in range(1, len(option), 3):
                        if option[i] == value:
                            option[i + 1] = 'DEFAULT'
                            break
        r_data = [self.prompt, self.help_s, self.pid, option]
        self.form_prompt.append(self.insert_dell_s_pid(r_data))

    def dealwith_checkbox(self, para_list):
        second_varid = False
        self.dell_special_items = []
        for p_line in para_list:
            if re.match('checkbox varid', p_line, re.IGNORECASE):
                self.form_id.append('CHECKBOX~' + p_line.split('=')[1].strip())
                if second_varid:
                    r_data = [self.prompt, self.help_s, self.pid, self.default]
                    self.form_prompt.append(self.insert_dell_s_pid(r_data))
                second_varid = True
            self.common_match(p_line)
        r_data = [self.prompt, self.help_s, self.pid, self.default]
        self.form_prompt.append(self.insert_dell_s_pid(r_data))

    def dealwith_date_time(self, para_list, n_type):
        datetime = []
        default = []
        self.form_id.append('TIME~' + n_type)
        para_list_iter = iter(para_list)
        for p_line in para_list_iter:
            if re.match('prompt', p_line, re.IGNORECASE):
                datetime.append(p_line.split('=')[1].strip())
            if re.match('help', p_line, re.IGNORECASE):
                datetime.append(p_line.split('=')[1].strip())
            if re.search('default', p_line, re.IGNORECASE):
                data = p_line.split('default')[1].split('=')[1].strip()
                default.append(data)
                for next_line in para_list_iter:
                    if re.search('default', next_line, re.IGNORECASE):
                        data = next_line.split('default')[1].split('=')[1].strip()
                        default.append(data)
                datetime.append(default)
        self.form_prompt.append(datetime)

    def dealwith_numeric(self, para_list):
        second_varid = False
        self.dell_special_items = []
        for p_line in para_list:
            if re.match('numeric varid', p_line, re.IGNORECASE):
                self.form_id.append('NUMERIC~' + p_line.split('=')[1].strip())
                if second_varid:
                    r_data = [self.prompt, self.help_s, self.pid, self.minimum, self.maximum, self.step, self.default]
                    self.form_prompt.append(self.insert_dell_s_pid(r_data))
                second_varid = True
            self.common_match(p_line)
        r_data = [self.prompt, self.help_s, self.pid, self.minimum, self.maximum, self.step, self.default]
        self.form_prompt.append(self.insert_dell_s_pid(r_data))

    def dealwith_password(self, para_list):
        self.dell_special_items = []
        for p_line in para_list:
            if re.match('password varid', p_line, re.IGNORECASE):
                self.form_id.append('PASSWORD~' + p_line.split('=')[1].strip())
            self.common_match(p_line)
        r_data = [self.prompt, self.help_s, self.pid, self.key, self.minsize, self.maxsize, self.ecoding]
        self.form_prompt.append(self.insert_dell_s_pid(r_data))

    def dealwith_string(self, para_list):
        self.dell_special_items = []
        for p_line in para_list:
            if re.match('string varid', p_line, re.IGNORECASE):
                self.form_id.append('STRING~' + p_line.split('=')[1].strip())
            self.common_match(p_line)
        r_data = [self.prompt, self.help_s, self.pid, self.key, self.minsize, self.maxsize]
        self.form_prompt.append(self.insert_dell_s_pid(r_data))

    def insert_dell_s_pid(self, r_data):
        if self.dell_special_items:
            for item in self.dell_special_items:
                r_data.insert(3, item)
        return r_data

    def common_match(self, p_line,):
        if re.match('prompt', p_line, re.IGNORECASE):
            self.prompt = p_line.split('=')[1].strip()
        if re.match('help', p_line, re.IGNORECASE):
            self.help_s = p_line.split('=')[1].strip()
        if re.match('dell_pid', p_line, re.IGNORECASE):
            p_list = p_line.split(' ')
            self.pid = p_list[1]
        if re.match('key', p_line, re.IGNORECASE):
            self.key = p_line.split('=')[1].strip()
        if re.match('minsize', p_line, re.IGNORECASE):
            self.minsize = p_line.split('=')[1].strip()
        if re.match('maxsize', p_line, re.IGNORECASE):
            self.maxsize = p_line.split('=')[1].strip()
        if re.match('minimum', p_line, re.IGNORECASE):
            self.minimum = p_line.split('=')[1].strip()
        if re.match('maximum', p_line, re.IGNORECASE):
            self.maximum = p_line.split('=')[1].strip()
        if re.match('ecoding', p_line, re.IGNORECASE):
            self.ecoding = p_line.split('=')[1].strip()
        if re.match('default', p_line, re.IGNORECASE):
            dkey = p_line.split('=')[1].strip()
            self.default = self.token_dict.get(dkey, 'None')
        if re.match('step', p_line, re.IGNORECASE):
            self.step = p_line.split('=')[1].strip()
        for dell_s in self.dell_special_key:
            if re.match(dell_s, p_line, re.IGNORECASE):
                self.dell_special_items.append(p_line.strip().replace(' ', ':'))
