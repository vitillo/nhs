import json
import os
import settings

from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir


def _load_conditions(path):
    with open(path) as f:
        return json.load(f)


def create_index(index_path=settings.INDEX_PATH, conditions_path=settings.CACHE_PATH):
    os.makedirs(index_path)
    schema = Schema(title=TEXT(stored=True), text=TEXT, url=ID(stored=True))
    index = create_in(index_path, schema)

    writer = index.writer()
    conditions = _load_conditions(conditions_path)
    seen = set()
    for condition in conditions:
        if condition["url"] not in seen:
            writer.add_document(**condition)
            seen.add(condition["url"].lower())
    writer.commit()


def load_index(index_path=settings.INDEX_PATH):
    return open_dir(index_path)


if __name__ == "__main__":
    create_index()
