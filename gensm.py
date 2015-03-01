from build_sourcemap import build_source_map
from modular_build import read_file
import sys

try:
    import simplejson as json
except ImportError:
    import json

if len(sys.argv) < 3:
    raise Exception('Usage: gensm.py source1.txt source2.txt ... generated.txt')

source_files = sys.argv[1:-1]
generated_file = sys.argv[-1]

sources = []
for source_file in source_files:
    sources.append(read_file(source_file))
generated = read_file(generated_file)

print json.dumps(build_source_map(sources, source_files, generated_file, generated))
