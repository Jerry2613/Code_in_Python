import re
from data_dealwith import DataSave


class FileDealWith(object):

    def __init__(self, o_folder, p_folder, original_file_list, o_file_name=0):
        self.original_file_list = original_file_list
        self.active_file_dict = {}
        self.active_file_list = []
        self.active_override_file_list = []
        self.remove_file_list = []
        self.o_folder = o_folder
        self.p_folder = p_folder

        data_list = self.p_folder.replace('/', ' ').replace('\\', ' ').split(' ')
        # priority [1] > [0]
        self.override_priority_list = [data_list[-2], data_list[-1]]

        self.buildup()

        if o_file_name != 0:
            DataSave.list_to_txt(self.original_file_list, o_folder, o_file_name + '_origin.txt')
            DataSave.list_to_txt(self.active_override_file_list, o_folder, o_file_name + '_override.txt')
            DataSave.list_to_txt(self.remove_file_list, o_folder, o_file_name + '_del.txt')
            DataSave.list_to_txt(self.active_file_list, o_folder, o_file_name + '_final.txt')

    def get_priority_number(self, file_path):
        override_priority = 0
        if re.search(self.override_priority_list[0], file_path, re.IGNORECASE):
            override_priority = 16
            if re.search(self.override_priority_list[1], file_path, re.IGNORECASE):
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
