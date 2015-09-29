"""
Screenwriters turn Document objects into Screenplays
created by beth on 7/22/15
"""
from abc import ABCMeta, abstractmethod
from json import JSONEncoder, JSONDecoder
import json
from json.decoder import WHITESPACE
from random import shuffle
import textwrap

from nltk import Tree

from nltk.parse.stanford import StanfordParser

from document import Document
from screenplay import Screenplay, Scene, SceneElement


class Screenwriter(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.screenwriter_class = type(self).__name__

    @abstractmethod
    # returns a list of DisplayFrame objects
    def write_screenplay(self, document):
        if not isinstance(document, Document):
            raise Exception("Yo, this is not a document: " + str(document))
        screenplay = Screenplay()
        screenplay.doc_id = document.doc_id
        screenplay.title = document.header
        return screenplay

    def __str__(self):
        return json.dumps(self, cls=ScreenwriterJsonEncoder, indent=4)


# most basic converter - one sentence per scene, all scenes shown for the same time
class BasicScreenwriter(Screenwriter):
    def write_screenplay(self, document):
        screenplay = super(BasicScreenwriter, self).write_screenplay(document)
        scenes = []

        sentence_count = 0
        for sentence in document.sentences():
            scene = Scene()
            scene.duration = 1.0
            scene.identifier = sentence_count

            scene_element = SceneElement()
            scene_element.content = sentence.text
            scene_element.name = "S" + str(sentence_count)
            sentence_count += 1

            scene.elements = [scene_element]
            scenes.append(scene)

        screenplay.scenes = scenes
        return screenplay

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


# fixed dimension screenwriter - you decide how many lines, how wide in characters
class FixedDimensionScreenwriter(Screenwriter):
    def __init__(self, height_in_lines=5, width_in_chars=70):
        super().__init__()
        self.height = height_in_lines
        self.width = width_in_chars

    def write_screenplay(self, document):
        screenplay = super(FixedDimensionScreenwriter, self).write_screenplay(document)
        scenes = []

        full_text = " ".join([s.text for s in document.sentences()])
        wrapped_text = textwrap.wrap(full_text, self.width)

        for i in range(0, len(wrapped_text), self.height):
            scene = Scene()
            scene.duration = 1.0
            scene.identifier = i

            scene_element = SceneElement()
            scene_element.content = "\n".join(wrapped_text[i: (i + self.height)])
            scene_element.name = "S" + str(i)

            scene.elements = [scene_element]
            scenes.append(scene)

        screenplay.scenes = scenes
        return screenplay

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


# randomized screenwriter - takes all sentences from the document and randomizes their order
# all are shown for the same amount of time
class RandomizedScreenwriter(Screenwriter):
    def write_screenplay(self, document):
        screenplay = super(RandomizedScreenwriter, self).write_screenplay(document)
        scenes = []

        sentence_count = 0
        for sentence in document.sentences():
            scene = Scene()
            scene.duration = 1.0
            scene.identifier = sentence_count

            scene_element = SceneElement()
            scene_element.content = sentence.text
            scene_element.name = "S" + str(sentence_count)
            sentence_count += 1

            scene.elements = [scene_element]
            scenes.append(scene)

        # only difference between this and the basic screenwriter
        shuffle(scenes)

        screenplay.scenes = scenes
        return screenplay

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


# only constituents of a certain height in the parse tree are returned
class ConstituentHeightScreenwriter(Screenwriter):
    def __init__(self, height=0):
        super().__init__()
        self.parser = StanfordParser()
        self.constituent_height = height

    def write_screenplay(self, document):
        screenplay = super(ConstituentHeightScreenwriter, self).write_screenplay(document)

        inputTrees = self.parser.raw_parse_sents([sentence.text for sentence in document.sentences()])

        element_count = 0
        for treeSet in inputTrees:
            for tree in treeSet:
                scene = Scene()
                scene.duration = 1.0

                # if no constituent height set, take all constituents in order of height
                if not self.constituent_height:
                    max_height = 0
                    for subtree in tree.subtrees():
                        if subtree.height() > max_height:
                            max_height = subtree.height()
                    for height in range(max_height):
                        for subtree in tree.subtrees(lambda t: t.height() == height):
                            scene_element = SceneElement()
                            scene_element.name = "Element " + str(element_count)
                            scene_element.content = ' '.join(subtree.leaves())
                            scene.addElement(scene_element)
                            element_count += 1
                else:
                    for subtree in tree.subtrees(lambda t: t.height() == self.constituent_height):
                        scene_element = SceneElement()
                        scene_element.name = "Element " + str(element_count)
                        scene_element.content = ' '.join(subtree.leaves())
                        scene.addElement(scene_element)
                        element_count += 1

                screenplay.addScene(scene)
        return screenplay

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.screenwriter_class == other.screenwriter_class \
                   and self.constituent_height == other.constituent_height
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


# print tokens as they emerge from Stanford Parser's formatting (pformat)
# This is an example of how NOT to do it
class StanfordParserScreenwriter(Screenwriter):
    def __init__(self):
        super().__init__()
        self.parser = StanfordParser()

    def write_screenplay(self, document):
        screenplay = super(StanfordParserScreenwriter, self).write_screenplay(document)

        inputTrees = self.parser.raw_parse_sents([sentence.text for sentence in document.sentences()])

        element_count = 0
        for treeSet in inputTrees:
            for tree in treeSet:
                scene = Scene()
                scene.duration = 1.0

                formatted_string = self.pformat(tree, margin=70, indent=0, nodesep='', parens='()')
                scene_element = SceneElement()
                scene_element.name = "Element " + str(element_count)
                scene_element.content = formatted_string
                scene.addElement(scene_element)
                element_count += 1

                screenplay.addScene(scene)
        return screenplay

    # stolen from NLTK tree pformat
    def pformat(self, tree, margin=70, indent=0, nodesep='', parens='()'):
        s = self._pformat_flat(tree, nodesep, parens)
        if len(s) + indent < margin:
            return s

        # If it doesn't fit on one line, then write it on multi-lines.
        s_lines = []
        for child in tree:
            if isinstance(child, Tree):
                s_lines.append('\n' + ' ' * (indent + 2) + self.pformat(child, margin, indent + 2, nodesep, parens))
            elif isinstance(child, tuple):
                s_lines.append('\n' + ' ' * (indent + 2) + "/".join(child))
            else:
                s_lines.append('\n' + ' ' * (indent + 2) + '%s' % child)
        return "".join(s_lines)

        # stolen from NLTK tree _pformat_flat

    def _pformat_flat(self, tree, nodesep, parens):
        childstrs = []
        for child in tree:
            if isinstance(child, Tree):
                childstrs.append(self._pformat_flat(child, nodesep, parens))
            elif isinstance(child, tuple):
                childstrs.append("/".join(child))
            else:
                childstrs.append('%s' % child)
        return " ".join(childstrs)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.screenwriter_class == other.screenwriter_class
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


# part-of-speech screenwriter: splits on certain POS patterns
class PartOfSpeechSplitScreenwriter(Screenwriter):
    def __init__(self):
        super().__init__()
        self.parser = StanfordParser()  # converts string to tree
        self.breaklabels = {"PP", "VP", "IN", "ADVP"}
        self.label_blacklist = {"ROOT"}

    def write_screenplay(self, document):
        screenplay = super(PartOfSpeechSplitScreenwriter, self).write_screenplay(document)

        inputTrees = self.parser.raw_parse_sents([sentence.text for sentence in document.sentences()])

        element_count = 0
        for treeSet in inputTrees:
            for tree in treeSet:
                scene = Scene()
                scene.duration = 1.0  # TODO: make this dependent on some property of sentence

                prefix_blacklist = set()
                for s in tree.treepositions():
                    if len(s) == 0:  # root of tree
                        continue
                    if not isinstance(tree[s], Tree):
                        continue
                    has_child_pp = False
                    for t in tree[s].subtrees():
                        if t == tree[s]:
                            continue
                        if t.label() in self.breaklabels and len(t.leaves()) > 1:
                            has_child_pp = True
                    # if it has a PP child, can't print it so continue
                    printed = False
                    if not has_child_pp:
                        in_blacklist = False
                        for n in range(len(s)):
                            if tuple(s[:len(s) - n]) in prefix_blacklist:
                                in_blacklist = True
                        if not in_blacklist:  # and tree[s].label() not in self.label_blacklist:
                            if len(tree[s].leaves()) == 1 and tree[s].leaves()[0] == ",":
                                screenplay.addScene(scene)
                                scene = Scene()
                                scene.duration = 1.0
                            else:
                                scene.addElement(SceneElement(" ".join(tree[s].leaves()),
                                                              tree[s].label(),
                                                              len(s)))
                            printed = True
                            prefix_blacklist.add(s)
                    if not printed:
                        print("\t", end="")
                    print(s, tree[s].label(), tree[s].leaves(), end="\n")

                element_count += 1

                screenplay.addScene(scene)
        return screenplay

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.screenwriter_class == other.screenwriter_class
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


# JSON encoding and decoding

class ScreenwriterJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BasicScreenwriter):
            return {"screenwriter_class": "Basic"}
        if isinstance(obj, RandomizedScreenwriter):
            return {"screenwriter_class": "Randomized"}
        if isinstance(obj, ConstituentHeightScreenwriter):
            return {"screenwriter_class": "ConstituentHeight",
                    "constituent_height": obj.constituent_height}
        if isinstance(obj, StanfordParserScreenwriter):
            return {"screenwriter_class": "StanfordParser"}
        if isinstance(obj, PartOfSpeechSplitScreenwriter):
            return {"screenwriter_class": "PartOfSpeechSplit"}
        return None


class ScreenwriterJsonDecoder(JSONDecoder):
    def decode(self, json_string, _w=WHITESPACE.match):
        dict_obj = super(ScreenwriterJsonDecoder, self).decode(json_string)
        screenwriter_type = dict_obj["screenwriter_class"]
        if screenwriter_type == "Basic":
            return BasicScreenwriter()
        if screenwriter_type == "Randomized":
            return RandomizedScreenwriter()
        if screenwriter_type == "ConstituentHeight":
            return ConstituentHeightScreenwriter(height=dict_obj["constituent_height"])
        if screenwriter_type == "StanfordParser":
            return StanfordParserScreenwriter()
        if screenwriter_type == "PartOfSpeechSplit":
            return PartOfSpeechSplitScreenwriter()
        return None
