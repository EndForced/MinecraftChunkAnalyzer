import time
from io import BytesIO
import  nbtlib as nb
import numpy as np
import zlib
import gzip
from typing import Union
from pathlib import Path
from ChunkAnalyzer import FastChunkAnalyzer

class FastMca:
    def __init__(self, region_path: Union[Path,str] ) -> None:
        self.__data = np.fromfile(region_path, dtype=">i4")
        self.__entries = self.__parse_location_entries(self.__data)

    @staticmethod
    def __parse_location_entries(data):
        dtype = [('offset', np.uint32), ('total_sectors', np.uint32), ('sectors_count', np.uint16)]
        entries = np.empty(1024, dtype=dtype)
        total_sectors = 2
        for i in range(1024):
            value = data[i]
            entries[i]['offset'] = value >> 8
            entries[i]['sectors_count'] = value & 0xFF
            total_sectors += (value & 0xFF)
            entries[i]['total_sectors'] = total_sectors
        return entries

    def __get_chunk_raw(self,chunk_cords: tuple[int,int]):
        chunk_index = chunk_cords[0]*32 + chunk_cords[1]
        entry_point = self.__entries[chunk_index]
        start_byte = (entry_point['total_sectors'] * 4096 - entry_point['sectors_count'] * 4096) // 4
        end_byte = (entry_point['total_sectors'] * 4096) // 4
        nbt = self.__data[start_byte:end_byte]
        if len(nbt) == 0: return None
        compression_type = (nbt[1] >> 24) & 0xFF
        words_count = (nbt[0] + 3) // 4
        compressed_chunk = nbt[1:1+words_count].tobytes()[1:]

        if compression_type == 1:
            return nb.File.parse(BytesIO(gzip.decompress(compressed_chunk)))
        elif compression_type == 2:
            return  nb.File.parse(BytesIO(zlib.decompress(compressed_chunk)))
        elif compression_type == 3:
            return  nb.File.parse(BytesIO(compressed_chunk))
        else:
            raise ValueError("Unknown chunk compression type")

    def get_chunk(self, cords: tuple[int,int]):
        raw_chunk = self.__get_chunk_raw(cords)
        sections = raw_chunk.get('sections')
        return  FastChunkAnalyzer(sections)


if __name__ == "__main__":
    fm = FastMca('minecraft/overworld/3/r.0.0.mca')
    a = fm.get_chunk((1,1))
    print(a.look_for_block('minecraft:bedrock'))

