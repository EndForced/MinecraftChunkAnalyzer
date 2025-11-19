from anvil import Chunk, Region, Block, Biome
from typing import Dict, List, Tuple, Union
from pathlib import Path
from io import BytesIO
import pathlib
import os

class MyChunk:
    def __init__(self, chunk, dimension: str):
        self.chunk = chunk
        self.maxHeight = 318 if dimension == "overworld" else 256
        self.minHeight = -64 if dimension == "overworld" else 0

    def exists(self):
        return self.chunk is not None

    def blocks(self) -> Dict[str, int]:
        """Return count of all blocks inside the chunk."""
        data = {}
        for x in range(16):
            for y in range(self.minHeight, self.maxHeight):
                for z in range(16):
                    block_id = self.chunk.get_block(x, y, z).id
                    data[block_id] = data.get(block_id, 0) + 1
        return data

    def look_for_blocks(self, block_ids: Union[str, List[str]]) -> Dict[str, List[Tuple[int, int, int]]]:
        """Returns dict[block_id] = list of positions where found."""
        if not self.exists():
            return {}

        if isinstance(block_ids, str):
            block_ids = [block_ids]

        result = {bid: [] for bid in block_ids}

        for x in range(16):
            for y in range(self.minHeight, self.maxHeight):
                for z in range(16):
                    block = self.chunk.get_block(x, y, z)
                    if block.id in result:
                        result[block.id].append((x, y, z))

        return {k: v for k, v in result.items() if v}

class ChunkManager:
    def __init__(self, path: str):
        """
        Path = path to Minecraft folder used by Bobby.
        """
        self.path = Path(path)
        self.chunks = {}


    def from_corners_to_chunks(self, p1: tuple[int,int],p2: tuple[int,int]) -> list:
        lenght_chunks = abs(p1[0]-p2[0]) // 16 + 2
        width_chunks = abs(p1[1]-p2[1]) // 16 + 2

        lenght_start = (min(p1[0],p2[0]) // 16) - 1
        width_start = (min(p1[1], p2[1]) // 16) - 1

        res = []
        for x in range(lenght_start, lenght_start + lenght_chunks):
            for y in range(width_start, width_start + width_chunks):
                res.append((x,y))

        return res


    def load_by_list(self, chunks_list: List[Tuple[int, int]], dimension: str):
        dim_path = Path(self.path, dimension)

        # --- helpers ---
        def chunk_to_region(chunk_x: int, chunk_z: int):
            return chunk_x // 32, chunk_z // 32

        def load_file(path: Union[pathlib.Path, str]) -> Union[bytes, None]:
            path = Path(path)
            if not path.parent.exists():
                return None
            if path.name in os.listdir(path.parent):
                with open(path, "rb") as f:
                    return f.read()
            return None

        def search_for_file(filename: str, start: pathlib.Path) -> Union[bytes, None]:
            """Recursive file search inside dimension folder."""
            for entry in os.scandir(start):
                if entry.is_file() and entry.name == filename:
                    return load_file(entry.path)
                if entry.is_dir():
                    result = search_for_file(filename, entry.path)
                    if result is not None:
                        return result
            return None

        # --- gather region files required ---
        region_set = {chunk_to_region(x, z) for x, z in chunks_list}
        region_file_data = {}

        for rx, rz in region_set:
            filename = f"r.{rx}.{rz}.mca"
            file_bytes = search_for_file(filename, dim_path)
            if file_bytes:
                region_file_data[(rx, rz)] = BytesIO(file_bytes)

        loaded = {}

        for (rx, rz), file_obj in region_file_data.items():
            region = Region.from_file(file_obj)

            for cx, cz in chunks_list:
                if chunk_to_region(cx, cz) != (rx, rz):
                    continue

                local_x = cx % 32
                local_z = cz % 32

                try:
                    chunk = region.get_chunk(local_x, local_z)
                except:
                    continue

                if chunk:
                    loaded[(cx, cz)] = chunk

        self.chunks.update({
            coords: MyChunk(chunk, dimension)
            for coords, chunk in loaded.items()
        })




if __name__ == "__main__":
    cm = ChunkManager(r"C:\Users\DNS\PycharmProjects\BedrockPatternFinder\minecraft")
    # cm.load_by_list([(-50,50), (0,0)], "overworld")
    # print(cm.chunks[(0,0)].look_for_blocks("deepslate"))
    print(len(cm.from_corners_to_chunks((0,0),(256,256))))

