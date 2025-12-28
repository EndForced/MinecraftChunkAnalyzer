#---------Raw NBT parsing--------------#


from ..models.Chunk import RawChunk
from ..models.NBT import NBTTag
from ..models.Region import RawRegion, Region, TwoDimCord
from ..models.NBTInfo import *
from ..ports.IChunkAnalyzer import IMcaParser, IChunkAnalyzer
from ..ports.INBTReader import INBTTagReader
from typing import Union, List
import numpy as np
import gzip
import zlib
import struct
from numba import jit


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

        self._cache_skip_functions = {
            1: self._skip_byte,
            2: self._skip_int16,
            3: self._skip_int32,
            4: self._skip_int64,
            5: self._skip_int32,
            6: self._skip_int64,
            7: self._skip_bytearray,
            8: self._skip_string,
            9: self._skip_list,
            10: self._skip_compound,
            11: self._skip_intarray,
            12: self._skip_long_array
        }

        self._name_cache = {}
        self._return_bytes_for_arrays = True

        self._size_map = {
            1: 1,  # Byte
            2: 2,  # Short
            3: 4,  # Int
            4: 8,  # Long
            5: 4,  # Float
            6: 8,  # Double
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

    def get_next_type_fast(self, impl: bool = False) -> int:
        return self._read_uint8()

    def get_next_name(self) -> str:
        start = self.current_byte
        _ = self._read_uint8()
        name_len = self._read_uint16()
        name = self._read_bytes(name_len).decode("utf-8") if name_len > 0 else ""
        self.current_byte = start
        return name

    def _get_next_name(self) -> str:
        pos = self.current_byte
        data = self.data
        name_len = (data[pos] << 8) | data[pos + 1]
        pos += 2
        if name_len == 0:
            self.current_byte = pos
            return ""
        name_bytes = data[pos:pos + name_len]
        pos += name_len

        self.current_byte = pos
        try:
            return name_bytes.decode('ascii')
        except UnicodeDecodeError:
            return name_bytes.decode('utf-8')

    def read(self) -> NBTTag:
        tag = self.get_next_type(True).tag_id
        name = self._get_next_name()
        payload = None

        if tag in [1,2,3,4,5,6]:
            payload = self._read_base(self._tag_spec_cache[tag])
        elif tag in [7, 8, 11, 12]:
            payload = self._read_with_length_field(self._tag_spec_cache[tag])
        elif tag == 9:  # list
            payload = self._read_list()
        elif tag == 10:
            payload = self._read_compound()

        return NBTTag(name=name, value=payload)

    def parse_through_tree(self, route: List) -> Union[NBTTag, None]:
        self.get_next_type(True)
        length = self._read_int16()
        self.current_byte += length

        while route:
            type_tag = self.get_next_type(True).tag_id
            self.current_byte -= 1
            name = self.get_next_name()
            if type_tag == 0:
                return None
            if name != route[0]:
                self.current_byte += 1
                length = self._read_int16()
                self.current_byte += length
                self._cache_skip_functions[type_tag]()
            elif name == route[0]:
                return self.read()


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

        return [read_func() for _ in range(size)]

    def _read_compound(self): #I hate my life
        payload_out = {}
        data = self.data
        pos = self.current_byte

        while True:
            tag_id = data[pos]
            pos += 1

            if tag_id == 0:  # TAG_End
                self.current_byte = pos
                return payload_out

            name_len = (data[pos] << 8) | data[pos + 1]
            pos += 2

            if name_len:
                name_bytes = data[pos:pos + name_len]
                pos += name_len

                name = self._name_cache.get(name_bytes)
                if name is None:
                    try:
                        name = name_bytes.decode('ascii')
                    except UnicodeDecodeError:
                        name = name_bytes.decode('utf-8')

                    if name_len <= 32:
                        self._name_cache[name_bytes] = name
            else:
                name = ""

            if tag_id == 1:  # Byte
                payload = data[pos]
                pos += 1
            elif tag_id == 2:  # Short
                payload = (data[pos] << 8) | data[pos + 1]
                pos += 2
            elif tag_id == 3:  # Int
                payload = ((data[pos] << 24) | (data[pos + 1] << 16) |
                           (data[pos + 2] << 8) | data[pos + 3])
                pos += 4
            elif tag_id == 4:  # Long
                payload = ((data[pos] << 56) | (data[pos + 1] << 48) |
                           (data[pos + 2] << 40) | (data[pos + 3] << 32) |
                           (data[pos + 4] << 24) | (data[pos + 5] << 16) |
                           (data[pos + 6] << 8) | data[pos + 7])
                pos += 8
            elif tag_id == 5:  # Float
                payload = struct.unpack_from(">f", data, pos)[0]
                pos += 4
            elif tag_id == 6:  # Double
                payload = struct.unpack_from(">d", data, pos)[0]
                pos += 8

            elif tag_id == 7:  # Byte array
                size = ((data[pos] << 24) | (data[pos + 1] << 16) |
                        (data[pos + 2] << 8) | data[pos + 3])
                pos += 4
                if size:
                    if self._return_bytes_for_arrays:
                        payload = data[pos:pos + size]
                    else:
                        payload = list(data[pos:pos + size])
                    pos += size
                else:
                    payload = [] if not self._return_bytes_for_arrays else b''

            elif tag_id == 8:  # String
                str_len = (data[pos] << 8) | data[pos + 1]
                pos += 2
                if str_len:
                    str_bytes = data[pos:pos + str_len]
                    pos += str_len
                    try:
                        payload = str_bytes.decode('ascii')
                    except UnicodeDecodeError:
                        payload = str_bytes.decode('utf-8')
                else:
                    payload = ""

            elif tag_id == 9:  # List
                list_result, new_pos = self._read_list_at_pos(data, pos)
                payload = list_result
                pos = new_pos

            elif tag_id == 10:  # Compound (рекурсия)
                self.current_byte = pos
                payload = self._read_compound()
                pos = self.current_byte

            elif tag_id == 11:  # Int array
                size = ((data[pos] << 24) | (data[pos + 1] << 16) |
                        (data[pos + 2] << 8) | data[pos + 3])
                pos += 4
                if size:
                    arr = memoryview(data)[pos:pos + size * 4]
                    if size > 16:
                        payload = np.frombuffer(arr, dtype='>i4').tolist()
                    else:
                        payload = list(struct.unpack_from(f">{size}i", data, pos))
                    pos += size * 4
                else:
                    payload = []

            elif tag_id == 12:  # Long array
                size = ((data[pos] << 24) | (data[pos + 1] << 16) |
                        (data[pos + 2] << 8) | data[pos + 3])
                pos += 4
                if size:
                    arr = memoryview(data)[pos:pos + size * 8]
                    if size > 8:
                        payload = np.frombuffer(arr, dtype='>i8').tolist()
                    else:
                        payload = list(struct.unpack_from(f">{size}q", data, pos))
                    pos += size * 8
                else:
                    payload = []

            payload_out[name] = payload

        self.current_byte = pos
        return payload_out

    def _read_list_at_pos(self, data: bytes, start_pos: int):
        pos = start_pos
        list_type = data[pos]
        pos += 1
        size = ((data[pos] << 24) | (data[pos + 1] << 16) |
                (data[pos + 2] << 8) | data[pos + 3])
        pos += 4

        if size == 0:
            return [], pos

        result = []
        if list_type in (1, 2, 3, 4, 5, 6):
            elem_size = self._size_map[list_type]
            for _ in range(size):
                if list_type == 1:  # Byte
                    result.append(data[pos])
                elif list_type == 2:  # Short
                    result.append((data[pos] << 8) | data[pos + 1])
                elif list_type == 3:  # Int
                    result.append(((data[pos] << 24) | (data[pos + 1] << 16) |
                                   (data[pos + 2] << 8) | data[pos + 3]))
                elif list_type == 5:  # Float
                    result.append(struct.unpack_from(">f", data, pos)[0])
                elif list_type == 6:  # Double
                    result.append(struct.unpack_from(">d", data, pos)[0])
                pos += elem_size

        elif list_type == 7:
            for _ in range(size):
                arr_size = ((data[pos] << 24) | (data[pos + 1] << 16) |
                            (data[pos + 2] << 8) | data[pos + 3])
                pos += 4
                if arr_size:
                    result.append(list(data[pos:pos + arr_size]))
                    pos += arr_size
                else:
                    result.append([])

        elif list_type == 8:
            for _ in range(size):
                str_len = (data[pos] << 8) | data[pos + 1]
                pos += 2
                if str_len:
                    try:
                        result.append(data[pos:pos + str_len].decode('ascii'))
                    except:
                        result.append(data[pos:pos + str_len].decode('utf-8'))
                    pos += str_len
                else:
                    result.append("")

        elif list_type == 10:
            for _ in range(size):
                old_pos = self.current_byte
                self.current_byte = pos
                result.append(self._read_compound())
                pos = self.current_byte
                self.current_byte = old_pos

        else:
            for _ in range(size):
                old_pos = self.current_byte
                self.current_byte = pos
                tag = self.read()
                result.append(tag.value)
                pos = self.current_byte
                self.current_byte = old_pos

        return result, pos

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
        if tag.tag_id == 7:  # byte array
            size = self._read_int32()
            if size == 0:
                return []
            arr = struct.unpack_from(f">{size}b", self.data, self.current_byte)
            self.current_byte += size
            return list(arr)

        elif tag.tag_id == 8:  # string
            size = self._read_int16()
            if size == 0:
                return ""
            s = self.data[self.current_byte:self.current_byte + size].decode("utf-8")
            self.current_byte += size
            return s

        elif tag.tag_id == 11:  # int array
            size = self._read_int32()
            if size == 0:
                return []
            arr = struct.unpack_from(f">{size}i", self.data, self.current_byte)
            self.current_byte += size * 4
            return list(arr)

        elif tag.tag_id == 12:  # long array
            size = self._read_int32()
            if size == 0:
                return []
            arr = struct.unpack_from(f">{size}q", self.data, self.current_byte)
            self.current_byte += size * 8
            return list(arr)

    def _skip_byte(self):
        self.current_byte += 1

    def _skip_int16(self):
        self.current_byte += 2

    def _skip_int32(self):
        self.current_byte += 4

    def _skip_int64(self):
        self.current_byte += 8

    def _skip_bytearray(self):
        size = self._read_int32()
        self.current_byte += size

    def _skip_string(self):
        size =  self._read_int16()
        self.current_byte += size

    def _skip_intarray(self):
        size = self._read_int32() * 4
        self.current_byte += size

    def _skip_long_array(self):
        size = self._read_int32() * 8
        self.current_byte += size

    def _skip_list(self):
        tags_type = self._read_uint8()
        size = self._read_int32()

        for _ in range(size):
            self._cache_skip_functions[tags_type]()

    def _skip_compound(self):
        while True:
            tag_type = self.get_next_type_fast(True)
            if tag_type == 0:
                return
            length = self._read_int16()
            self.current_byte += length
            self._cache_skip_functions[tag_type]()

@jit(nopython=True)
def extract_block_id_fast(block_data, block_index, bits_per_block, palette_size):
    blocks_per_long = 64 // bits_per_block
    long_index = block_index // blocks_per_long
    bit_offset = (block_index % blocks_per_long) * bits_per_block

    if long_index < len(block_data):
        block_id = (block_data[long_index] >> bit_offset) & ((1 << bits_per_block) - 1)
        return block_id if block_id < palette_size else 0
    return 0

class ChunkAnalyzer(IChunkAnalyzer):
    def __init__(self, sections):
        self.sections = sections
        self._build_lookup()
        if not sections:
            self.exist = False

    def _build_lookup(self):
        self.section_data = []

        for section in self.sections:
            y_level = section.get('Y', -100)
            block_states = section.get('block_states', {})
            palette = block_states.get('palette', [])
            block_data = block_states.get('data', [])

            palette_names = [block.get('Name', 'minecraft:air') for block in palette]
            block_data_np = np.array(block_data, dtype=np.int64) if block_data else np.array([], dtype=np.int64)

            self.section_data.append({
                'y': y_level,
                'palette': palette_names,
                'block_data': block_data_np,
                'bits_per_block': max(4, (len(palette) - 1).bit_length()) if palette else 4,
                'is_single_block': len(palette) == 1
            })

    def look_for_block(self, block_name):
        return any(
            block_name in section['palette']
            for section in self.section_data
        )

    def get_block(self, x, y, z):
        section_y = y // 16
        local_y = y % 16
        block_index = local_y * 256 + z * 16 + x

        for section in self.section_data:
            if section['y'] == section_y:
                palette = section['palette']

                if not palette:
                    return "minecraft:air"

                if section['is_single_block']:
                    return palette[0]

                if len(section['block_data']) > 0:
                    block_id = extract_block_id_fast(
                        section['block_data'],
                        block_index,
                        section['bits_per_block'],
                        len(palette)
                    )
                    return palette[block_id] if block_id < len(palette) else "minecraft:air"

        return "minecraft:air"

    def get_palette(self):
        all_blocks = set()
        for section in self.section_data:
            all_blocks.update(section['palette'])
        return list(all_blocks)

    def bulk_get_blocks(self, coordinates):
        results = []
        for x, y, z in coordinates:
            results.append(self.get_block(x, y, z))
        return results

    def find_blocks_in_area(self, block_name, min_y=0, max_y=255):
        locations = []

        for section in self.section_data:
            if not (min_y <= section['y'] * 16 <= max_y):
                continue

            if block_name not in section['palette']:
                continue

            if section['is_single_block'] and section['palette'][0] == block_name:
                for y in range(16):
                    for z in range(16):
                        for x in range(16):
                            world_y = section['y'] * 16 + y
                            if min_y <= world_y <= max_y:
                                locations.append((x, world_y, z))
                continue

            palette_index = section['palette'].index(block_name)
            bits_per_block = section['bits_per_block']
            blocks_per_long = 64 // bits_per_block

            for long_index, long_val in enumerate(section['block_data']):
                for block_in_long in range(blocks_per_long):
                    bit_offset = block_in_long * bits_per_block
                    block_id = (long_val >> bit_offset) & ((1 << bits_per_block) - 1)

                    if block_id == palette_index:
                        block_index = long_index * blocks_per_long + block_in_long
                        if block_index < 4096:
                            y_local = block_index // 256
                            remainder = block_index % 256
                            z_local = remainder // 16
                            x_local = remainder % 16

                            world_y = section['y'] * 16 + y_local
                            if min_y <= world_y <= max_y:
                                locations.append((x_local, world_y, z_local))

        return locations










