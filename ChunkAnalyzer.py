import numpy as np
from numba import jit


@jit(nopython=True)
def extract_block_id_fast(block_data, block_index, bits_per_block, palette_size):
    blocks_per_long = 64 // bits_per_block
    long_index = block_index // blocks_per_long
    bit_offset = (block_index % blocks_per_long) * bits_per_block

    if long_index < len(block_data):
        block_id = (block_data[long_index] >> bit_offset) & ((1 << bits_per_block) - 1)
        return block_id if block_id < palette_size else 0
    return 0


class FastChunkAnalyzer:
    def __init__(self, sections):
        self.sections = sections
        self._build_lookup()

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
                        if block_index < 4096:  # 16x16x16
                            y_local = block_index // 256
                            remainder = block_index % 256
                            z_local = remainder // 16
                            x_local = remainder % 16

                            world_y = section['y'] * 16 + y_local
                            if min_y <= world_y <= max_y:
                                locations.append((x_local, world_y, z_local))

        return locations