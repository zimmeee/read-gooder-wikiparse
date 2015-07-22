"""
OpenMind Document format - any raw text format is converted to this first
created by beth on 6/15/15
edited 7/22/15
"""

from json import JSONEncoder
import json


class Document:
    def __init__(self, header=None, section=None):
        self.header = header
        self.section = section

    def sentences(self):
        return self.section.sentences()

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
        return Section(header=dict_object["header"] if "header" in dict_object else None,
                       paragraphs=[Paragraph.fromDict(paragraph) for paragraph in dict_object["paragraphs"]]
                       if "paragraphs" in dict_object else None,
                       subsections=[Section.fromDict(s) for s in dict_object["subsections"]]
                       if "subsections" in dict_object else None)

    def sentences(self):
        all_sentences = []
        if self.paragraphs:
            for paragraph in self.paragraphs:
                for sentence in paragraph.sentences:
                    all_sentences.append(sentence)
        if self.subsections:
            for subsection in self.subsections:
                for sentence in subsection.sentences():
                    all_sentences.append(sentence)
        return all_sentences

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Paragraph:
    def __init__(self, sentences, position):
        self.sentences = sentences
        self.position = position

    def __repr__(self):
        return json.dumps(self, cls=ParagraphJSONEncoder, indent=4)

    @staticmethod
    def fromDict(dict_object):
        return Paragraph(sentences=[Sentence.from_dict(sentence) for sentence in dict_object["sentences"]],
                         position=dict_object["position"])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Sentence:
    def __init__(self, text, position):
        self.text = text
        self.position = position

    def __repr__(self):
        return json.dumps(self, cls=SentenceJSONEncoder, indent=4)

    @staticmethod
    def from_dict(dict_object):
        return Sentence(text=dict_object["text"], position=dict_object["position"])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


# JSON encoding #######################################################################################################


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


class SectionJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Section):
            raise Exception("Cannot use this encoder to encode non-Section class.")
        serialized_section = {}
        if obj.header:
            serialized_section["header"] = obj.header
        if obj.paragraphs:
            paragraph_encoder = ParagraphJSONEncoder()
            serialized_section["paragraphs"] = [paragraph_encoder.default(paragraph)
                                                for paragraph in obj.paragraphs]
        if obj.subsections:
            subsection_encoder = SectionJSONEncoder()
            serialized_section["subsections"] = [subsection_encoder.default(subsection)
                                                 for subsection in obj.subsections]
        return serialized_section


class ParagraphJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Paragraph):
            raise Exception("Cannot use this encoder to encode non-Paragraph class.")
        serialized_paragraph = {}
        if obj.sentences:
            sentence_encoder = SentenceJSONEncoder()  # for serializing individual sentences
            serialized_paragraph["sentences"] = [sentence_encoder.default(sentence) for sentence in obj.sentences]
        serialized_paragraph["position"] = obj.position
        return serialized_paragraph


class SentenceJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Sentence):
            raise Exception("Cannot use this encoder to encode non-Sentence class.")
        serialized_sentence = {"text": obj.text, "position": obj.position}
        return serialized_sentence
