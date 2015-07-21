"""
created by beth on 6/11/15
"""
from json import JSONEncoder
import abc

from openmind_format import Document


class DisplayFrame(object):
    def __init__(self):
        self.text_components = []
        self.display_hold_distance = 0.0

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def fromDict(dict_object):
        display_frame = DisplayFrame()
        display_frame.text_components = [TextComponent.fromDict(cp) for cp in dict_object["text_components"]]
        display_frame.display_hold_distance = float(dict_object["display_hold_distance"])
        return display_frame


class TextComponent(object):
    def __init__(self):
        self.alignment = "Left"
        # can be TopLeft, Top, TopRight, TopJustified, Left, Center, Right, Justified,
        # BottomLeft, Bottom, BottomRight, BottomJustified, BaselineLeft, Baseline,
        # BaselineRight, BaselineJustified, MidlineLeft, Midline, MidlineRight, MidlineJustified

        self.color = "white"
        self.font_name = "ARIAL SDF"
        self.font_size = 100.0
        self.font_style = "Normal"
        # can be Normal, Bold, Italic, Underline, LowerCase, UpperCase, SmallCaps, or any combination
        # such as BoldUnderline

        self.height = 100.0
        self.kerning = True
        self.line_spacing = 0.0
        self.outline_color = "gray"
        self.outline_width = 0.2
        self.overflow_mode = "Overflow"
        # can be Overflow, Ellipsis, Masking, Truncate, ScrollRect, Page

        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.rotation_z = 0.0
        self.rotation_w = 1.0
        self.text_string = ""
        self.width = 100.0
        self.word_wrapping = True
        self.relative_x_position = 0.0
        self.relative_y_position = 0.0
        self.relative_z_position = 100.0
        self.identifier = "Text"

    @staticmethod
    def fromDict(dict_object):
        text_component = TextComponent()
        text_component.alignment = dict_object["alignment"]
        text_component.color = dict_object["color"]
        text_component.font_name = dict_object["font_name"]
        text_component.font_size = float(dict_object["font_size"])
        text_component.font_style = dict_object["font_style"]
        text_component.height = float(dict_object["height"])
        text_component.kerning = bool(dict_object["kerning"])
        text_component.line_spacing = float(dict_object["line_spacing"])
        text_component.outline_color = dict_object["outline_color"]
        text_component.outline_width = float(dict_object["outline_width"])
        text_component.overflow_mode = dict_object["overflow_mode"]
        text_component.rotation_x = float(dict_object["rotation_x"])
        text_component.rotation_y = float(dict_object["rotation_y"])
        text_component.rotation_z = float(dict_object["rotation_z"])
        text_component.rotation_w = float(dict_object["rotation_w"])
        text_component.text_string = dict_object["text_string"]
        text_component.width = float(dict_object["width"])
        text_component.word_wrapping = bool(dict_object["word_wrapping"])
        text_component.relative_x_position = dict_object["relative_x_position"]
        text_component.relative_y_position = dict_object["relative_y_position"]
        text_component.relative_z_position = dict_object["relative_z_position"]
        text_component.identifier = dict_object["identifier"]
        return text_component

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class DisplayFrameJSONEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, DisplayFrame):
            print("Cannot use this class to serialize: " + str(type(obj)))
        serialized_df = {}
        if obj.display_hold_distance:
            serialized_df["display_hold_distance"] = obj.display_hold_distance
        if obj.text_components:
            text_component_encoder = TextComponentJSONEncoder()  # for serializing the text components
            serialized_df["text_components"] = [text_component_encoder.default(comp) for comp in obj.text_components]
        return serialized_df


class TextComponentJSONEncoder(JSONEncoder):
    def default(self, obj):
        serialized_component = {"alignment": obj.alignment, "color": obj.color, "font_name": obj.font_name,
                                "font_size": obj.font_size, "font_style": obj.font_style, "height": obj.height,
                                "kerning": obj.kerning, "line_spacing": obj.line_spacing,
                                "outline_color": obj.outline_color, "outline_width": obj.outline_width,
                                "overflow_mode": obj.overflow_mode, "rotation_x": obj.rotation_x,
                                "rotation_y": obj.rotation_y, "rotation_z": obj.rotation_z,
                                "rotation_w": obj.rotation_w, "text_string": obj.text_string, "width": obj.width,
                                "word_wrapping": obj.word_wrapping, "relative_x_position": obj.relative_x_position,
                                "relative_y_position": obj.relative_y_position,
                                "relative_z_position": obj.relative_z_position, "identifier": obj.identifier}
        return serialized_component


class DocumentConverter(object):
    @abc.abstractmethod
    # returns a list of DisplayFrame objects
    def format(self, document):
        if not isinstance(document, Document):
            raise Exception("Yo, this is not a document: " + str(document))
        return


# most basic formatter - there is just one part, and it is the entire sentence
class BasicDocumentConverter(DocumentConverter):
    def __init__(self):
        return

    def format(self, document):
        display_frames = []
        for sentence in document.sentences():
            display_frame = DisplayFrame()
            display_frame.display_hold_distance = 0.1

            text_component = TextComponent()
            text_component.alignment = "TopLeft"
            text_component.color = "white"
            text_component.kerning = True
            text_component.font_name = "ARIAL SDF"
            text_component.font_size = 100.0
            text_component.font_style = "Normal"
            text_component.height = 100.0
            text_component.line_spacing = 0.0
            text_component.outline_color = "gray"
            text_component.outline_width = 0.2
            text_component.overflow_mode = "Overflow"
            text_component.rotation_x = 0.0
            text_component.rotation_y = 0.0
            text_component.rotation_z = 0.0
            text_component.rotation_w = 1.0
            text_component.width = 100.0
            text_component.word_wrapping = True

            text_component.text_string = sentence.text

            display_frame.text_components = [text_component]
            display_frames.append(display_frame)
        return display_frames


        # # line length formatter
        # # taken from Noah's original line_length_converter method in simplify_wiki_html
        # class LineLengthDocumentConverter(DocumentConverter):
        # def __init__(self, line_length):
        # self.desired_line_length = line_length
        #
        # def format(self, inputString):
        # result = []
        #
        #         words = wordpunct_tokenize(inputString)
        #         num_words = len(words)
        #
        #         if num_words > 0:
        #             num_sentence_parts = ceil(num_words / self.desired_line_length)
        #
        #             for i in range(0, num_sentence_parts):
        #                 start = i * self.desired_line_length
        #                 end = start + self.desired_line_length if start + self.desired_line_length < num_words else num_words
        #                 result.append(SentenceFragment(importance=0, text=' '.join(words[start:end]), tokens=words[start:end]))
        #         return result
        #
        #
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
        # # only constituents of a certain length in tokens are returned
        # class ConstituentTokenLengthSentenceFormatter(SentenceFormatter):
        #     def __init__(self, parser, min_length=0, max_length=20):
        #         if not isinstance(parser, StanfordParser):
        #             raise Exception("ConstituentSentenceFormatter: Argument for parser is not a StanfordParser object.")
        #         self.parser = parser  # converts string to tree
        #         self.min_length = min_length
        #         self.max_length = max_length
        #
        #     def format(self, inputString):
        #         inputTrees = self.parser.raw_parse(inputString)
        #         result = []
        #
        #         for treeSet in inputTrees:
        #             for tree in treeSet:
        #                 for subtree in tree.subtrees(lambda t: self.min_length <= len(t.leaves()) <= self.max_length):
        #                     result.append(SentenceFragment(importance=len(subtree.leaves()), tokens=subtree.leaves(),
        #                                                    text=' '.join(subtree.leaves())))
        #         return result