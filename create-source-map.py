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
    def __init__(self, files):
        self.file_names_ = files
        self.file_index = -1
        self._next_file()

    def _next_file_word(self):
        # Roll until we find a word char
        while self.pos_ < len(self.text_) and re.match('\W', self.text_[self.pos_]):
            char = self.text_[self.pos_]
            if char == '\n':
                self.line += 1
                self.column = 0
            else:
                self.column += 1
            self.pos_ += 1
        if self.pos_ == len(self.text_):
            return None
        word_start = self.pos_
        while self.pos_ < len(self.text_) and re.match('\w', self.text_[self.pos_]):
            self.pos_ += 1
            self.column += 1
        return self.text_[word_start:self.pos_]

    def next_word(self):
        while True:
            word = self._next_file_word()
            if word:
                return word
            if not self._next_file():
                return None

    def _next_file(self):
        self.file_index += 1
        if self.file_index == len(self.file_names_):
            return False
        self.file_name = self.file_names_[self.file_index]
        self.line = 0
        self.column = 0
        self.pos_ = 0
        self.text_ = read_file(self.file_name)
        return True

class SourceMappingGenerator:
    def __init__(self, source_files, compiled_file):
        self.source_files_ = source_files
        self.compiled_file_ = compiled_file
        self.sourcemap_ = []
        self.current_line_number_ = 0
        self.sourcemap_line_ = []


    def add_mapping(self, generated_line, generated_column, source_file_index, source_line, source_column):
        if self.current_line_number_ != generated_line:
            self._push_sourcemap_line()
            self.current_line_number_ = generated_line
        self.sourcemap_line_.append(encode([generated_column, source_file_index, source_line, source_column]))


    def _push_sourcemap_line(self):
        self.sourcemap_.append(",".join(self.sourcemap_line_))
        self.sourcemap_line_ = []


    def output(self):
        if len(self.sourcemap_line_) > 0:
            self._push_sourcemap_line()
        print ";".join(self.sourcemap_)


file_names = ["1.txt", "2.txt"]
output_file = "out.txt"

source_picker = WordPicker(file_names)
generated_picker = WordPicker([output_file])

sourceMap = SourceMappingGenerator(file_names, output_file)
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
    sourceMap.add_mapping(generated_picker.line, generated_picker.column - word_len, source_picker.file_index, source_picker.line, source_picker.column - word_len)


sourceMap.output()


