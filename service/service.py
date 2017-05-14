import re
import logging
import sys

from flask import Flask, request, jsonify
from flask_caching import Cache
from whoosh.qparser import QueryParser, OrGroup
from index import load_index

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
parser = None
searcher = None


@app.route("/conditions", methods=["GET"])
@cache.cached(key_prefix=lambda: request.full_path, timeout=0)
def conditions():
    query = " ".join(re.findall("\w+", request.args.get("query", "")))
    query = parser.parse(query)
    app.logger.info("Search Query: {}".format(query))

    results = searcher.search(query)
    output = []
    for result in results:
        output.append({"title": result["title"],
                       "url": result["url"],
                       "score": result.score})
    return jsonify(output)


@app.before_first_request
def before_first_request():
    global parser, searcher
    index = load_index()
    og = OrGroup.factory(0.9)
    parser = QueryParser("text", schema=index.schema, group=og)
    searcher = index.searcher()

    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.INFO)
