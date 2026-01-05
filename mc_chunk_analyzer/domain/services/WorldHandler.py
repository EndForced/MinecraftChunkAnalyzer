from pathlib import Path
from typing import List, Union
from numba import njit
import numpy as np


from .ChunkAnalyzer import NBTTagReader, ChunkAnalyzer
from ..models.Chunk import RawChunk, Corners, Dimensions
from .utils import ChunkManager, Profiler


@njit(fastmath=True)
def build_cords(ys: np.ndarray, dim: Dimensions):
    res = np.empty((256, 3), dtype=np.int64)
    height_diff = 65 if dim == "Overworld" else 1
    for z in range(16):
        for x in range(16):
            idx = z * 16 + x
            res[idx, 0] = x
            res[idx, 1] = np.int64(ys[idx] - height_diff)
            res[idx, 2] = z

    return res

#skip first bit because only 63 can be easily divided by 9
@njit(fastmath=True)
def extract_heights(heights_longs: np.ndarray):
    res = np.zeros(256, dtype=np.int64)
    mask = np.int64((1 << 9) - 1)

    for i in range(37):
        current_long = heights_longs[i]
        for j in range(7):
            idx = i * 7 + j
            if idx < 256:
                res[idx] = (current_long >> (j * 9)) & mask
    return res


prof = Profiler()

class GroundProjector:
    def __init__(self, chunks: List[RawChunk]):
        self.min_x = 0
        self.min_z = 0
        self._chunks_arr = self._build_chunk_matrix(chunks)

    def _build_chunk_matrix(self, chunks: List[RawChunk]) -> List[List[Union[RawChunk, None]]]:
        if not chunks:
            return []

        all_x = [chunk.abs_cord.x for chunk in chunks]
        all_z = [chunk.abs_cord.z for chunk in chunks]

        self.min_x, max_x = min(all_x), max(all_x)
        self.min_z, max_z = min(all_z), max(all_z)

        width = max_x - self.min_x + 1
        height = max_z - self.min_z + 1

        # 3. Создаем пустую матрицу [Rows][Cols] -> [Z][X]
        # Мы инициализируем её так, чтобы matrix[z][x] не вызывал IndexError
        matrix = [[None for _ in range(width)] for _ in range(height)]

        # 4. Заполняем матрицу
        for chunk in chunks:
            # Индекс столбца (X)
            x_idx = chunk.abs_cord.x - self.min_x
            # Индекс строки (Z)
            z_idx = chunk.abs_cord.z - self.min_z

            # Кладём чанк в матрицу: сначала Z, потом X
            matrix[z_idx][x_idx] = chunk

        return matrix

    # def project(self) -> List[List[np.ndarray]]:
    #     """
    #     Преобразует чанки в данные о блоках на поверхности.
    #     """
    #     # Инициализируем структуру результата той же размерности, что и матрица чанков
    #     width = len(self._chunks_arr)
    #     height = len(self._chunks_arr[0]) if width > 0 else 0
    #
    #     data_parsed = [[None for _ in range(height)] for _ in range(width)]
    #
    #     for x_idx in range(width):
    #         for z_idx in range(height):
    #             chunk = self._chunks_arr[x_idx][z_idx]
    #
    #             if chunk is None:
    #                 data_parsed[x_idx][z_idx] = np.zeros((16, 16), dtype=int)
    #                 continue
    #
    #             try:
    #                 reader = NBTTagReader(chunk.raw_data)
    #                 chunk_nbt = reader.read().value
    #                 level_data = chunk_nbt.get("Level", chunk_nbt)
    #                 heightmaps = level_data.get("Heightmaps", {})
    #                 heights_raw = heightmaps.get("WORLD_SURFACE")
    #
    #                 if heights_raw is None:
    #                     continue
    #
    #                 heights = extract_heights(np.array(heights_raw))
    #                 sections = level_data.get("sections", [])
    #                 if not sections:
    #                     continue
    #                 parser = ChunkAnalyzer(sections)
    #                 cords = build_cords(heights, chunk.dimension)
    #
    #                 blocks = parser.bulk_get_blocks(cords)
    #                 data_parsed[x_idx][z_idx] = blocks
    #
    #
    #             except Exception as e:
    #                 data_parsed[x_idx][z_idx] = None

        return data_parsed

    def project(self):
        width = len(self._chunks_arr)
        height = len(self._chunks_arr[0]) if width > 0 else 0
        data_parsed = [[None for _ in range(height)] for _ in range(width)]

        for x_idx in range(width):
            for z_idx in range(height):
                chunk = self._chunks_arr[x_idx][z_idx]
                if chunk is None: continue

                try:
                    # 1. Замеряем чтение NBT (самое тяжелое место обычно тут)
                    with prof("NBT Reading"):
                        reader = NBTTagReader(chunk.raw_data)
                        chunk_nbt = reader.read().value
                        level_data = chunk_nbt.get("Level", chunk_nbt)

                    # 2. Замеряем распаковку высот
                    with prof("Heightmaps Extract"):
                        heights_raw = level_data.get("Heightmaps", {}).get("WORLD_SURFACE")
                        if heights_raw is None: continue
                        heights = extract_heights(np.array(heights_raw))
                        cords = build_cords(heights)

                    # 3. Замеряем поиск блоков в секциях
                    with prof("Chunk Analysis"):
                        sections = level_data.get("sections", [])
                        parser = ChunkAnalyzer(sections)
                        blocks = parser.bulk_get_blocks(cords)
                        data_parsed[x_idx][z_idx] = blocks

                except Exception as e:
                    print(f"Error at {chunk.abs_cord}: {e}")

        # Печатаем результат в конце работы
        prof.report()
        return data_parsed


cm = ChunkManager(Path(r"C:\Users\Taras\AppData\Roaming\PrismLauncher\instances\Quantum Tech\minecraft\.bobby\Andrey2006.go.ro_25565\1892924735912129312\minecraft\the_nether"), "Nether")
corners = Corners(-100,20,0,60)
c = cm.get_chunks(corners)
gp = GroundProjector(c)
a = gp.project()
