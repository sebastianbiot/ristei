# ristei
ristei is a Python script that converts RIS records to TEI bibliographical items.

RIS (Research Information Systems) files, sometimes referred to as RefMan files, contain bibliographical information presented as plain-text lists of key/value pairs. RIS files are commonly offered as one of the bibliography export formats on sites like Google Scholar, JSTOR, ResearchGate, etc.

TEI (Text Encoding Initiative) files are XML files used to represent text (manuscripts, letters, fiction, poetry, etc.) in digital forms. TEI files may contain references to bibliographical items.

ristei converts the content of RIS files into XML sections, i.e. a sequence of `biblStruct` elements, that can be added to TEI files.

## Caveat
ristei is a small Python 3 script, written for personal purposes. It is easy to use but requires some familiarity with the terminal. I wrote it on macOS Monterey (12.3.1) running Python 3 (3.10.4) and have not tested it in other environments.

Both RIS and TEI allow for a wide variety of documents to be encoded in their respective formats. ristei focuses on journal articles and books.

## Usage
    ./ristei.py a_file.ris <another_file.ris> <etc.ris>

That’s it. There are currently no command-line options.

## License
MIT License

Copyright (c) 2022 Sebastian Biot

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
