"""
Screenwriters turn Document objects into Screenplays
created by beth on 7/22/15
"""
import abc

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

            scene_element = SceneElement()
            scene_element.content = sentence.text
            scene_element.identifier = "Sentence " + str(sentence_count)
            sentence_count += 1

            scene.elements = [scene_element]
            scenes.append(scene)

        screenplay.title = document.header
        screenplay.scenes = scenes
        return screenplay


# only constituents of a certain length in tokens are returned
class ConstituentHeightScreenwriter(Screenwriter):
    def __init__(self, parser, height=0):
        if not isinstance(parser, StanfordParser):
            raise Exception("ConstituentTokenLengthScreenwriter: Argument for parser is not a StanfordParser object.")
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
                            scene_element.identifier = "Element " + str(element_count)
                            scene_element.content = ' '.join(subtree.leaves())
                            scene.addElement(scene_element)
                            element_count += 1
                else:
                    for subtree in tree.subtrees(lambda t: t.height() == self.constituent_height):
                        scene_element = SceneElement()
                        scene_element.identifier = "Element " + str(element_count)
                        scene_element.content = ' '.join(subtree.leaves())
                        scene.addElement(scene_element)
                        element_count += 1

                screenplay.addScene(scene)
        return screenplay


        # # naive implementation of vstf: trees are flattened and returned as lists of SentenceFragment objects
        # class StupidVstfSentenceFormatter(SentenceFormatter):
        #     def __init__(self, max_words_per_part, parser):
        #         self.max_words_per_part = max_words_per_part
        #         if not isinstance(parser, StanfordParser):
        #             raise Exception("StupidVstfFormatter: Argument for parser is not a StanfordParser object.")
        #         self.parser = parser  # converts string to tree
        #
        #     def format(self, inputString):
        #         # parse the sentence into a tree
        #         inputTrees = self.parser.raw_parse(inputString)
        #
        #         result = []
        #
        #         for treeSet in inputTrees:
        #             for tree in treeSet:
        #                 depth = 0
        #                 part = SentenceFragment(importance=depth * 2)
        #
        #                 # the "flattened" tree is just a list of the tokens, in order
        #                 for string_token in tree.flatten():
        #                     if string_token in string.punctuation:
        #                         part.append(string_token)
        #                         part.text = ' '.join(part.tokens)
        #                         result.append(part)
        #                         depth = 1  # only the very first line in the sentence is flush left; the rest are at depth = 1
        #                         part = SentenceFragment(importance=depth * 2)
        #                     elif part.len() >= self.max_words_per_part:
        #                         part.text = ' '.join(part.tokens)
        #                         result.append(part)
        #                         depth += 1
        #                         part = SentenceFragment(importance=depth * 2)
        #                         part.append(string_token)
        #                     else:
        #                         part.append(string_token)
        #
        #         return result
        #
        #
        # # format according to term frequency
        # class TermFrequencySentenceFormatter(SentenceFormatter):
        #     def format(self, inputString):
        #         tokens = wordpunct_tokenize(inputString)
        #         tags = pos_tag(tokens)
        #         text = Text(tokens)
        #         result = []
        #
        #         last_token_count = 0
        #         part = []
        #         for i in range(len(tags)):
        #             word = tags[i][0]
        #             tag = tags[i][1]
        #             token_count = text.count(word)
        #             if word[0] in string.punctuation:
        #                 part.append((word, tag, token_count))
        #                 self.appendToResult(part, result)
        #                 part = []
        #             elif token_count > last_token_count:
        #                 self.appendToResult(part, result)
        #                 part = [(word, tag, token_count)]
        #             else:
        #                 part.append((word, tag, token_count))
        #             last_token_count = token_count
        #         self.appendToResult(part, result)
        #         return result
        #
        #     def appendToResult(self, part, result):
        #         if len(part) > 0:
        #             result.append(SentenceFragment(importance=part[0][2],
        #                                            tokens=[e[0] for e in part],
        #                                            text=" ".join([e[0] for e in part])))
        #
        #
        # # print tokens as they emerge from Stanford Parser's formatting (pformat)
        # class StanfordParserSentenceFormatter(SentenceFormatter):
        #     def __init__(self, max_words_per_part, parser):
        #         self.max_words_per_part = max_words_per_part
        #         if not isinstance(parser, StanfordParser):
        #             raise Exception("StanfordParserSentenceFormatter: Argument for parser is not a StanfordParser object.")
        #         self.parser = parser  # converts string to tree
        #
        #     def format(self, inputString):
        #         inputTrees = self.parser.raw_parse(inputString)
        #
        #         for treeSet in inputTrees:
        #             formatted_string = self.pformat(treeSet[0], margin=70, indent=0, nodesep='', parens='()')
        #             fragments = []
        #             for string_fragment in formatted_string.split('\n'):
        #                 fragments.append(SentenceFragment(importance=self.getIndent(string_fragment),
        #                                                   tokens=self.getTokens(string_fragment),
        #                                                   text=self.getText(string_fragment)))
        #
        #             # first pass - eliminate empty rows
        #             clean_fragments = self.eliminateEmptyRows(fragments)
        #
        #             # second pass - clean up individual fragments
        #             clean_fragments = self.cleanIndividualFragments(clean_fragments)
        #
        #             # third pass - connect fragments
        #             clean_fragments = self.connectFragments(clean_fragments)
        #
        #             return clean_fragments
        #
        #     def eliminateEmptyRows(self, fragment_list):
        #         clean_fragments = []
        #         for fragment in fragment_list:
        #             if not fragment.text:
        #                 continue
        #             clean_fragments.append(fragment)
        #         return clean_fragments
        #
        #     def cleanIndividualFragments(self, fragment_list):
        #         clean_fragments = []
        #         for fragment in fragment_list:
        #             new_text = fragment.text.replace("-LRB- ", "(").replace(" -RRB-", ")")
        #             new_text = new_text.replace("``", "\"").replace("''", "\"")
        #             for quoted_part in re.findall(r'\".+?\"', new_text):
        #                 new_text = new_text.replace(quoted_part, quoted_part.replace('\" ', '\"').replace(' \"', '\"'))
        #             new_fragment = SentenceFragment(importance=fragment.indent,
        #                                             tokens=self.getTokens(new_text),
        #                                             text=new_text)
        #             clean_fragments.append(new_fragment)
        #         return clean_fragments
        #
        #     def connectFragments(self, fragment_list):
        #         temp = []
        #         open_quote = False
        #         connected_fragment = []
        #         for fragment in fragment_list:
        #             if re.match("[.,;:]", fragment.text):
        #                 connected_fragment.append(fragment)
        #                 temp.append(connected_fragment)
        #                 connected_fragment = []
        #             elif re.match("\"", fragment.text):
        #                 if open_quote:
        #                     connected_fragment.append(fragment)
        #                     temp.append(connected_fragment)
        #                     connected_fragment = []
        #                     open_quote = False
        #                 else:
        #                     if len(connected_fragment) > 0:
        #                         temp.append(connected_fragment)
        #                     connected_fragment = [fragment]
        #                     open_quote = True
        #             else:
        #                 if len(connected_fragment) > 0 and not open_quote:
        #                     temp.append(connected_fragment)
        #                     connected_fragment = [fragment]
        #                 else:
        #                     connected_fragment.append(fragment)
        #         clean_fragments = []
        #         for c in temp:
        #             clean_fragments.append(SentenceFragment(importance=max([f.indent for f in c]),
        #                                                     tokens=[t for f in c for t in f.tokens],
        #                                                     text="".join([f.text for f in c])))
        #         return clean_fragments
        #
        #     def getIndent(self, a):
        #         return len(a) - len(a.lstrip(' '))
        #
        #     def getTokens(self, a):
        #         return [e for e in a.split()]
        #
        #     def getText(self, a):
        #         return a.lstrip()
        #
        #     # stolen from NLTK tree pformat
        #     def pformat(self, tree, margin=70, indent=0, nodesep='', parens='()'):
        #         s = self._pformat_flat(tree, nodesep, parens)
        #         if len(s) + indent < margin:
        #             return s
        #
        #         # If it doesn't fit on one line, then write it on multi-lines.
        #         s_lines = []
        #         for child in tree:
        #             if isinstance(child, Tree):
        #                 s_lines.append('\n' + ' ' * (indent + 2) + self.pformat(child, margin, indent + 2, nodesep, parens))
        #             elif isinstance(child, tuple):
        #                 s_lines.append('\n' + ' ' * (indent + 2) + "/".join(child))
        #             else:
        #                 s_lines.append('\n' + ' ' * (indent + 2) + '%s' % child)
        #         return "".join(s_lines)
        #
        #     # stolen from NLTK tree _pformat_flat
        #     def _pformat_flat(self, tree, nodesep, parens):
        #         childstrs = []
        #         for child in tree:
        #             if isinstance(child, Tree):
        #                 childstrs.append(self._pformat_flat(child, nodesep, parens))
        #             elif isinstance(child, tuple):
        #                 childstrs.append("/".join(child))
        #             else:
        #                 childstrs.append('%s' % child)
        #         return " ".join(childstrs)
        #
        #
        # # every constituent in the parse is returned in order of size as a SentenceFragment
        # class ConstituentHeightSentenceFormatter(SentenceFormatter):
        #     def __init__(self, parser, constituent_height=None):
        #         if not isinstance(parser, StanfordParser):
        #             raise Exception("ConstituentSentenceFormatter: Argument for parser is not a StanfordParser object.")
        #         self.parser = parser  # converts string to tree
        #         self.constituent_height = constituent_height
        #
        #     def format(self, inputString):
        #         # parse the sentence into a tree
        #         inputTrees = self.parser.raw_parse(inputString)
        #         result = []
        #
        #         for treeSet in inputTrees:
        #             for tree in treeSet:
        #                 # if no constituent height set, take all constituents in order of height
        #                 if not self.constituent_height:
        #                     max_height = 0
        #                     for subtree in tree.subtrees():
        #                         if subtree.height() > max_height:
        #                             max_height = subtree.height()
        #                     for height in range(max_height):
        #                         for subtree in tree.subtrees(lambda t: t.height() == height):
        #                             result.append(SentenceFragment(importance=subtree.height(), tokens=subtree.leaves(),
        #                                                            text=' '.join(subtree.leaves())))
        #                 else:
        #                     for subtree in tree.subtrees(lambda t: t.height() == self.constituent_height):
        #                         result.append(SentenceFragment(importance=subtree.height(), tokens=subtree.leaves(),
        #                                                        text=' '.join(subtree.leaves())))
        #         return result
        #
        #
