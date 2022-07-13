import re, sqlite3
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse

DOCSET_ROOT = 'ase.docset'
DOCSET_DOCS = Path(f'{DOCSET_ROOT}/Contents/Resources/Documents')

class Docset():

    def __init__(self) -> None:
        self.conn = sqlite3.connect(f'{DOCSET_ROOT}/Contents/Resources/docSet.dsidx')
        self.cur = self.conn.cursor()

        try:
            self.cur.execute('DROP TABLE searchIndex;')
        except:
            pass

        self.cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
        self.cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')
    
    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def insert_index(self, name, type, path):
        self.cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, type, path))

    def find_by_name(self, name) -> list:
        self.cur.execute('SELECT * FROM searchIndex WHERE (name = ?)', (name,))
        return self.cur.fetchall()

    def find_by_path(self, path) -> list:
        self.cur.execute('SELECT * FROM searchIndex WHERE (path = ?)', (path,))
        return self.cur.fetchall()

def get_page_title(soup) -> Optional[str]:
    title = soup.find("title")
    return title.text
    
if __name__ == "__main__":

    docset = Docset()

    # Modules

    with open(DOCSET_DOCS / "py-modindex.html") as fp:
        soup = BeautifulSoup(fp, features="lxml")

    for a in soup.select(".indextable a"):
        name = a.text
        path = a["href"]
        docset.insert_index(name, "Module", path)
    
    # API Index

    with open(DOCSET_DOCS / "genindex.html") as fp:
        soup = BeautifulSoup(fp, features="lxml")

    for a in soup.select(".indextable a"):
        name = a.text
        path = a["href"]

        if name == "module": continue
        if urlparse(path).fragment.startswith("module-"): continue

        res = re.search(r"(.*)\(\) \(in module (\S+)\)", name)
        if res:
            groups = res.groups()
            name = urlparse(path).fragment
            docset.insert_index(name, "Method", path)
            # print(name)
            continue

        res = re.search(r"(.*) \(in module (\S+)\)", name)
        if res:
            groups = res.groups()
            name = urlparse(path).fragment
            docset.insert_index(name, "Variable", path)
            # print(name)
            continue

        res = re.search(r"\(in module (\S+)\)", name)
        if res:
            groups = res.groups()
            name = urlparse(path).fragment
            docset.insert_index(name, "Method", path)
            # print(name)
            continue
    
        res = re.search(r"(.*) \(class in (\S+)\)", name)
        if res:
            groups = res.groups()
            name = urlparse(path).fragment
            docset.insert_index(name, "Class", path)
            # print(name)
            continue

        res = re.search(r"\((\S+) property\)", name)
        if res:
            groups = res.groups()
            name = urlparse(path).fragment
            docset.insert_index(name, "Property", path)
            # print(name)
            continue

        res = re.search(r"\((\S+) class method\)", name)
        if res:
            groups = res.groups()
            name = urlparse(path).fragment
            docset.insert_index(name, "Method", path)
            # print(name)
            continue

        res = re.search(r"\((\S+) method\)", name)
        if res:
            groups = res.groups()
            name = urlparse(path).fragment
            docset.insert_index(name, "Method", path)
            # print(name)
            continue

        res = re.search(r"\((\S+) static method\)", name)
        if res:
            groups = res.groups()
            name = urlparse(path).fragment
            docset.insert_index(name, "Method", path)
            # print(name)
            continue

        res = re.search(r"\((\S+) attribute\)", name)
        if res:
            groups = res.groups()
            name = urlparse(path).fragment
            docset.insert_index(name, "Variable", path)
            # print(name)
            continue
        
        res = re.search(r"^[A-Z_\$]+$", name)
        if res:
            groups = res.groups()
            name = urlparse(path).fragment
            docset.insert_index(name, "Variable", path)
            # print(name)
            continue

        # print(name, path)

    # Source code

    with open(DOCSET_DOCS / "_modules/index.html") as fp:
        soup = BeautifulSoup(fp, features="lxml")
    
    for a in soup.select(".document ul > li > a"):
        name = a.text
        path = a["href"]
        docset.insert_index(name, "File", f"_modules/{path}")
