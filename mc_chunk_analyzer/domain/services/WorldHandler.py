from pathlib import Path
from typing import List
from numba import njit
import numpy as np
from numba.np.arrayobj import np_array
import  math


from .ChunkAnalyzer import NBTTagReader, ChunkAnalyzer
from ..models.Chunk import RawChunk, Corners
from .utils import ChunkManager

def build_cords(ys: np.ndarray):
    res = []
    for z in range(16):
        for x in range(16):
            res.append((x, int(ys[z * 16 + x] - 64), z))
    return res


#skip first bit because only 63 can be easily divided by 9
@njit(fastmath = True)
def extract_heights(heights:List[np.int64]):
    cords = []
    for num in heights:
        for j in range(8):
            a = ( num >> 64 - (1 + 9 * j )) & 0b111111111
            if a == 0: continue
            cords.append(a)
    return cords


class GroundProjector:
    def __init__(self, chunks: List[RawChunk]):
        """
        Создаёт двумерную матрицу чанков по координатам chunk.abs_cord
        """
        self._chunks_arr: List[List[RawChunk]] = self._build_chunk_matrix(chunks)

    def _build_chunk_matrix(self, chunks: List[RawChunk]) -> List[List[RawChunk]]:
        """
        Строит 2D матрицу [row][col] из списка чанков, используя chunk.abs_cord
        """
        if not chunks:
            return []

        # находим минимальные координаты, чтобы сдвинуть матрицу к (0,0)
        min_x = min(chunk.abs_cord.x for chunk in chunks)
        max_x = max(chunk.abs_cord.x for chunk in chunks)

        min_z = min(chunk.abs_cord.z for chunk in chunks)
        max_z = max(chunk.abs_cord.z for chunk in chunks)

        width = max_x - min_x + 1
        height = max_z - min_z + 1

        # создаём пустую матрицу нужного размера
        matrix: List[List[RawChunk | None]] = [
            [None for _ in range(width)] for _ in range(height)
        ]

        # заполняем матрицу чанками
        for chunk in chunks:
            x_idx = chunk.abs_cord.x - min_x
            z_idx = chunk.abs_cord.z - min_z
            matrix[z_idx][x_idx] = chunk

        return matrix

    def project(self) -> List[List[np.ndarray]]:
        """
        Преобразует каждый чанк в высоты и возвращает 2D массив высот
        """
        data_parsed: List[List[np.ndarray]] = [
            [] for _ in range(len(self._chunks_arr))
        ]

        for row_idx, chunk_row in enumerate(self._chunks_arr):
            for chunk in chunk_row:
                if chunk is None:
                    # если чанк отсутствует, заполняем нулями
                    heights = np.zeros((16, 16), dtype=int)  # размер чанка 16x16 блоков
                    blocks = []
                else:
                    heights_raw = (
                        NBTTagReader(chunk.raw_data)
                        .parse_through_tree(["Heightmaps", "WORLD_SURFACE"])
                        .value["WORLD_SURFACE"]
                    )
                    heights = extract_heights(np.array(heights_raw))

                    blocks_raw = (
                        NBTTagReader(chunk.raw_data)
                        .read().value["sections"]
                    )
                    parser = ChunkAnalyzer(blocks_raw)
                    cords = build_cords(heights)
                    print(cords)
                    blocks = parser.bulk_get_blocks(cords)
                data_parsed[row_idx].append(blocks)

        return data_parsed


cm = ChunkManager(Path(r"C:\Users\DNS\PycharmProjects\BedrockPatternFinder\minecraft\overworld"), "Overworld")
corners = Corners(-10,10,-10,10)
c = cm.get_chunks(corners)
# print(c[0].abs_cord)
gp = GroundProjector(c)
# gp.project()
a = list(gp.project()[5][2])
print(a.count("minecraft:air"), a)




# mp = McaParser()
# f = open("r.-6.-6.mca", "rb")
# rg = RawRegion(f.read(),TwoDimCord((0,0)),"Overworld")
# f.close()
# rg = mp.parse(rg)
# dataa = []
# for cord in rg.raw_chunks.keys():
#     data =rg.raw_chunks[cord].raw_data
#     if data:
#         parser = NBTTagReader(data)
#         d = parser.parse_through_tree(["Heightmaps","WORLD_SURFACE"])
#         dataa.append(d.value["WORLD_SURFACE"])
#
# dv = np.concatenate(dataa)
# print(dv.dtype)
#
#
