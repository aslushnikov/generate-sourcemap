import re
import collections


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
        self.file_names_ = collections.deque(files)
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
        if len(self.file_names_) == 0:
            return False
        ++self.file_index
        self.file_name = self.file_names_.popleft()
        self.line = 0
        self.column = 0
        self.pos_ = 0
        self.text_ = read_file(self.file_name)
        return True

picker = WordPicker(["1.txt", "2.txt"])
while True:
    word = picker.next_word()
    if not word:
        break
    print "word: %s lineNumber: %d column: %d" % (word, picker.line, picker.column - len(word))

