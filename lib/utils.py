# coding: utf-8
import string


def parse_fasta(file_path):
    seq = {}
    with open(file_path) as f:
        data = True
        name = None
        while data:
            data = f.readline()
            s = data.strip()
            if s.startswith('>'):
                name = ''
                for char in s[1:].strip():
                    if char not in string.printable[:62]:
                        char = '_'
                    name += char

                seq[name] = ''
            else:
                if not name:
                    continue
                if s:
                    seq[name] = seq[name] + s

    return seq


if __name__ == '__main__':
    parse_fasta('upload/839f90f4-1c77-4147-bfbe-7dcedfa5926e.fasta')
