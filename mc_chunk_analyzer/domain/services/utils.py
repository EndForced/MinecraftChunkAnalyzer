from pathlib import Path
from typing import List, Set, Tuple
import re

from ..models.Region import RawRegion
from ..models.Chunk import RawChunk
from ..models.Chunk import Corners
from ...domain.models.Chunk import Dimensions
from ..services.ChunkAnalyzer import McaParser
from ...infrastructure.fs.services import search_for_files


class ChunkManager:
    """
    path + corners -> List[RawChunk]
    """

    def __init__(self, root: Path, dimension: Dimensions):
        self._root = root
        self._parser = McaParser()
        self._dimension = dimension

    def get_chunks(self, corners: Corners) -> List[RawChunk]:
        regions = self._load_required_regions(corners)
        return self._extract(regions, corners)

    # ---------- region logic ----------

    def _load_required_regions(self, corners: Corners) -> List[RawRegion]:
        region_coords = self._get_required_region_coords(corners)
        region_paths = self._find_region_files(region_coords)
        return [RawRegion(path, self._dimension) for path in region_paths]

    def _get_required_region_coords(self, corners: Corners) -> Set[tuple[int, int]]:
        # Используем .zmin / .zmax если они есть,
        # либо четко осознаем, что y в Corners — это на самом деле Z на карте
        rx_min = corners.xmin // 32
        rx_max = corners.xmax // 32
        rz_min = corners.ymin // 32  # <-- Проверь имя поля в классе Corners!
        rz_max = corners.ymax // 32

        return {
            (rx, rz)
            for rx in range(rx_min, rx_max + 1)
            for rz in range(rz_min, rz_max + 1)
        }

    from pathlib import Path
    from typing import List, Set, Tuple

    def _find_region_files(
            self,
            region_coords: Set[Tuple[int, int]]
    ) -> List[Path]:
        """
        Finds only region files matching the given region_coords (rx, rz)
        using `search_for_files` and without regex.
        """
        region_dir = self._root
        target_files = {f"r.{rx}.{rz}.mca" for rx, rz in region_coords}
        all_mca_files = search_for_files(files=list(target_files), root=region_dir)
        return all_mca_files

    # ---------- chunk logic ----------

    def _extract(self, data: List[RawRegion], corners: Corners) -> List[RawChunk]:
        xmin = corners.xmin - 1
        xmax = corners.xmax + 1
        zmin = corners.ymin - 1
        zmax = corners.ymax + 1

        result: List[RawChunk] = []

        for region in data:
            parsed = self._parser.parse(region)

            for cord, chunk in parsed.raw_chunks.items():
                if xmin <= cord.x <= xmax and zmin <= cord.z <= zmax:
                    result.append(chunk)

        return result


import time
from collections import defaultdict

class Profiler:
    def __init__(self):
        self.stats = defaultdict(float)
        self.counts = defaultdict(int)

    def __call__(self, name):
        """Используется как контекстный менеджер: with prof('name'):"""
        class Timer:
            def __init__(self, outer, name):
                self.outer = outer
                self.name = name
            def __enter__(self):
                self.start = time.perf_counter()
            def __exit__(self, *args):
                dt = time.perf_counter() - self.start
                self.outer.stats[self.name] += dt
                self.outer.counts[self.name] += 1
        return Timer(self, name)

    def report(self):
        print(f"\n{'='*20} PERFORMANCE REPORT {'='*20}")
        print(f"{'Step':<20} | {'Total (s)':<10} | {'Avg (ms)':<10} | {'Calls':<8}")
        print("-" * 55)
        for name in sorted(self.stats, key=self.stats.get, reverse=True):
            total = self.stats[name]
            count = self.counts[name]
            avg = (total / count) * 1000
            print(f"{name:<20} | {total:<10.4f} | {avg:<10.2f} | {count:<8}")
        print("=" * 55)



if __name__ == "__main__":
    c = Corners(-10,10,-10,10)




