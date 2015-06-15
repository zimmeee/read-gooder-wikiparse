from json import JSONEncoder
import string

__author__ = 'beth'


class SentenceFragment:
    def __init__(self, indent=0, tokens=None):
        self.tokens = list() if tokens is None else tokens
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

    @staticmethod
    def fromDict(dict_object):
        return SentenceFragment(indent=dict_object["indent"], tokens=dict_object["tokens"])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


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

    @staticmethod
    def fromDict(dict_object):
        return Sentence(H1=dict_object["H1"], H2=dict_object["H2"], H3=dict_object["H3"],
                        H4=dict_object["H4"], H5=dict_object["H5"], numwords=dict_object["numwords"],
                        sentence_parts=[SentenceFragment.fromDict(part) for part in dict_object["sentence_parts"]])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Document:
    def __init__(self, title=None, numsentences=None, numwords=None, sentences=None):
        self.title = title
        self.numsentences = numsentences
        self.numwords = numwords
        for sentence in sentences:
            if not isinstance(sentence, Sentence):
                raise Exception("This thing is not a sentence: " + str(sentence))
        self.sentences = sentences

    def __repr__(self):
        return "\n".join([str(sentence) for sentence in self.sentences])

    @staticmethod
    def fromDict(dict_object):
        return Document(title=dict_object["a_title"], numsentences=dict_object["num_sentences"],
                        numwords=dict_object["num_words"],
                        sentences=[Sentence.fromDict(part) for part in dict_object["sentences"]])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


# JSON encoding #######################################################################################################

class SentenceFragmentJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, SentenceFragment):
            raise Exception("Cannot use this encoder to encode non-SentenceFragment class.")
        serialized_fragment = {"tokens": obj.tokens, "indent": obj.indent}
        return serialized_fragment


class SentenceJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Sentence):
            raise Exception("Cannot use this encoder to encode non-Sentence class.")
        serialized_sentence = {"H1": obj.H1, "H2": obj.H2, "H3": obj.H3, "H4": obj.H4, "H5": obj.H5,
                               "numwords": obj.numwords}
        sf_encoder = SentenceFragmentJSONEncoder()  # for serializing individual sentence fragments
        serialized_sentence["sentence_parts"] = [sf_encoder.default(fragment)
                                                 for fragment in obj.sentence_parts]
        return serialized_sentence


class DocumentJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Document):
            raise Exception("Cannot use this encoder to encode non-Document class.")
        serialized_document = {"title": obj.title, "numsentences": obj.numsentences, "numwords": obj.numwords}
        sent_encoder = SentenceJSONEncoder()  # for serializing individual sentences
        serialized_document["sentences"] = [sent_encoder.default(sentence) for sentence in obj.sentences]
        return serialized_document