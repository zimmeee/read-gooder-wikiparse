import string

__author__ = 'beth'


class SentenceFragment:
    def __init__(self, indent=0, parts=None):
        self.tokens = list() if parts is None else parts
        self.indent = indent

    def __repr__(self):
        str_val = self.tokens[0] if len(self.tokens) == 1 else ' '.join(self.tokens)
        return ' ' * self.indent + str_val

    def append(self, token):
        if token in string.punctuation and self.len() > 0:
            self.tokens[self.len() - 1] += token
        else:
            self.tokens.append(token)

    def len(self):
        return len(self.tokens)


class Sentence:
    def __init__(self, H1="", H2="", H3="", H4="", H5="", numwords=0, sentence_parts=None):
        self.H1 = H1
        self.H2 = H2
        self.H3 = H3
        self.H4 = H4
        self.H5 = H5
        self.numwords = numwords
        if not sentence_parts:
            self.sentence_parts = []
        for part in sentence_parts:
            if not isinstance(part, SentenceFragment):
                raise Exception("This thing is not a sentence fragment: " + str(part))
        self.sentence_parts = sentence_parts

    def __repr__(self):
        headlines = "H1: " + self.H1 + "\n" + "H2: " + self.H2 + "\n" + "H3: " + self.H3 + "\n" + "H4: " + \
                    self.H4 + "\n" + "H5: " + self.H5 + "\n"
        return headlines + "\n".join([str(fragment) for fragment in self.sentence_parts]) + "\n"


class Document:
    def __init__(self, title=None, numsentences=None, numwords=None, sentences=None):
        self.title = title
        self.numsentences = numsentences
        self.numwords = numwords
        for sentence in sentences:
            if not isinstance(sentence, Sentence):
                raise Exception("This thing is not a sentence, asshole: " + str(sentence))
        self.sentences = sentences

    def __repr__(self):
        return "\n".join([str(sentence) for sentence in self.sentences])