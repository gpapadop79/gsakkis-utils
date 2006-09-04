#!/usr/bin/env python

import sys

# decoding table: map each digit to the letter(s) that can be encoded to it
decode = tuple("E JNQ RWX DSY FT AM CIV BKU LOP GHZ".split())

# encoding table: map each letter to the digit it is encoded to
encode = dict([(letter,digit) for (digit,letters) in enumerate(decode)
                for letter in letters])

def normalizeWord(word):
    # XXX: For every letter, both its upper and lower case are mapped to
    # the same digit; if not, replace word.upper() -> word
    return ''.join([c for c in word.upper() if c.isalpha()])

class PhoneBook:
    def __init__(self, phonebookFile, dictFile):
        self._phonebook = phonebookFile
        self.setDictionary(dictFile)

    def __iter__(self):
        return open(self._phonebook)

    def setDictionary(self, dictFile):
        # map digit -> words starting with a decoded letter for this digit
        self._digit2Words = digit2Words = {}
        for word in open(dictFile):
            word = word.rstrip()
            digit2Words.setdefault(encode[normalizeWord(word)[0]],[]).append(word)

    def decodePhone(self, phone):
        phone = phone.rstrip()
        digits = [int(c) for c in phone if c.isdigit()]
        #for solution in self._iterSolution(digits, None):
        for solution in self._iterSolution2(digits, []):
            print "%s: %s" % (phone,' '.join(map(str,solution)))

    def _iterSolution(self, digits, lastFound):
        size = len(digits)
        if not size:
            yield []
        else:
            matched = False
            for word in self._digit2Words.get(digits[0],()):
                normalizedEncoded = [encode[c] for c in normalizeWord(word)]
                wordlen = len(normalizedEncoded)
                if normalizedEncoded == digits[:wordlen]:
                    matched = True
                    prefix = [word]
                    for rest_solution in self._iterSolution(digits[wordlen:], prefix[0]):
                        yield prefix + rest_solution
            if not matched and not isinstance(lastFound,int):
                prefix = [digits[0]]
                for rest_solution in self._iterSolution(digits[1:], prefix[0]):
                    yield prefix + rest_solution


    def _iterSolution2(self, digits, accumulator):
        size = len(digits)
        if not size:
            yield accumulator
        else:
            matched = False
            for word in self._digit2Words.get(digits[0],()):
                normalizedEncoded = [encode[c] for c in normalizeWord(word)]
                wordlen = len(normalizedEncoded)
                if wordlen > size:
                    continue
                if normalizedEncoded == digits[:wordlen]:
                    matched = True
                    accumulator.append(word)
                    for rest_solution in self._iterSolution2(digits[wordlen:],
                                                             accumulator):
                        yield rest_solution
                    accumulator.pop()
            if not matched and not (accumulator and isinstance(accumulator[-1],int)):
                accumulator.append(digits[0])
                for rest_solution in self._iterSolution2(digits[1:], accumulator):
                    yield rest_solution
                accumulator.pop()


if __name__ == '__main__':
    phonebook = PhoneBook(sys.argv[2], sys.argv[1])
    for phone in phonebook:
        phonebook.decodePhone(phone)

