"""
Process the text output of a wikipedia dump
- Identify articles that are good candidates for reading-gooder
- Generate automated reading comprehension questions

created by noah on 4/15/15
updated by beth on 6/15/15 (to python 3)
"""

import sys
import json
import re

from lxml import html
from lxml import etree


ROOT_LEVEL = 0
MAX_LEVEL = 5


class HtmlSection:
    tag = ''
    text = ''
    level = 0

    def __init__(self, element):
        self.tag = element.tag
        self.text = element.text

        first_digit = re.search('\d', self.tag)

        if first_digit:
            self.level = int(self.tag[first_digit.start()])
        elif self.tag == 'static':
            self.level = ROOT_LEVEL
        else:
            self.level = MAX_LEVEL

    def __str__(self):
        return '%s' % self.tag

    def __repr__(self):
        return '%s' % self.tag

    def __hash__(self):
        return hash(self.tag)


H2 = "<h2>"
H3 = "<h3>"
H4 = "<h4>"
LI = "<li>"
SENT = "<sentence>"

H2_ELEMENT = HtmlSection(html.fromstring(H2))
H3_ELEMENT = HtmlSection(html.fromstring(H3))
H4_ELEMENT = HtmlSection(html.fromstring(H4))
LI_ELEMENT = HtmlSection(html.fromstring(LI))
SENT_ELEMENT = HtmlSection(html.fromstring(SENT))


def clear_sections(section_headers, current_section):
    for key in section_headers:
        if key >= current_section:
            section_headers[key] = ''


def update_section(line, previous_section, section_headers):
    """
    Update the section headers.
    When you enter a new section, the subsection headers below you in the outline
    should be set to None
    :param section_headers:
    :return:
    """
    try:
        element = html.fromstring(line)

        new_section = HtmlSection(element)

        if previous_section.level >= new_section.level:
            clear_sections(section_headers, new_section)
            print('Cleared sections below', new_section)

        section_headers[new_section] = new_section.text

    except etree.ParserError as e:
        # Generally this means we have reached the end of an article </doc>
        print(e)
        return None

    return new_section


def build_json(section_headers, line):
    result = section_headers.copy()
    result[SENT_ELEMENT] = line

    str_result = dict((k.tag, v) for k, v in result.iteritems())

    return json.dumps(str_result)


def parse_article(input_file):
    # outline = create_article_outline(etree.parse(input_file))

    section_headers = {H2_ELEMENT: '', H3_ELEMENT: '', H4_ELEMENT: '', LI_ELEMENT: ''}
    current_section = HtmlSection(html.fromstring('<title>Train</title>'))

    with open(input_file) as file:
        # Skip the document information for now
        next(file)
        for line in file:
            line = line.strip()

            if line != '':
                if line.startswith('<'):
                    current_section = update_section(line, current_section, section_headers)
                    if current_section is None:
                        print('Finished processing article')
                        break
                else:
                    encoded = build_json(section_headers, line)
                    print(encoded)


def create_article_outline(doc):
    """
    :param doc: An etree object containing the wikipedia article
    :return: A json object containing the article outline
    """
    print("Creating article outline...")
    root = doc.getroot()

    outline = []

    outline.append({'label': root.attrib['title'], 'class': 'title'})

    for child in root:
        outline.append({'label': child.text, 'class': child.tag})

    return json.dumps(outline, indent=4, separators=(',', ': '))


def main():
    parse_article("/Users/noah/Data/Wikipedia/TrainExtract/AA/wiki_00")
    pass


if __name__ == '__main__':
    sys.exit(main())