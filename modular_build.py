from os import path

def read_file(filename):
    with open(path.normpath(filename), 'rt') as input:
        return input.read()
