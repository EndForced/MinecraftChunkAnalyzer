from dataclasses import dataclass

@dataclass(frozen=True)
class NBTTagSpec:
    tag_id: int
    fixed_size: int | None
    has_length_field: bool = False


TAG_SPECS = {
    0:  NBTTagSpec(0, 0),
    1:  NBTTagSpec(1, 1),      # byte
    2:  NBTTagSpec(2, 2),      # short
    3:  NBTTagSpec(3, 4),      # int
    4:  NBTTagSpec(4, 8),      # long
    5:  NBTTagSpec(5, 4),      # float
    6:  NBTTagSpec(6, 8),      # double
    7:  NBTTagSpec(7, None, True),  # byte array
    8:  NBTTagSpec(8, None, True),  # string
    9:  NBTTagSpec(9, None),        # list
    10: NBTTagSpec(10, None),       # compound
    11: NBTTagSpec(11, None, True), # int array
    12: NBTTagSpec(12, None, True), # long array
}

def get_tag_spec_by_id(tag_id: int) -> NBTTagSpec:
    return TAG_SPECS[tag_id]
