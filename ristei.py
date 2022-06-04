#!/usr/bin/env python3

"""
A script to convert (RefMan) RIS files to TEI biblStructs.
"""

import argparse
import datetime
import logging
import sys
import re

from typing import Optional  # Spend enough time with Swift
                             # and optionals grow on you.

from xml.dom.minidom import Document
from xml.dom.minidom import Element
from xml.dom.minidom import getDOMImplementation


class RISDate:
    """Convenience class to convert RIS dates into TEI dates

    Easily converts from RIS’s date format to an XML-compatible
    representation of date (as a value and as an attribute).
    """

    __year = None
    __month = None
    __season = None

    def __init__(self, value: str) -> None:
        """Constructor

        Arg:
            value: A RIS date string. RIS date string look like
                this year/month/day/season; every element except
                the year is optional.
        """
        if not value:
            raise ValueError

        split_date = value.split("/")
        if not split_date:
            raise ValueError

        self.__year = split_date[0]
        if not self.__year:
            raise ValueError

        try:
            self.__month = split_date[1]
            self.__season = split_date[3]
            # Drop day token
        except IndexError:
            pass

    def toValue(self) -> str:
        """Returns a human-readable, simplified date"""
        if self.__season:
            return f"{self.__season} {self.__year}"
        elif self.__month:
            d = datetime.date(int(self.__year), int(self.__month), 1)
            return f"{d.strftime('%B')} {self.__year}"
        return self.__year

    def toAttr(self) -> str:
        """Returns a TEI-compliant attribute date"""
        if self.__month:
            return f"{self.__year}-{self.__month}"
        return f"{self.__year}"

"""
"""
class BiblioItem:
    """A bibliographical item

    Manages the transition between an RIS representation of a bibliographical
    item and a TEI representation of the same."""

    values: dict[str, str] = {}
    xmlDoc: Document = None

    dumb_apostrophes: re.Pattern = re.compile("(\S)'([std]|ll)", re.I)
    doi_prefix: re.Pattern = re.compile("DOI:\s*", re.I)

    def __init__(self, kv_pairs: list[list[str]]) -> None:
        """Constructor

        Arg:
            kv_pairs: A list of lists; each list is a two-item list
                containing an RIS key and a value.
        """
        self.authors: list[str] = [v.strip() for k, v in kv_pairs if k in ["AU", "A1"]]
        self.editors: list[str] = [v.strip() for k, v in kv_pairs if k in ["A3"]]
        self.values = {k: v.strip() for k, v in kv_pairs}

    def toXML(self, doc: Document) -> Element:
        """Returns a TEI bibliography item

        Arg:
            doc: The XML document to which this instance of
                a TEI item is attached.
        """
        self.xmlDoc = doc

        struct = self.createElement("biblStruct")

        analytic = self.analytic()
        if analytic:
            struct.appendChild(analytic)

        monogr = self.monogr()
        if monogr:
            struct.appendChild(monogr)

        series = self.series()
        if series:
            struct.appendChild(series)

        return struct

    def createElement(self, elementName: str) -> Element:
        """Creates and returns an empty element

        Arg:
            elementName: name of teh element to be created
        """
        return self.xmlDoc.createElement(elementName)

    def createTextElement(self, elementName: str, value: str) -> Element:
        """Creates and returns a simple text element

        Args:
            elementName: name of the element to be created
            value: the value of the element to be created
        """
        elem = self.createElement(elementName)
        node = self.xmlDoc.createTextNode(value)
        elem.appendChild(node)
        return elem

    def createElementFrom(
            self,
            elementName: str,
            keys: list[str],
            attrs: Optional[list[str, str]] = None) -> Optional[Element]:
        """Creates and returns an element

        Args:
            elementName: name of the element to be created
            keys: a list of RIS keys from which the value of the element
                will be determined. The method will iterate through the
                list until it finds an valid/existing key then stop.
            attrs: an optional two-element list containing an attribute 
                name and an attribute value.
        """
        value = None
        for key in keys:
            if key in self.values:
                value = self.fix_dumb_typography(self.values[key])
                element = self.createTextElement(elementName, value)
                if attrs:
                    element.setAttribute(attrs[0], attrs[1])
                return element

    def analytic(self):
        pass

    def monogr(self):
        pass

    def series(self) -> Optional[Element]:
        """Returns a series element"""
        series = self.createElement("series")

        title = self.series_title()
        if title:
            series.appendChild(title)
            return series

    def person(self, name: str) -> Element:
        """Returns an element representing a person’s name

        Args:
            name: A string representation of a person’s name.
                Expected to be something like Last, First M.
        """
        names = name.split(",")
        surname = self.createTextElement("surname", names[0].strip())
        forename = self.createTextElement("forename", names[1].strip())

        person = self.createElement("persName")
        person.appendChild(forename)
        person.appendChild(surname)
        return person

    def authorship(self, name: str) -> Element:
        """Returns one or more author element

        See person() about arg.
        """
        author = self.createElement("author")
        author.appendChild(self.person(name))
        return author

    def editorship(self, name: str) -> Element:
        """Returns one or more editor element

        See person() about arg.
        """
        editor = self.createElement("editor")
        editor.appendChild(self.person(name))
        return editor

    def imprint(self) -> Element:
        """Returns imprint element"""
        imprint = self.createElement("imprint")

        pub_place = self.pub_place()
        if pub_place:
            imprint.appendChild(pub_place)

        publisher = self.publisher()
        if publisher:
            imprint.appendChild(publisher)

        date = self.date()
        if date:
            imprint.appendChild(date)

        return imprint

    def date(self) -> Optional[Element]:
        """Returns imprint date element"""
        date = None
        if "Y1" in self.values:
            date = self.values["Y1"]
        elif "PY" in self.values:
            date = self.values["PY"]

        if date:
            try:
                ris_date = RISDate(date)
                el_date = self.createTextElement("date", ris_date.toValue())
                el_date.setAttribute("when", ris_date.toAttr())
                return el_date
            except ValueError:
                logging.warning(f"Unable to parse Imprint date: {date}")

    def title(self) -> Optional[Element]:
        """Returns item title element"""
        return self.createElementFrom("title", ["TI", "T1"])

    def series_title(self) -> Optional[Element]:
        """Returns series title element"""
        return self.createElementFrom("title", ["T2", "T3"], ["level", "s"])

    def pub_place(self) -> Optional[Element]:
        """Returns publisher’s city element"""
        return self.createElementFrom("pubPlace", ["CY"])

    def publisher(self) -> Optional[Element]:
        """Returns publisher element"""
        return self.createElementFrom("publisher", ["PB"])

    def fix_dumb_typography(self, value: str) -> str:
        match = self.dumb_apostrophes.search(value)
        if match:
            value = self.dumb_apostrophes.sub("\\1’\\2", value)
        return value


class Book(BiblioItem):
    """A book"""

    def monogr(self) -> Element:
        """Returns monograph element"""
        root = self.createElement("monogr")

        for name in self.authors:
            root.appendChild(self.authorship(name))
        for name in self.editors:
            root.appendChild(self.editorship(name))

        title = self.title()
        if title:
            root.appendChild(title)

        isbn = self.isbn()
        if isbn:
            root.appendChild(isbn)

        imprint = self.imprint()
        if imprint:
            root.appendChild(imprint)

        series = self.series()
        if series:
            series.appendChild(series)

        return root

    def isbn(self) -> Optional[Element]:
        """Returns ISBN element"""
        return self.createElementFrom("idno", ["SN"], ["type", "ISBN"])


class Journal(BiblioItem):
    """A journal"""

    def analytic(self) -> Element:
        """Returns analytic element"""
        root = self.createElement("analytic")

        # Add all primary authors first
        for name in self.authors:
            root.appendChild(self.authorship(name))

        # Add title
        title = self.title()
        if title:
            root.appendChild(title)

        # Identification schemes
        doi = self.doi()
        if doi:
            root.appendChild(doi)

        issn = self.issn()
        if issn:
            root.appendChild(issn)

        return root

    def monogr(self) -> Element:
        """Returns monograph element"""
        root = self.createElement("monogr")

        # Add journal title
        journal_title = self.journal_title()
        if journal_title:
            root.appendChild(journal_title)

        # Imprint
        imprint = self.imprint()
        if imprint:
            root.appendChild(imprint)

        # Scopes
        volume = self.volume()
        if volume:
            root.appendChild(volume)

        issue = self.issue()
        if issue:
            root.appendChild(issue)

        pages = self.pages()
        if pages:
            root.appendChild(pages)

        return root

    def pages(self) -> Optional[Element]:
        """Returns page (range) element"""
        if ("SP" in self.values):
            start_page = self.values["SP"]

            if ("EP" in self.values):
                end_page = self.values["EP"]
            else:
                # Some RIS files sometimes lazily use
                # SP only to indicate a page range.
                split = start_page.split("-")
                try:
                    start_page = split[0]
                    end_page = split[1]
                except IndexError:
                    logging.warning(f"Unable to parse SP as range: {start_page}")

            if start_page and end_page:
                pages = f"{start_page}–{end_page}"

                elem = self.createTextElement("biblScope", pages)
                elem.setAttribute("unit", "page")
                elem.setAttribute("from", start_page)
                elem.setAttribute("to", end_page)
                return elem

    def doi(self) -> Optional[Element]:
        """Returns DOI element"""
        if ("DO" in self.values):
            # Some providers include a "DOI: " prefix which
            # shouldn’t be included.
            doi = self.doi_prefix.sub("", self.values["DO"])
            elem = self.createTextElement("idno", doi)
            elem.setAttribute("type", "DOI")
            return elem

    def journal_title(self) -> Optional[Element]:
        """Returns journal title element"""
        return self.createElementFrom("title", ["JO", "T2"], ["level", "j"])

    def volume(self) -> Optional[Element]:
        """Returns volume element"""
        return self.createElementFrom("biblScope", ["VL"], ["unit", "volume"])

    def issue(self) -> Optional[Element]:
        """Returns issue element"""
        return self.createElementFrom("biblScope", ["IS"], ["unit", "issue"])

    def issn(self) -> Optional[Element]:
        """Returns ISSN element"""
        return self.createElementFrom("idno", ["SN"], ["type", "ISSN"])

"""
"""
class TeiFile:
    """A TEI-compliant bibliography file"""

    separator = '  -'

    def __init__(self) -> None:
        self.records = []

    def parse(self, source_files: list[str]) -> None:
        """Reads one or more RIS file.

        Takes a list of paths to RIS files, reads each one
        of them, and adds their content to an instance of
        TeiFile for later output.

        Args:
            source_files: A list of paths to RIS files
        """
        for source_file in source_files:
            try:
                with open(source_file, encoding="utf-8") as f:
                    kv_pairs = []

                    for line in f:
                        kv_pair = line[:-1].split(self.separator)

                        # In RIS files, ER signals the end of a record.
                        if kv_pair[0] == "ER":
                            self.add_record(kv_pairs)
                            kv_pairs = []
                        else:
                            kv_pairs.append(kv_pair)
            except FileNotFoundError:
                logging.error(f"Unable to find file “{source_file}”")

    def add_record(self, kv_pairs: list[list[str]]) -> None:
        """Adds a set of RIS key/value pairs to an instance of TeiFile.

        Adds an item to this instance TeiFile’s catalog of RIS records.
        Each item in the catalog will be converted into a Book or a Journal
        object to be output as TEI.

        Args:
            kv_pairs: A list of lists; each list contains two strings,
                one representing an RIS key, the other a text value for
                that key.
        """
        record = None
        r_type = kv_pairs[0][1].strip()

        match r_type:
            case "JOUR":    # Journal article
                record = Journal(kv_pairs)
            case "BOOK":    # Book
                record = Book(kv_pairs)
            case "EDBOOK":  # Edited book
                record = Book(kv_pairs)
            case "EBOOK":   # Electronic book
                record = Book(kv_pairs)
            case _:
                print(f"{r_type} is not a supported RIS type.")

        if record:
            self.records.append(record)

    def toXML(self) -> None:
        """Returns TEI bibliography"""
        dom = getDOMImplementation()
        doc = dom.createDocument("", "listBibl", "")
        top = doc.documentElement

        for record in self.records:
            child = record.toXML(doc)
            top.appendChild(child)

        return doc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", nargs='+', help="Path to source RIS file")
    args = parser.parse_args()

    f = TeiFile()
    f.parse(args.source)

    tei = f.toXML()
    print(tei.toprettyxml(indent="  "))

    return 0


if __name__ == '__main__':
    sys.exit(main())
