"""
Screenwriters turn Document objects into Screenplays
created by beth on 7/22/15
"""
import abc
from random import shuffle

from nltk import Tree
from nltk.parse.stanford import StanfordParser

from document import Document
from screenplay import Screenplay, Scene, SceneElement


class Screenwriter(object):
    @abc.abstractmethod
    # returns a list of DisplayFrame objects
    def write_screenplay(self, document):
        if not isinstance(document, Document):
            raise Exception("Yo, this is not a document: " + str(document))
        return


# most basic converter - one sentence per scene, all scenes shown for the same time
class BasicScreenwriter(Screenwriter):
    def __init__(self):
        return

    def write_screenplay(self, document):
        screenplay = Screenplay()
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

        screenplay.title = document.header
        screenplay.scenes = scenes
        return screenplay


# randomized screenwriter - takes all sentences from the document and randomizes their order
# all are shown for the same amount of time
class RandomizedScreenwriter(Screenwriter):
    def __init__(self):
        return

    def write_screenplay(self, document):
        screenplay = Screenplay()
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

        screenplay.title = document.header
        screenplay.scenes = scenes
        return screenplay


# only constituents of a certain height in the parse tree are returned
class ConstituentHeightScreenwriter(Screenwriter):
    def __init__(self, parser, height=0):
        if not isinstance(parser, StanfordParser):
            raise Exception("ConstituentHeightScreenwriter: Argument for parser is not a StanfordParser object.")
        self.parser = parser
        self.constituent_height = height

    def write_screenplay(self, document):
        screenplay = Screenplay()
        screenplay.title = document.header

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


# print tokens as they emerge from Stanford Parser's formatting (pformat)
class StanfordParserScreenwriter(Screenwriter):
    def __init__(self, parser):
        if not isinstance(parser, StanfordParser):
            raise Exception("StanfordParserScreenwriter: Argument for parser is not a StanfordParser object.")
        self.parser = parser  # converts string to tree

    def write_screenplay(self, document):
        screenplay = Screenplay()
        screenplay.title = document.header

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


# part-of-speech screenwriter: splits on certain POS patterns
class PartOfSpeechSplitScreenwriter(Screenwriter):
    def __init__(self, parser):
        if not isinstance(parser, StanfordParser):
            raise Exception("StanfordParserScreenwriter: Argument for parser is not a StanfordParser object.")
        self.parser = parser  # converts string to tree
        self.breaklabels = {"PP", "VP", "IN", "ADVP"}
        self.label_blacklist = {"ROOT"}

    def write_screenplay(self, document):
        screenplay = Screenplay()
        screenplay.title = document.header

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
