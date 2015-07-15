"""
reads from raw transcription results json file, outputs to database or folder of files
created by beth on 7/3/15
"""
import json
import os
import sys
import datetime

from single_convert import sentenceformatter_factory, stanfordparser_factory, do_conversion


if __name__ == "__main__":
    transcription_results_file = sys.argv[1]  # file format here is json (json export from Google Spreadsheet)
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
            transcriber_name = transcript["transcriberName"]
            timestamp = datetime.datetime.strptime(transcript["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")

            output_file = os.path.join(output_directory, file_identifier + "-" + formatter_name + "-" +
                                       transcriber_name + ".json")
            print(output_file)
            do_conversion(formatter, "Basic", document_text, file_identifier, output_file)
