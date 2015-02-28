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
    def __init__(self, compiled_file, source_files):
        self.compiled_file_ = compiled_file
        self.source_files_ = source_files
        self.sourcemap_ = []
        self.line_ = 0


    def add_mapping(self, generated_line, generated_column, source_file_index, source_line, source_column):
        if self.line_ != generated_line:
            self.sourcemap_.append(";")
            self.line_ = generated_line
        self.sourcemap_.append(encode([generated_column, source_file_index, source_line, source_column))

    def output(self):
        print 


picker = WordPicker(["1.txt", "2.txt"])
while True:
    word = picker.next_word()
    if not word:
        break
    print "%s:%d:%d  --- %s" % (picker.file_name, picker.line, picker.column - len(word), word)
