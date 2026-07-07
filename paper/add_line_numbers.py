import sys
import zipfile
import tempfile
from pathlib import Path
from lxml import etree

docx = Path(sys.argv[1])

with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)

    with zipfile.ZipFile(docx) as z:
        z.extractall(tmpdir)

    document = tmpdir / "word" / "document.xml"

    tree = etree.parse(document)
    root = tree.getroot()

    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    }

    sectPr = root.find(".//w:sectPr", ns)

    ln = etree.Element(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}lnNumType"
    )
    ln.set(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}countBy",
        "1",
    )
    ln.set(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}restart",
        "continuous",
    )

    sectPr.insert(0, ln)

    tree.write(
        document,
        encoding="UTF-8",
        xml_declaration=True,
    )

    output = docx.with_name(docx.stem + "_final.docx")

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for file in tmpdir.rglob("*"):
            if file.is_file():
                z.write(file, file.relative_to(tmpdir))

print(output)
