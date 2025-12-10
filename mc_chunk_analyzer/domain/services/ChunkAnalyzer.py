from ..models.Chunk import RawChunk
from ..models.NBT import NBTTag
from ..models.Region import RawRegion, Region, TwoDimCord
from ..models.NBTInfo import *
from ..ports.IChunkAnalyzer import IMcaParser
from ..ports.INBTReader import INBTTagReader
from typing import Union, List
import numpy as np
import gzip
import zlib
import struct

class McaParser(IMcaParser):
    @staticmethod
    def __parse_location_table(raw_bytes: bytes) -> np.ndarray:
        table = np.frombuffer(raw_bytes[:4096], dtype=">u4")
        entries = np.zeros(1024, dtype=[
            ('offset', np.uint32),
            ('count', np.uint16),
        ])
        entries["offset"] = table >> 8
        entries["count"] = table & 0xFF
        return entries

    def parse(self, region: RawRegion) -> Region:
        data = region.data
        cord = region.cord
        entries = self.__parse_location_table(data)
        raw_chunks = {}

        for i in range(1024):
            offset = entries[i]["offset"]
            count  = entries[i]["count"]
            chunk_x = cord.x * 32 + (i % 32)
            chunk_z = cord.z * 32 + (i // 32)
            chunk_cord = TwoDimCord((chunk_x, chunk_z))
            if offset == 0 or count == 0:
                raw_chunks[chunk_cord] = RawChunk(chunk_cord, None, region.dimension)
                continue
            byte_start = offset * 4096
            byte_end   = byte_start + count * 4096
            chunk_bytes = data[byte_start:byte_end]
            length = int.from_bytes(chunk_bytes[:4], "big")
            compression_type = chunk_bytes[4]
            compressed = chunk_bytes[5:5 + length - 1]

            if compression_type == 1:
                decompressed = gzip.decompress(compressed)
            elif compression_type == 2:
                decompressed = zlib.decompress(compressed)
            else:
                decompressed = compressed
            raw_chunks[chunk_cord] = RawChunk(chunk_cord, decompressed, region.dimension)

        return Region(
            readable=True,
            cord=cord,
            raw_chunks=raw_chunks,
            dimension=region.dimension
        )

# ---------- Kinda fast nbt reading tbh ----------
class NBTTagReader(INBTTagReader):
    def __init__(self, data: bytes):
        super().__init__()
        self._tag_spec_cache = [get_tag_spec_by_id(i) for i in range(13)]
        self._tag_length_cache = [self._tag_spec_cache[i].tag_id for i in range(13)]
        self.current_byte = 0
        self.data = data
        self.mv = memoryview(self.data)
        self._read_func = {
            7: lambda: self._read_with_length_field(self._tag_spec_cache[7]),
            8: lambda: self._read_with_length_field(self._tag_spec_cache[8]),
            11: lambda: self._read_with_length_field(self._tag_spec_cache[11]),
            12: lambda: self._read_with_length_field(self._tag_spec_cache[12])
        }
        self._fixed_read_map = {
            1: self._read_int8,
            2: self._read_int16,
            3: self._read_int32,
            4: self._read_int64,
            5: self._read_float,
            6: self._read_double,
        }

    def _read_uint8(self) -> int:
        v = self.mv[self.current_byte]
        self.current_byte += 1
        return v

    def _read_int8(self) -> int:
        v = int.from_bytes(self.mv[self.current_byte:self.current_byte+1], 'big', signed=True)
        self.current_byte += 1
        return v

    def _read_int16(self) -> int:
        v = int.from_bytes(self.mv[self.current_byte:self.current_byte+2], 'big', signed=True)
        self.current_byte += 2
        return v

    def _read_uint16(self) -> int:
        v = int.from_bytes(self.mv[self.current_byte:self.current_byte+2], 'big', signed=False)
        self.current_byte += 2
        return v

    def _read_int32(self) -> int:
        v = int.from_bytes(self.mv[self.current_byte:self.current_byte+4], 'big', signed=True)
        self.current_byte += 4
        return v

    def _read_int64(self) -> int:
        v = int.from_bytes(self.mv[self.current_byte:self.current_byte+8], 'big', signed=True)
        self.current_byte += 8
        return v

    def _read_float(self) -> float:
        v = struct.unpack_from(">f", self.mv, self.current_byte)[0]
        self.current_byte += 4
        return v

    def _read_double(self) -> float:
        v = struct.unpack_from(">d", self.mv, self.current_byte)[0]
        self.current_byte += 8
        return v

    def _read_bytes(self, n: int) -> bytes:
        b = self.mv[self.current_byte:self.current_byte + n].tobytes()
        self.current_byte += n
        return b

    def _peek_uint8(self) -> int:
        return self.mv[self.current_byte]

    def get_next_type(self, impl: bool = False) -> NBTTagSpec:
        tag_id = self._read_uint8()
        return self._tag_spec_cache[tag_id]

    def get_next_name(self) -> str:
        start = self.current_byte
        _ = self._read_uint8()
        name_len = self._read_uint16()
        name = self._read_bytes(name_len).decode("utf-8") if name_len > 0 else ""
        self.current_byte = start
        return name

    def _get_next_name(self) -> str:
        name_len = self._read_uint16()
        if name_len == 0:
            return ""
        return self._read_bytes(name_len).decode("utf-8")

    def read(self) -> NBTTag:
        tag = self.get_next_type(True)
        name = self._get_next_name()
        payload = None

        if tag.fixed_size:
            payload = self._read_base(tag)
        elif tag.tag_id in [7, 8, 11, 12]:
            payload = self._read_with_length_field(tag)
        elif tag.tag_id == 9:  # list
            payload = self._read_list()
        elif tag.tag_id == 10:
            payload = self._read_compound()

        return NBTTag(name=name, value=payload)

    def _read_list(self) -> List:
        tags_type = self._read_uint8()
        size = self._read_int32()
        if size == 0:
            return []

        if tags_type in [1, 2, 3, 4, 5, 6]:
            read_func = self._read_base
        elif tags_type in [7, 8, 11, 12]:
            read_func = self._read_func[tags_type]
        elif tags_type == 10:
            read_func = self._read_compound
        elif tags_type == 9:
            read_func = self._read_list
        else:
            raise ValueError(f"Strange tag id bro {tags_type}")

        if tags_type in (3, 4):
            if tags_type == 3:
                nbytes = 4 * size
                arr = np.frombuffer(self.mv[self.current_byte:self.current_byte + nbytes], dtype='>i4')
                self.current_byte += nbytes
                return arr.tolist()
            else:
                nbytes = 8 * size
                arr = np.frombuffer(self.mv[self.current_byte:self.current_byte + nbytes], dtype='>i8')
                self.current_byte += nbytes
                return arr.tolist()

        out = []
        for _ in range(size):
            out.append(read_func())
        return out

    def _read_compound(self):
        payload_out = {}
        while True:
            tag = self.get_next_type(True)
            if tag.tag_id == 0:
                return payload_out
            name = self._get_next_name()
            if tag.fixed_size:
                payload = self._read_base(tag)
            elif tag.tag_id in [7, 8, 11, 12]:
                payload = self._read_with_length_field(tag)
            elif tag.tag_id == 9:
                payload = self._read_list()
            elif tag.tag_id == 10:
                payload = self._read_compound()
            else:
                payload = None
            payload_out[name] = payload

    def _read_base(self, tag_spec: NBTTagSpec):
        read_fn = self._fixed_read_map.get(tag_spec.tag_id)
        if read_fn is None:
            raise ValueError(f"Strange tag id bro {tag_spec.tag_id}")
        return read_fn()

    def _read_length_str(self, n, impl: bool = False):
        if impl:
            return self._read_bytes(n).decode("utf-8") if n > 0 else ""
        else:
            return self.mv[self.current_byte:self.current_byte + n].tobytes().decode("utf-8") if n > 0 else ""

    def _read_with_length_field(self, tag: NBTTagSpec) -> Union[List[int], str]:
        if tag.tag_id == 7:  # byte array -> return list of signed bytes (like original)
            size = self._read_int32()
            if size == 0:
                return []
            arr = np.frombuffer(self.mv[self.current_byte:self.current_byte + size], dtype='>i1')
            self.current_byte += size
            return arr.tolist()

        elif tag.tag_id == 8:  # string
            size = self._read_int16()
            if size == 0:
                return ""
            b = self._read_bytes(size)
            return b.decode("utf-8")

        elif tag.tag_id == 11:  # int array
            size = self._read_int32()
            if size == 0:
                return []
            nbytes = size * 4
            arr = np.frombuffer(self.mv[self.current_byte:self.current_byte + nbytes], dtype='>i4')
            self.current_byte += nbytes
            return arr.tolist()

        elif tag.tag_id == 12:
            size = self._read_int32()
            if size == 0:
                return []
            nbytes = size * 8
            arr = np.frombuffer(self.mv[self.current_byte:self.current_byte + nbytes], dtype='>i8')
            self.current_byte += nbytes
            return arr.tolist()

        else:
            raise ValueError(f"Unsupported with-length tag: {tag.tag_id}")
