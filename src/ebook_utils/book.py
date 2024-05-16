class BookMeta:
    def __init__(self, title: str, subtitle: str, author: str, ean: str) -> None:
        self._meta = {
            'title': title,
            'subtitle': subtitle,
            'author': author,
            'ean': ean
        }

    def __getitem__(self, key):
        return self._meta[key]

class BookChapter:
    def __init__(self, title: str, content: str) -> None:
        self._title = title
        self._content = content

    @property
    def title(self) -> str:
        return self._title

    @property
    def content(self) -> str:
        return self._content

class BookToc:
    def __init__(self, pages: list[BookChapter]) -> None:
        self._pages = pages

    def __getitem__(self, key):
        return self.pages[key]

class Book:
    def __init__(self, toc: BookToc, meta: BookMeta) -> None:
        self._meta = meta
        self._toc = toc

    def export() -> None:
        # aqui debe generar el archivo
        pass
