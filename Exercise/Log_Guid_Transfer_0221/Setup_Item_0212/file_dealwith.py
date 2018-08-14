import re


class FileDealWith(object):
    output_folder = ''
    oem_folder = ''
    override_priority_list = []         # priority [1] > [0]

    def __init__(self, original_file_list, original_file_list_name=0, active_override_file_list_name=0,
                       remove_file_list_name=0, active_file_list_name=0):
        self.original_file_list = original_file_list
        self.active_file_dict = {}
        self.active_file_list = []
        self.active_override_file_list = []
        self.remove_file_list = []
        self.buildup()
        if original_file_list_name != 0:
            FileDealWith.write_list_to_file(self.original_file_list, original_file_list_name)
        if active_override_file_list_name != 0:
            FileDealWith.write_list_to_file(self.active_override_file_list, active_override_file_list_name)
        if remove_file_list_name != 0:
            FileDealWith.write_list_to_file(self.remove_file_list, remove_file_list_name)
        if active_file_list_name != 0:
            FileDealWith.write_list_to_file(self.active_file_list, active_file_list_name)

    def get_active_file_list(self):
        return self.active_file_list

    @classmethod
    def get_priority_number(cls, filepath):
        override_priority = 0
        if re.search(cls.override_priority_list[0], filepath, re.IGNORECASE):
            override_priority = 16
            if re.search(cls.override_priority_list[1], filepath, re.IGNORECASE):
                override_priority = 32
        return override_priority

    def buildup(self):
        all_override_file_list = [i for i in self.original_file_list if re.search('override', i, re.IGNORECASE)]
        # produce active_override_file_list
        for data in all_override_file_list:
            data_list = data.split('\\')
            filename = data_list[-1]
            same_filename_priority = [self.get_priority_number(aof) for aof in all_override_file_list
                                      if re.search(filename, aof, re.IGNORECASE)]
            if self.get_priority_number(data) >= max(same_filename_priority):
                self.active_override_file_list.append(data)
        # produce remove_file_list
        same_filename_dict = {}
        for f in self.active_override_file_list:
            key = f.split('\\')
            for data in self.original_file_list:
                if re.search(key[-1], data, re.IGNORECASE):
                    same_filename_dict[data] = 1
        for i in self.active_override_file_list:
            del same_filename_dict[i]
        self.remove_file_list = list(same_filename_dict.keys())
        # produce active_file_list
        for i in self.original_file_list:
            self.active_file_dict[i] = 1
        for i in self.remove_file_list:
            del self.active_file_dict[i]
        self.active_file_list = list(self.active_file_dict.keys())

    @classmethod
    def update_output_folder(cls, output_folder, oem_folder):
        print(' go p1')
        cls.output_folder = output_folder
        cls.oem_folder = oem_folder
        print(' go p2')
        if re.search('/', cls.oem_folder, re.IGNORECASE):
            data_list = cls.oem_folder.replace('/', ' ').split(' ')
        else:
            data_list = cls.oem_folder.replace('\\', ' ').split(' ')
        print(' go p3')
        print(data_list)
        print('-2:', data_list[-2])
        print('-1:', data_list[-1])
        cls.override_priority_list = [data_list[-2], data_list[-1]]
        print(' go p4')

    @classmethod
    def write_list_to_file(cls, w_list, w_file, encoding_mode=0):
        if cls.output_folder == '':
            w_path_file = w_file
        else:
            w_path_file = cls.output_folder + '\\' + w_file
        if encoding_mode == 0:
            mode = 'utf-8'
        else:
            mode = encoding_mode
        with open(w_path_file, "w", encoding=mode) as wf:
            for list_d in w_list:
                if isinstance(list_d, list):
                    for cell in list_d:
                        if isinstance(cell, list):
                            for sub_cell in cell:
                                wf.write(str(sub_cell) + ' ')
                        else:
                            wf.write(str(cell) + ' ')
                    wf.write('\n')
                else:
                    wf.write(list_d + '\n')
