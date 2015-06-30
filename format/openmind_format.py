from json import JSONEncoder
import json
import string

__author__ = 'beth'


class Document:
    def __init__(self, header=None, section=None):
        self.header = header
        self.section = section

    def __repr__(self):
        return json.dumps(self, cls=DocumentJSONEncoder, indent=4)

    @staticmethod
    def fromDict(dict_object):
        return Document(header=dict_object["header"] if "header" in dict_object else "",
                        section=Section.fromDict(dict_object["section"]) if "section" in dict_object else None)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Section:
    def __init__(self, header=None, paragraphs=None, subsections=None):
        self.header = header
        self.paragraphs = paragraphs
        self.subsections = subsections

    def __repr__(self):
        return json.dumps(self, cls=SectionJSONEncoder, indent=4)

    @staticmethod
    def fromDict(dict_object):
        return Section(header=dict_object["header"] if "header" in dict_object else "",
                       paragraphs=[Paragraph.fromDict(paragraph) for paragraph in dict_object["paragraphs"]]
                       if "paragraphs" in dict_object else [],
                       subsections=[Section.fromDict(s) for s in dict_object["section"]]
                       if "section" in dict_object else None)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Paragraph:
    def __init__(self, sentences=None):
        self.sentences = sentences

    def __repr__(self):
        return json.dumps(self, cls=ParagraphJSONEncoder, indent=4)

    @staticmethod
    def fromDict(dict_object):
        return Paragraph(sentences=[Sentence.from_dict(sentence) for sentence in dict_object["sentences"]])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class SentenceFragment:
    def __init__(self, indent=0, tokens=None, text=None):
        self.tokens = list() if tokens is None else tokens
        self.indent = indent
        self.text = text if text else None

    def __repr__(self):
        return json.dumps(self, cls=SentenceFragmentJSONEncoder, indent=4)

    def append(self, token):
        if token in string.punctuation and self.len() > 0:
            self.tokens[self.len() - 1] += token
        else:
            self.tokens.append(token)

    def len(self):
        return len(self.tokens)

    @staticmethod
    def fromDict(dict_object):
        return SentenceFragment(indent=dict_object["indent"],
                                tokens=dict_object["tokens"] if "tokens" in dict_object else None,
                                text=dict_object["text"] if "text" in dict_object else None)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Sentence:
    def __init__(self, numwords=0, sentence_parts=None):
        self.numwords = numwords
        if not sentence_parts:
            self.sentence_parts = []
        for part in sentence_parts:
            if not isinstance(part, SentenceFragment):
                raise Exception("This thing is not a sentence fragment: " + str(part))
        self.sentence_parts = sentence_parts

    def __repr__(self):
        return json.dumps(self, cls=SentenceJSONEncoder, indent=4)

    @staticmethod
    def from_dict(dict_object):
        return Sentence(numwords=dict_object["num_words"],
                        sentence_parts=[SentenceFragment.fromDict(part) for part in dict_object["sentence_parts"]])

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
        serialized_fragment = {}
        if obj.tokens:
            serialized_fragment["tokens"] = obj.tokens
        serialized_fragment["indent"] = obj.indent
        if obj.text:
            serialized_fragment["text"] = obj.text
        return serialized_fragment


class SentenceJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Sentence):
            raise Exception("Cannot use this encoder to encode non-Sentence class.")
        serialized_sentence = {}
        if obj.sentence_parts:
            sf_encoder = SentenceFragmentJSONEncoder()  # for serializing individual sentence fragments
            serialized_sentence["sentence_parts"] = [sf_encoder.default(fragment) for fragment in obj.sentence_parts]
        serialized_sentence["numwords"] = obj.numwords
        return serialized_sentence


class ParagraphJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Paragraph):
            raise Exception("Cannot use this encoder to encode non-Paragraph class.")
        serialized_paragraph = {}
        if obj.sentences:
            sentence_encoder = SentenceJSONEncoder()  # for serializing individual sentences
            serialized_paragraph["sentences"] = [sentence_encoder.default(sentence) for sentence in obj.sentences]
        return serialized_paragraph


class SectionJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Section):
            raise Exception("Cannot use this encoder to encode non-Section class.")
        serialized_section = {}
        if obj.header:
            serialized_section["header"] = obj.header
        if obj.paragraphs:
            paragraph_encoder = ParagraphJSONEncoder()
            serialized_section["paragraphs"] = [paragraph_encoder.default(paragraph) for paragraph in obj.paragraphs]
        if obj.subsections:
            subsection_encoder = SectionJSONEncoder()
            serialized_section["section"] = [subsection_encoder.default(subsection) for subsection in obj.subsections]
        return serialized_section


class DocumentJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Document):
            raise Exception("Cannot use this encoder to encode non-Document class.")
        serialized_document = {}
        if obj.header:
            serialized_document["header"] = obj.header
        if obj.section:
            sect_encoder = SectionJSONEncoder()  # for serializing individual sections
            serialized_document["section"] = sect_encoder.default(obj.section)
        return serialized_document