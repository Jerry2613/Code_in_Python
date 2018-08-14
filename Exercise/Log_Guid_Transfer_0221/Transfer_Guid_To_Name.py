import os
import glob


class FileLocation(object):
    def __init__(self):
        self.project_root = 'c:\bios'
        self.target_files = []

    @property
    def root_path(self):
        return self.project_root

    @root_path.setter
    def root_path(self, value):
        self.project_root = value

    # input: filename_extension
    # output: None
    # internal object: self.target_files will save matched filename and absolute path
    def gather_target_files(self, filename_extension):
        for root, dirs, files in os.walk(self.root_path):
            for tfile in files:
                if tfile.endswith(filename_extension):
                    self.target_files.append(os.path.join(root, tfile))


class GuidAction(object):
    def __init__(self):
        self._LogFile = 'Old.log'
        self._NewLogFileName = 'New.log'
        self.Guid_Table = []

    @property
    def output_log_file(self):
        return self._NewLogFileName

    @output_log_file.setter
    def output_log_file(self, name):
        self._NewLogFileName = name

    @property
    def target_log_file(self):
        return self._LogFile

    @target_log_file.setter
    def target_log_file(self, name):
        self._LogFile = name

    @staticmethod
    def produce_guidfile_from_file(tfile, guidfile, attrib='w'):
        with open(tfile, "r") as Dec_file, open(guidfile, attrib) as DPF_guid:
            for line in Dec_file:
                if GuidAction.isguid(line):
                    for ch in ['=', '0x', ',', '{', '}', '\n']:
                        line = line.replace(ch, ' ')
                    line_list = line.split()
                    for i in range(1, len(line_list)):
                        if i == 1:
                            line_list[i] = line_list[i].zfill(8)
                            continue
                        line_list[i] = line_list[i].zfill(2) if i >= 4 else line_list[i].zfill(4)
                    new_line = "-".join(line_list[1:4]) \
                               + "-" + "".join(line_list[4:6]) \
                               + "-" + "".join(line_list[6:])
                    new_line = new_line.upper() + ' ' + line_list[0] + '\n'
                    DPF_guid.write(new_line)

    def merge_guidfile_to_guidtable_list(self, filename):
        with open(filename, "r") as Guid_File:
            for line in Guid_File:
                line_list = (line.replace("\n", "")).split(' ')
                self.Guid_Table.append(line_list)

    def replace_guid_by_name(self, line):
        if 4 <= line.count('-'):
            line_list = (line.replace('\n', '')).split(' ')
            for index, data in enumerate(line_list):
                if 4 == data.count('-'):
                    tail_string = ''
                    leading_char = ''
                    for i in ['.', ',']:
                        if 1 == data.count(i):
                            leading_char = i if i == data[0] else ''
                            sub_data_list = (data.replace(i, ' ')).split(' ')
                            data = sub_data_list[0]
                            if leading_char == '':
                                tail_string = i + sub_data_list[1] if 2 == len(sub_data_list) else i
                            break
                    for guid, name in self.Guid_Table:
                        if data == guid:
                            line_list[index] = leading_char + name + tail_string
                            break
            return ' '.join(line_list) + "\n"

    def transfer_logfile_guid(self):
        with open(self.target_log_file, "r") as Old_log, open(self.output_log_file, "w") as New_log:
            for original_message in Old_log:
                m_message = self.replace_guid_by_name(original_message)
                if m_message is None:
                    m_message = original_message
                New_log.write(m_message)

    @staticmethod
    def isguid(line):
        return False if 1 <= line.count('#') else 10 == line.count(',')

    @staticmethod
    def remove_duplicated_line(org_file, mod_file):
        checked = []
        with open(org_file, "r") as org, open(mod_file, "w") as mod:
            for line in org:
                add_flag = True
                for i in checked:
                    if line == i:
                        add_flag = False
                        break
                if add_flag:
                    checked.append(line)
                    mod.write(line)

    @staticmethod
    def build_driver_guid_from_inf(tfile, guidfile, attrib='a'):
        with open(tfile, "r") as inf_file, open(guidfile, attrib) as guid_file:
            file_guid = ''
            base_name = ''
            for iline in inf_file:
                if 1 == iline.count('='):
                    iline_list = iline.split('=')
                    if iline_list[0].strip() == "FILE_GUID":
                        file_guid = (iline_list[1].replace('\n', '')).strip()
                    if iline_list[0].strip() == "BASE_NAME":
                        base_name = (iline_list[1].replace('\n', '')).strip()
                if file_guid != '' and base_name != '':
                    guid_file.write(file_guid + ' ' + base_name + '\n')
                    break


if __name__ == '__main__':
    # Find out all dec files in target project
    pj = FileLocation()
    pj.root_path = 'c:\BIOS\Rugged2\Liv2_99.0.41_Rev0901_BT'
    pj.gather_target_files('.dec')

    # Find out unique GUID and save to file
    for file in pj.target_files:
        GuidAction.produce_guidfile_from_file(file, "Dec_Guid_All.txt", 'a+')
    GuidAction.remove_duplicated_line("Dec_Guid_All.txt", "Dec_Guid_Unique.txt")

    # find out .inf guid
    if True:
        inf = FileLocation()
        inf.root_path = 'c:\BIOS\Rugged2\Liv2_99.0.41_Rev0901_BT'
        inf.gather_target_files('.inf')

        # Find out unique GUID and save to file
        for file in inf.target_files:
            GuidAction.build_driver_guid_from_inf(file, "Inf_Guid_All.txt", 'a+')
        GuidAction.remove_duplicated_line("Inf_Guid_All.txt", "Inf_Guid_Unique.txt")

    # merge all unique guid file to one
    read_files = glob.glob("*_Guid_Unique.txt")

    with open("Guid_All.txt", "wb") as outfile:
        for f in read_files:
            with open(f, "rb") as infile:
                outfile.write(infile.read())
    GuidAction.remove_duplicated_line("Guid_All.txt", "Guid_Unique.txt")

    # Transfer Log file's Guid
    p = GuidAction()
    p.target_log_file = "LivingStone2.log"
    filename_list = p.target_log_file.split('.')
    filename_list.insert(1, '_New.')
    p.output_log_file = ''.join(filename_list)
    p.merge_guidfile_to_guidtable_list('Guid_Unique.txt')
    p.transfer_logfile_guid()

    # produce loading_sequence.txt
    with open(p.output_log_file, "r") as logfile, open('loading_sequence.txt', "w") as loading:
        for line in logfile:
            if 1 == line.count('.Entry'):
                para = line.split('.Entry')
                loading.write(para[0] + '\n')
#            if 1 == line.count('Loading driver'):
#                loading.write('***' + line)
