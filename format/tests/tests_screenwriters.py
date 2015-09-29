import os
import unittest

from screenwriters import *


class ScreenwriterSerializationTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['STANFORD_PARSER'] = "../../resources"
        os.environ['STANFORD_MODELS'] = "../../resources"

    def testReconstituteScreenwriter(self):
        # BasicScreenwriter test
        screenwriter = BasicScreenwriter()
        serialized_json = json.dumps(screenwriter, cls=ScreenwriterJsonEncoder, sort_keys=True)
        deserialized_screenwriter = json.loads(serialized_json, cls=ScreenwriterJsonDecoder)
        self.assertEquals(screenwriter, deserialized_screenwriter)

        # RandomizedScreenwriter test
        screenwriter = RandomizedScreenwriter()
        serialized_json = json.dumps(screenwriter, cls=ScreenwriterJsonEncoder, sort_keys=True)
        deserialized_screenwriter = json.loads(serialized_json, cls=ScreenwriterJsonDecoder)
        self.assertEquals(screenwriter, deserialized_screenwriter)

        # ConstituentHeightScreenwriter test
        screenwriter = ConstituentHeightScreenwriter(height=3)
        serialized_json = json.dumps(screenwriter, cls=ScreenwriterJsonEncoder, sort_keys=True)
        deserialized_screenwriter = json.loads(serialized_json, cls=ScreenwriterJsonDecoder)
        self.assertEquals(screenwriter, deserialized_screenwriter)

        # StanfordParserScreenwriter test
        screenwriter = StanfordParserScreenwriter()
        serialized_json = json.dumps(screenwriter, cls=ScreenwriterJsonEncoder, sort_keys=True)
        deserialized_screenwriter = json.loads(serialized_json, cls=ScreenwriterJsonDecoder)
        self.assertEquals(screenwriter, deserialized_screenwriter)

        # PartOfSpeechSplitScreenwriter test
        screenwriter = PartOfSpeechSplitScreenwriter()
        serialized_json = json.dumps(screenwriter, cls=ScreenwriterJsonEncoder, sort_keys=True)
        deserialized_screenwriter = json.loads(serialized_json, cls=ScreenwriterJsonDecoder)
        self.assertEquals(screenwriter, deserialized_screenwriter)
