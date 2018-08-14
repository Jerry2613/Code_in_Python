import os
import sys
import errno
import xlrd
import hashlib


class RuggedDigest():
    """Base class for rugged digest table"""

    def __init__(self):
        self.s_raw_data = []
        self.m_raw_data = []
        self.hex_digest = []
        self.lv_s_raw_data = []
        self.lv_m_raw_data = []
        self.lv_hex_digest = []

        self.outputd = os.path.join(os.getcwd(),'Rugged2')
        self.outputdf = os.path.join(self.outputd, 'Dummy.h')
        self.servicetagfilename = os.path.join(self.outputd, 'RuggedServiceTag.h')
        self.macfilename = os.path.join(self.outputd, 'RuggedMac.h')
        self.digestfilename = os.path.join(self.outputd, 'RuggedDigest.h')

        self.lv_outputd = os.path.join(os.getcwd(),'Livingstone')
        self.lv_outputdf = os.path.join(self.lv_outputd, 'Dummy.h')
        self.lv_servicetagfilename = os.path.join(self.lv_outputd, 'RuggedServiceTag.h')
        self.lv_macfilename = os.path.join(self.lv_outputd, 'RuggedMac.h')
        self.lv_digestfilename = os.path.join(self.lv_outputd, 'RuggedDigest.h')

        self.rugged_project_sheet = ['Columbus II Tags', 'Eriksson II Tags', 'Magellan II Tags','Livingstone Tags']
        self.project_sheet_num_of_rows = {'Columbus II Tags': 0, 'Eriksson II Tags': 0, 'Magellan II Tags': 0,
                                          'Livingstone Tags': 0}
        self.ServiceTag_col = 0
        self.MacAddress_col = 3
        self.test_servicetag = ['BPSQNY1']
        self.test_macaddress = ['102030405060']

        if not os.path.exists(os.path.dirname(self.outputdf)):
            print("mkdir:", os.path.dirname(self.outputdf))
            os.makedirs(os.path.dirname(self.outputdf), exist_ok=True)
        if not os.path.exists(os.path.dirname(self.lv_outputdf)):
            print("mkdir:", os.path.dirname(self.lv_outputdf))
            os.makedirs(os.path.dirname(self.lv_outputdf), exist_ok=True)

        if os.path.isfile(self.digestfilename):
            os.remove(self.digestfilename)
        if os.path.isfile(self.lv_digestfilename):
            os.remove(self.lv_digestfilename)
        if os.path.isfile(self.macfilename):
            os.remove(self.macfilename)
        if os.path.isfile(self.lv_macfilename):
            os.remove(self.lv_macfilename)

    def transfer_xls2list(self):
        with xlrd.open_workbook(sys.argv[1]) as xl_workbook:
            #print('Sheet name:',xl_workbook.sheet_names())
            for i in self.rugged_project_sheet:
                project_sheet = xl_workbook.sheet_by_name(i)
                self.project_sheet_num_of_rows[i] = project_sheet.nrows - 1    # skip first row (row name)
                for s_row in range(1, 1 + self.project_sheet_num_of_rows[i]):
                    st_cell = project_sheet.cell(s_row, self.ServiceTag_col).value
                    mac_cell = project_sheet.cell(s_row, self.ServiceTag_col).value
                    if i == 'Livingstone Tags':
                        self.lv_s_raw_data.append(st_cell)
                        self.lv_m_raw_data.append(mac_cell)
                    else:
                        self.s_raw_data.append(st_cell)
                        self.m_raw_data.append(mac_cell)

    def hexreverse(data):
        b1 = data[0:2]
        b2 = data[2:4]
        b3 = data[4:6]
        b4 = data[6:8]
        rdata = b4 + b3 + b2 + b1
        return rdata

    def produce_table_file(self, table, filename):
        with open(filename, mode='w') as Table_file:
            for m in table:
                Table_file.write('\"' + m + '\",\n')

    def produce_digest_table(self, service_raw_data, mac_raw_data, digestfilename):
        hex_digest = []
        for s, m in zip(service_raw_data, mac_raw_data):
            hash_object = hashlib.sha1((s + m).encode('utf-8'))
            hex_digest.append('0x' + RuggedDigest.hexreverse(hash_object.hexdigest()[0:8]) + ', ')
            hex_digest.append('0x' + RuggedDigest.hexreverse(hash_object.hexdigest()[8:16]) + ', ')
            hex_digest.append('0x' + RuggedDigest.hexreverse(hash_object.hexdigest()[16:24]) + ', ')
            hex_digest.append('0x' + RuggedDigest.hexreverse(hash_object.hexdigest()[24:32]) + ', ')
            hex_digest.append('0x' + RuggedDigest.hexreverse(hash_object.hexdigest()[32:40]) + ', ')
        with open(digestfilename, mode='w') as Hash_table:
            for i, h in enumerate(hex_digest):
                i += 1  # transfer 0 base to 1 base
                Hash_table.write(h)
                if i % 5 == 0:
                    Hash_table.write("\n")
            return hex_digest

    def addtestkey(self):
        self.s_raw_data += self.test_servicetag
        self.m_raw_data += self.test_macaddress
        self.lv_s_raw_data += self.test_servicetag
        self.lv_m_raw_data += self.test_macaddress

    def showtable(self):
        print("===Service Tag Table===")
        print('self_s_raw_data:', self.s_raw_data)
        print('self.livingstone_s_raw_data:', self.lv_s_raw_data)
        print("===MAC Address Table===")
        print('self.m_raw_data', self.m_raw_data)
        print('self.livingstone_m_raw_data', self.lv_m_raw_data)
        print("===Rugged 2 Digest Table===")
        with open(self.digestfilename, mode='r') as Digest_table:
            for line in Digest_table:
                print(line)
        print("===Livingstone Digest Table===")
        with open(self.lv_digestfilename, mode='r') as Digest_table_R2:
            for line in Digest_table_R2:
                print(line)
        print("==Project Service tag numbers===")
        print(self.project_sheet_num_of_rows)
        print('Rugged2 digest table length:', len(self.s_raw_data), '\n',
              'Livingstone digest table length:', len(self.lv_s_raw_data))


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise FileNotFoundError
        if os.path.isfile(sys.argv[1]):
            f1 = sys.argv[1].split('.')
            e = RuggedDigest()
            if f1[1] == "xls" or f1[1] == "xlsx":
                e.transfer_xls2list()
            else:
                raise FileNotFoundError
            e.addtestkey()
            e.produce_table_file(e.s_raw_data, e.servicetagfilename)
            e.produce_table_file(e.m_raw_data, e.macfilename)
            e.hex_digest = e.produce_digest_table(e.s_raw_data, e.m_raw_data, e.digestfilename)
            e.produce_table_file(e.lv_s_raw_data, e.lv_servicetagfilename)
            e.produce_table_file(e.lv_m_raw_data, e.lv_macfilename)
            e.lv_hex_digest = e.produce_digest_table(e.lv_s_raw_data, e.lv_m_raw_data, e.lv_digestfilename)
            e.showtable()
            print("Finish the SUMA for shipping Digest table !!")
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        print("The parameter is wrong or the file is not exist!!!")
        print("Command:")
        print("        Python RuggedDigest xlsnew.xlsx")
        sys.exit(errno.EINVAL)
    finally:
        pass
