import re


class SetupTreeData(object):

    def __init__(self, token_dict, gstring_dict, gset_dict, pid_dict, pid_token_dict, datoken_dict):
        self.token_dict = token_dict
        self.gstring_dict = gstring_dict
        self.gset_dict = gset_dict
        self.pid_dict = pid_dict
        self.pid_token_dict = pid_token_dict
        self.datoken_dict = datoken_dict

    def output_in_list(self, layer_list, total_key):
        total_table = []
        layer_line = 0
        l_layer = layer_list[layer_line]
        l_count = self.gset_dict[l_layer]  # layer_L0
        l_layer_index = total_key.index(l_layer)
        print('l_layer:', l_layer)
        print('l_count:', l_count)

        for l_loop in range(l_count):
            l_layer_index += 1
            print('l_layer_index in total_key:', l_layer_index)

            id_string = self.gset_dict[total_key[l_layer_index]]
            row_data = self.handle_layer_l_a(id_string, 'L')
            total_table.append(row_data)

            layer_line += 1
            # print('-----', layer_line, len(layer_list))
            if layer_line == len(layer_list):
                break
            a_layer = layer_list[layer_line]
            a_count = self.gset_dict[a_layer]  # layer_L0_A0
            a_layer_index = total_key.index(a_layer)
            form_s_index = a_layer_index + 1
            print('a_layer:', a_layer)
            print('a_count:', a_count)
            print('a_layer_index in total_key:', a_layer_index)

            for index in range(a_count):
                key = total_key[form_s_index + index]
                data = self.gset_dict[key]
                print('@@@@ key =', key, 'data =', data)
                if isinstance(data, list):
                    print('&&&& key =', key, '&&&& data =', data)
                    row_data = self.handle_layer_b(key)
                    total_table.append(row_data)
                else:
                    print('Correct ID #### key =', key, '#### data =', data)
                    row_data = self.handle_layer_l_a(data, 'A')
                    total_table.append(row_data)
                layer_line += 1

                layer_name = layer_list[layer_line]
                b_layer_count = self.gset_dict[layer_name]
                print('##### layer_name:', layer_name, 'count:', b_layer_count)
                t_index = total_key.index(layer_name)

                for i in range(1, b_layer_count + 1):  # layer_L0_A0_B0, B1 .....
                    if (t_index + i) < len(total_key):  # todo why need this
                        data = total_key[t_index + i]
                        row_data = self.handle_layer_b(data)
                        # Skip empty row data
                        if row_data[0] == '' and row_data[1] == '' and row_data[2] == '':
                            continue
                        total_table.append(row_data)
        return total_table

    def handle_layer_l_a(self, id_string, layer='L'):
        first_layer = ''
        second_layer = ''
        node = ''
        node_type = ''
        default_value = ''
        pid_n = ''
        pid_v = ''
        tokenid_n = []
        tokenid_v = []

        # Fix #define STR_DELL_QUIET_TITLE STRING_TOKEN(STR_DELL_STEALTH_TITLE) define to anoter string issue.
        data = self.token_dict.get(id_string, 'N/A')
        if data != 'N/A':
            data = data.replace('STRING_TOKEN', '').replace('(', '').replace(')', '')
            id_string = " ".join(data.split())

        # print('===id_string:', id_string)
        if layer == 'L':
            first_layer = self.gstring_dict.get(id_string, 'Todo')
        else:
            second_layer = self.gstring_dict.get(id_string, 'Todo')

        row_data = (first_layer, second_layer, node, node_type, default_value, pid_n,
                    pid_v, tokenid_n, tokenid_v)
        return row_data

    def handle_layer_b(self, key):
        first_layer = ''
        second_layer = ''
        node = ''
        node_type = ''
        default_value = ''
        pid_n = ''
        pid_v = ''
        tokenid_n = []
        tokenid_v = []

        # print('===', key)
        if re.match('TEXT~', key, re.IGNORECASE):
            # [help_string, text_string]
            data_list = self.gset_dict[key]
            node = self.gstring_dict[data_list[0]]
            if node == '':
                text_string_list = data_list[1]
                node = self.gstring_dict[text_string_list[0]]
            node_type = 'text'

        if re.match('inventory_', key, re.IGNORECASE):
            # ['value'] value will be updated during POST
            new_key = key.replace("INVENTORY_", '')
            if re.search('^', new_key, re.IGNORECASE):
                new_key = new_key.split('^')[0].strip()
            node = self.gstring_dict[new_key]
            node_type = 'inventory'
        if re.match('interactive_', key, re.IGNORECASE):
            # ['node_help', 'node_name', 'node_value']
            data_list = self.gset_dict[key]
            node = self.gstring_dict[data_list[1]]
            node_type = 'interactive'
        if re.match('time~', key, re.IGNORECASE):
            # [prompt, help, default]
            data_list = self.gset_dict[key]
            node = self.gstring_dict[data_list[0]]
            node_type = 'time'
            default_value = data_list[-1]
        if re.match('oneof~', key, re.IGNORECASE):
            # [prompt, help, pid, dell_special_pid, option_list]
            data_list = self.gset_dict[key]
            node_type = 'oneof'
            node, pid_n, pid_v, tokenid_n, tokenid_v = self.handle_node_pid_token(data_list)
            option_list = data_list[-1]
            for index, value in enumerate(option_list):
                if re.match('DEFAULT', str(value), re.IGNORECASE):
                    default_value = str(option_list[index-1])
        if re.match('checkbox~', key, re.IGNORECASE):
            # [prompt, help, pid, dell_special_pid, default]
            data_list = self.gset_dict[key]
            node_type = 'checkbox'
            node, pid_n, pid_v, tokenid_n, tokenid_v = self.handle_node_pid_token(data_list)
            default_value = data_list[-1]
        if re.match('numeric~', key, re.IGNORECASE):
            # [prompt, help, pid, default, min, max, step]
            data_list = self.gset_dict[key]
            node_type = 'numeric'
            # print('%%%%%%%%', data_list)
            node, pid_n, pid_v, tokenid_n, tokenid_v = self.handle_node_pid_token(data_list)
            default_value = data_list[-1]
        if re.match('password~', key, re.IGNORECASE):
            # [prompt, help, pid, key, minsize, maxsize, ecoding]
            data_list = self.gset_dict[key]
            node_type = 'password'
            node, pid_n, pid_v, tokenid_n, tokenid_v = self.handle_node_pid_token(data_list)
        if re.match('string~', key, re.IGNORECASE):
            # [prompt, help, pid, key, minsize, maxsize]
            data_list = self.gset_dict[key]
            node_type = 'string'
            node, pid_n, pid_v, tokenid_n, tokenid_v = self.handle_node_pid_token(data_list)

        row_data = (first_layer, second_layer, node, node_type, default_value, pid_n,
                    pid_v, tokenid_n, tokenid_v)
        return row_data

    def handle_node_pid_token(self, data_list):
        pid_name = 'N/A'
        pid_value = 'N/A'
        token_id_name = []
        token_id_value = []

        node = self.gstring_dict.get(data_list[0], 'todo')
        # Fix #define STR_DELL_QUIET_TITLE STRING_TOKEN(STR_DELL_STEALTH_TITLE) define to anoter string issue.
        if node == 'todo':
            data = self.token_dict.get(data_list[0], 'N/A')
            if data != 'N/A':
                data = data.replace('STRING_TOKEN', '').replace('(', '').replace(')', '')
                new_data = " ".join(data.split())
                node = self.gstring_dict.get(new_data, 'todo')
        # todo
        if len(data_list) >= 3 and data_list[2] != 'Unknown':
            pid_name = data_list[2]
            pid_value = self.pid_dict.get(pid_name, 'N/A')
            token_id_name = self.pid_token_dict.get(pid_name, 'N/A')
            if token_id_name != 'N/A':
                for token_name in token_id_name:
                    token_value = self.datoken_dict.get(token_name, 'N/A')
                    token_id_value.append(token_value)
        return node, pid_name, pid_value, token_id_name, token_id_value

    @staticmethod
    def show_layer(target_dict, layer, node_name):
        target_key = list(target_dict.keys())
        s_point = target_key.index(layer) + 1
        length = target_dict[layer]
        sub_key = target_key[s_point:s_point+length]
        print('Start index in gset_dict:', s_point, '|| Length:', length)
        print("Target key:", sub_key)
        for i in sub_key:
            print(target_dict[i])
        print('*****', layer, '=', node_name, 'End')
