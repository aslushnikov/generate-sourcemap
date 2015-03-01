from cStringIO import StringIO
import re

BASE64_DIGITS="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
VLQ_BASE_SHIFT = 5;
VLQ_CONTINUATION_BIT = 2**VLQ_BASE_SHIFT;
VLQ_BASE_MASK = VLQ_CONTINUATION_BIT - 1


def encode_primitive(number):
    if number == 0:
        return BASE64_DIGITS[0]
    number <<= 1
    letters = []
    while number > 0:
        digit = number & VLQ_BASE_MASK;
        number >>= VLQ_BASE_SHIFT
        if number > 0:
            digit |= VLQ_CONTINUATION_BIT
        letters.append(BASE64_DIGITS[digit])
    return "".join(letters)


def encode(numbers):
    codes = []
    for number in numbers:
        codes.append(encode_primitive(number))
    return "".join(codes)


def read_file(file_name):
    with open(file_name, 'r') as input:
        return input.read()


class WordPicker:
    def __init__(self, sources):
        self._sources = sources
        self.source_index = -1
        self._next_source()

    def _next_source_word(self):
        # Roll until we find a word char
        while self._pos < len(self._text) and re.match('\W', self._text[self._pos]):
            char = self._text[self._pos]
            if char == '\n':
                self.line += 1
                self.column = 0
            else:
                self.column += 1
            self._pos += 1
        if self._pos == len(self._text):
            return None
        word_start = self._pos
        while self._pos < len(self._text) and re.match('\w', self._text[self._pos]):
            self._pos += 1
            self.column += 1
        return self._text[word_start:self._pos]

    def next_word(self):
        while True:
            word = self._next_source_word()
            if word:
                return word
            if not self._next_source():
                return None

    def _next_source(self):
        self.source_index += 1
        if self.source_index == len(self._sources):
            return False
        self.line = 0
        self.column = 0
        self._pos = 0
        self._text = self._sources[self.source_index]
        return True

class SourceMappingGenerator:
    def __init__(self):
        self._not_empty = False
        self._sourcemap = StringIO()
        self._current_line_number = 0


    def add_mapping(self, generated_line, generated_column, source_file_index, source_line, source_column):
        if self._not_empty and self._current_line_number == generated_line:
            self._sourcemap.write(",")
        while self._current_line_number < generated_line:
            self._sourcemap.write(";")
            self._current_line_number += 1
        self._sourcemap.write(encode([generated_column, source_file_index, source_line, source_column]))
        self._not_empty = True


    def _push_sourcemap_line(self):
        self.sourcemap_.append(",".join(self._sourcemap_line))
        self._sourcemap_line = []


    def output(self):
        print self._sourcemap.getvalue()


file_names = ["1.txt", "2.txt"]
output_file = "out.txt"

origin_sources = []
for origin_file_name in file_names:
    origin_sources.append(read_file(origin_file_name))

generated_source = read_file(output_file)

source_picker = WordPicker(origin_sources)
generated_picker = WordPicker([generated_source])

sourceMap = SourceMappingGenerator()
while True:
    generated_word = generated_picker.next_word()
    if generated_word == None:
        break;
    source_word = source_picker.next_word()
    while source_word != None and source_word != generated_word:
        source_word = source_picker.next_word()
    if source_word == None:
        raise Exception("Failed to match generated and source files")
    word_len = len(generated_word)
    sourceMap.add_mapping(generated_picker.line, generated_picker.column - word_len, source_picker.source_index, source_picker.line, source_picker.column - word_len)

sourceMap.output()


