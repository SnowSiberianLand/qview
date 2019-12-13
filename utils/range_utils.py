# -*- coding: cp1251 -*-



import data_utils as du
import math

def is_overlapped(lst):
    """
    �������� ���������� � lst �� ������� �����������
    lst - ������, �������� - tuple (xbeg, xend)
    """
    n = len(lst)
    for i in range(n):
        intv1 = lst[i]
        for j in range(i+1,n):
            intv2 = lst[j]

            ll = du.intersection_length(intv1[0],intv1[1],intv2[0],intv2[1])
            if ll is not None:
                return True
    return False

def remove_empty_intervals(lst, min_thickness):
    """
    ������� �� ������ ����������� ��������� (�������� < min_thickness)
    """
    out = []
    
    n = len(lst)
    for i in range(n):
        itm = lst[i]
        ll = math.fabs(itm[1]-itm[0])
        if ll < min_thickness:
            continue

        out.append(itm)
        
    return out
        
def union_overlapped(lst):
    """
    ���������� �������������� ��������� � lst
    ��������� �� �������� ������������� ���������
    lst - ������, �������� - tuple (xbeg, xend)
    """
    out = lst
    count = 0
    while is_overlapped(out):
        #print out
        out = union_overlapped_impl(out)
        if count>100:
            break
        count = count+1
        
    return out
    
def union_overlapped_impl(lst):
    """
    ��� ����������� ������������� � range_utils
    ���������� �������������� ��������� � lst
    ��������� ����� ��������� �������������� ���������
    lst - ������, �������� - tuple (xbeg, xend)
    """

    excl = set()
    
    out = []
    n = len(lst)
    for i in range(n):
        intv1 = lst[i]
        if i in excl:
            continue

        bAppended = False
        for j in range(i+1,n):
            intv2 = lst[j]

            ll = du.intersection_length(intv1[0],intv1[1],intv2[0],intv2[1])
            if ll is not None:
                intv3 = du.union(intv1[0],intv1[1],intv2[0],intv2[1])
                out.append(intv3)
                excl.add(j)
                bAppended = True
                
        if bAppended==False:
            out.append(intv1)

        if i==n-1:
            out.append(intv1)    
    return out

def interval_or(lst, xbeg, xend):
    """
    ��������� ���������� �������� OR ��� ������� ���������� (lst)
    � ���������� [xbeg, xend]
    lst - ������, �������� - tuple (xbeg, xend)
    """
    lst.append( (xbeg,xend) )
    return union_overlapped(lst)
    
def interval_subtract(lst, xbeg, xend, min_thickness):
    """
    ��������� ���������� �������� SUBTRACT ��� ������� ���������� (lst)
    � ���������� [xbrg, xend]
    lst - ������, �������� - tuple (xbeg, xend)
    """

    out = []
    
    n = len(lst)
    for i in range(n):
        intv = lst[i]

        tmp = du.subtract(intv[0], intv[1], xbeg, xend)
        out = out + tmp

    out = remove_empty_intervals(out, min_thickness)

    return out
