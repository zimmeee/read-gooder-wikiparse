import json
import unittest

from screenplay import ScreenplayJSONEncoder, Screenplay
from screenwriters import BasicScreenwriter
from raw_converters import BasicTextFileRawConverter


class ScreenplaySerializationTestCase(unittest.TestCase):
    def setUp(self):
        doc_source = "Supernovas are among the most energetic events in the universe and result in the " \
                     "complete disruption of stars at the end of their lives. Originally, the distinction " \
                     "between Type I and Type II supernovas was based solely on the presence or absence of " \
                     "hydrogen atoms (hydrogen lines). Supernovas without hydrogen lines were called Type I, " \
                     "while those with hydrogen lines were Type II. Subsequent analysis of many of these events " \
                     "revealed that this empirical classification schema instead reflected two different mechanisms " \
                     "for the supernova explosion. Type I supernovas happen in binary stars — two stars that orbit " \
                     "closely each other — when one of the two binary stars is a small, dense, white dwarf star. " \
                     "If the companion star ranges too close to the white dwarf that it is orbiting, the white dwarf’s " \
                     "gravitational pull will draw matter from the other star. When the white dwarf acquires enough " \
                     "matter to become at least 1.4 times as big as the Sun, it collapses and explodes in a supernova. " \
                     "Type II supernovas occur when a star, much more massive than the Sun, ends its life. " \
                     "When such a star begins burning out, the core of the star quickly collapses releasing amazing " \
                     "energy in the form of neutrinos, a kind of particle smaller than even an atom. Electromagnetic " \
                     "radiation — energy that is electric and magnetic — causes the star to explode in a supernova. " \
                     "Whereas Type I supernovas typically destroy their parent stars, Type II explosions usually leave " \
                     "behind the stellar core. The classification schema regarding the mechanism for supernova " \
                     "explosions helps to more succinctly answer the question: Is the Sun in danger of becoming a " \
                     "supernova? Neither does our Sun have a companion star orbiting it nor does our Sun have the mass " \
                     "necessary to become a supernova. Furthermore, it will be another billion years until the Sun runs " \
                     "out of fuel and swells into a red giant star before going into a white dwarf form."
        doc_title = "Supernova"
        self.document = BasicTextFileRawConverter().convertToDocument(doc_source, doc_title)

    def runTest(self):
        converter = BasicScreenwriter()
        screenplay = converter.write_screenplay(self.document)
        serialized_json = json.dumps(screenplay, cls=ScreenplayJSONEncoder, sort_keys=True)
        deserialized_screenplay = Screenplay.fromDict(json.loads(serialized_json))
        self.assertEquals(screenplay, deserialized_screenplay)
