"""
reads from raw transcription results json file, outputs to database or folder of files
created by beth on 7/3/15
"""
import json
import os
import sys

from single_convert import do_conversion, sentenceformatter_factory, stanfordparser_factory


if __name__ == "__main__":
    transcription_results_file = sys.argv[1]
    output_directory = sys.argv[2]
    stanford_parser_directory = sys.argv[3]
    stanford_parser_models_directory = sys.argv[4]

    transcripts = json.loads(open(transcription_results_file, "r").read())

    for formatter_name in ["default", "stanfordparser"]:
        formatter = sentenceformatter_factory(formatter_name, stanfordparser_factory(stanford_parser_directory,
                                                                                     stanford_parser_models_directory))
        for transcript in transcripts:
            document_text = transcript["passageText"]
            file_identifier = transcript["fileIdentifier"]
            output_file = os.path.join(output_directory,
                                       os.path.splitext(file_identifier)[0] + "-" + formatter_name + ".txt")
            do_conversion(formatter, "Basic", document_text, file_identifier, output_file)
