# from mc_chunk_analyzer.benchmark_mca_unpack import reader
from mc_chunk_analyzer.domain.services.ChunkAnalyzer import McaParser,NBTTagReader
from mc_chunk_analyzer.domain.models.Region import RawRegion, TwoDimCord
from pathlib import Path
from typing import Literal
parser = McaParser()
# reader = NBTReader()
p = Path(r'C:\Users\DNS\PycharmProjects\BedrockPatternFinder\minecraft\overworld\3\r.0.0.mca')
with open(p, "rb") as f:
    data = f.read()
    r = RawRegion(data, TwoDimCord((0,0)), "Nether")
    # print(parser.parse(r))

data = parser.parse(r)
cord = TwoDimCord((1,0))
chunk = data.raw_chunks[cord]
# print(reader.parse_chunk(data.raw_chunks[cord]))
nr = NBTTagReader(chunk.raw_data)
print(nr.read())
