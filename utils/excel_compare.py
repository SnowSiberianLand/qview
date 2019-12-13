# -*- coding: cp1251 -*-

import sys

import path64 as mpath

import xlrd

def process(path, path_std, path_log):

    rb = xlrd.open_workbook('{0}'.format(path))
    rb_std = xlrd.open_workbook('{0}'.format(path_std))
    
    res = []
    
    if len(rb.sheets()) != len(rb_std.sheets()):
        print('Разное количество листов')
        print(False)
        sys.exit(1)

    f = open('{0}'.format(path_log), 'w')
    
    for n in range(len(rb.sheets())):
    
        sheet = rb.sheet_by_index(n)
        sheet_std = rb_std.sheet_by_index(n)
        
        vals = [sheet.row_values(rownum) for rownum in range(sheet.nrows)]
        vals_std = [sheet_std.row_values(rownum) for rownum in range(sheet_std.nrows)]
    
        res.append(vals==vals_std)

        if vals!=vals_std:
            f.write('\n')
            f.write('Лист {0} \n'.format(sheet.name))
            f.write('\n')
            for rownum in range(sheet.nrows):
                if sheet.row_values(rownum)!=sheet_std.row_values(rownum):
                    f.write('Строка {0} \n'.format(rownum+1))
                    
                    for index in sheet.row_values(rownum):
                        f.write('{0} '.format(index))
                        
                    f.write('\n')
                    
                    for index in sheet_std.row_values(rownum):
                        f.write('{0} '.format(index))
                        
                    f.write('\n')
                    f.write('\n')

    f.close()
    
    if False in res:
        print(False)
        sys.exit(1)
    else:
        print(True)


if __name__ == '__main__':

    path = sys.argv[1]

    path_std = sys.argv[2]

    path_log = sys.argv[3]
    
    process(path, path_std, path_log)
    