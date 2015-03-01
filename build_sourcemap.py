#!/usr/bin/env python
#
# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from cStringIO import StringIO
from modular_build import read_file
import re

BASE64_DIGITS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
VLQ_BASE_SHIFT = 5
VLQ_CONTINUATION_BIT = 2 ** VLQ_BASE_SHIFT
VLQ_BASE_MASK = VLQ_CONTINUATION_BIT - 1


def encode_primitive(number):
    if number == 0:
        return BASE64_DIGITS[0]
    if number < 0:
        number = ((-number) << 1) | 1
    else:
        number <<= 1
    letters = []
    while number > 0:
        digit = number & VLQ_BASE_MASK
        number >>= VLQ_BASE_SHIFT
        if number > 0:
            digit |= VLQ_CONTINUATION_BIT
        letters.append(BASE64_DIGITS[digit])
    return ''.join(letters)


def encode(numbers):
    codes = []
    for number in numbers:
        codes.append(encode_primitive(number))
    return ''.join(codes)


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


class SourceMappingStringGenerator:
    def __init__(self):
        self._not_empty = False
        self._sourcemap = StringIO()
        self._generated_line_number = 0
        self._generated_column_number = 0
        self._source_index = 0
        self._source_line_number = 0
        self._source_column_number = 0

    def add_mapping(self, generated_line, generated_column, source_index, source_line, source_column):
        if self._not_empty and self._generated_line_number == generated_line:
            self._sourcemap.write(',')
        while self._generated_line_number < generated_line:
            self._sourcemap.write(';')
            self._generated_line_number += 1
            self._generated_column_number = 0
        self._sourcemap.write(encode([generated_column - self._generated_column_number, source_index - self._source_index, source_line - self._source_line_number, source_column - self._source_column_number]))
        self._generated_column_number = generated_column
        self._source_index = source_index
        self._source_line_number = source_line
        self._source_column_number = source_column
        self._not_empty = True

    def value(self):
        return self._sourcemap.getvalue()


class SourceMappingStringIO:
    def __init__(self):
        self._out = StringIO()
        self.source_names = []
        self.sources = []

    def write(self, text):
        self._out.write(text)
        self.source_names.append(None)
        self.sources.append(text)

    def writeFile(self, file_name):
        text = read_file(file_name)
        self._out.write(text)
        self.source_names.append(file_name)
        self.sources.append(text)

    def writeNamedSource(self, text, source_name):
        self._out.write(text)
        self.source_names.append(source_name)
        self.sources.append(text)

    def getvalue(self):
        return self._out.getvalue()

    def close(self):
        self._out.close()


def build_source_map(sources, source_names, generated_name, generated_source):
    source_picker = WordPicker(sources)
    generated_picker = WordPicker([generated_source])
    named_source_indexes = dict()
    named_index = 0
    for source_name in source_names:
        if not source_name:
            continue
        named_source_indexes[source_name] = named_index
        named_index += 1

    source_mapping = SourceMappingStringGenerator()
    while True:
        generated_word = generated_picker.next_word()
        if generated_word is None:
            break
        source_word = source_picker.next_word()
        while source_word is not None and source_word != generated_word:
            source_word = source_picker.next_word()
        if source_word is None:
            raise Exception('Failed to match generated and source files')

        source_name = source_names[source_picker.source_index]
        if not source_name:
            continue

        word_len = len(generated_word)
        source_mapping.add_mapping(generated_picker.line, generated_picker.column - word_len, named_source_indexes[source_name], source_picker.line, source_picker.column - word_len)

    source_map_v3 = {}
    source_map_v3['version'] = 3
    source_map_v3['file'] = generated_name
    source_map_v3['sourceRoot'] = 'http://localhost:8090'
    source_map_v3['sources'] = [source for source in source_names if source]
    source_map_v3['names'] = []
    source_map_v3['mappings'] = source_mapping.value()
    return source_map_v3
