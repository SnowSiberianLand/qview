# -*- coding: cp1251 -*-
import mod_cmn
import struct



def get_fixed_width_unpacker(fieldspecs):
    """
    returns compiled method for split fixed width format
    fieldspecs - list of (begin_pos, end_pos, ...) items
    """

    fieldspecs.sort(key = lambda x: x[0]) # just in case

    # build the format for struct.unpack
    unpack_len = 0
    unpack_fmt = ""
    for fieldspec in fieldspecs:
        start = fieldspec[0] - 1
        end = start + fieldspec[1]
        if start > unpack_len:
            unpack_fmt += str(start - unpack_len) + "x"
        unpack_fmt += str(end - start) + "s"
        unpack_len = end

    #compile for efficiency
    unpacker = struct.Struct(unpack_fmt).unpack_from
    return unpacker


def make_dictionary(strs, sep = ':'):
    ret = {}
    items = [s.split(sep) for s in strs]
    for k, v in items:
        ret[k.strip()] = v.strip()    #пока сделал v.strip, но можно подумать (см. загрузка zak)
    return ret



if __name__ == '__main__':

    raw_data = [b"          Stallone            M. Sylvester G.     06.07.1946          22.07.2004XXXX",
                b"          Schwarzenegger      Arnold Alois        30.07.1947          13.08.2010 XX   "]

    str_func  = lambda s: str(s).strip()
    date_func = lambda s: mod_cmn.to_string_date(mod_cmn.date_t_from_string(s.decode()))

    # field specs (start pos (1-relative), len, field name, converter func)
    fieldspecs = [
        (11, 19, 'surname', str_func),
        (31, 19, 'given_names', str_func),
        (51, 10, 'birth_date', date_func),
        (71, 10, 'start_date', date_func),
        ]

    unpacker = get_fixed_width_unpacker(fieldspecs)

    for line in raw_data:
        raw_fields = unpacker(line)
        s = []
        for i, f in enumerate(raw_fields):
            x = fieldspecs[i][3](f)
            s.append(x)
        print(", ".join(s))