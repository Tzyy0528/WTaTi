"""Reference elemental phase-change temperatures and high-temperature MD targets.

The staged unary workflow uses the melting-to-boiling interval for its
high-temperature exploratory MD target.  This is intentionally a liquid or
near-liquid sampling regime rather than a solid-phase MD schedule.

Values below are normal-pressure values in kelvin transcribed from the
peer-reviewed melting- and boiling-point records served by PubChem PUG View
on 2026-07-24:
  W:  https://pubchem.ncbi.nlm.nih.gov/compound/23964
  Ta: https://pubchem.ncbi.nlm.nih.gov/compound/23956
  Ti: https://pubchem.ncbi.nlm.nih.gov/compound/23963
"""


TEMPERATURE_TABLE = {
    # Reported values: 3410/5900 degC (W), 2996/5429 degC (Ta),
    # and 1668/3287 degC (Ti), converted by adding 273.15 K.
    ("W",): {"melting_point_K": 3683.15, "boiling_point_K": 6173.15},
    ("Ta",): {"melting_point_K": 3269.15, "boiling_point_K": 5702.15},
    ("Ti",): {"melting_point_K": 1941.15, "boiling_point_K": 3560.15},
}


def normalize_symbols(symbols):
    """返回排序去重后的元素元组，例如 ['Al', 'Al'] -> ('Al',)。"""
    return tuple(sorted(set(symbols)))


def get_temperature_window(symbols):
    """返回给定元素集合的熔点和沸点温度窗口。"""
    key = normalize_symbols(symbols)
    if key not in TEMPERATURE_TABLE:
        available = ", ".join("-".join(k) for k in sorted(TEMPERATURE_TABLE))
        if not available:
            available = "none; configure an approved temperature window first"
        raise KeyError(f"No temperature data for {'-'.join(key)}. Available: {available}")

    data = TEMPERATURE_TABLE[key]
    return data["melting_point_K"], data["boiling_point_K"]


def make_temperatures(symbols, n_rounds, margin=0.1):
    """生成熔点与沸点之间的高温探索 MD 温度。"""
    if n_rounds < 1:
        return []

    melting_point, boiling_point = get_temperature_window(symbols)
    t_min = melting_point + margin * (boiling_point - melting_point)
    t_max = boiling_point - margin * (boiling_point - melting_point)

    if n_rounds == 1:
        return [(t_min + t_max) / 2.0]

    step = (t_max - t_min) / (n_rounds - 1)
    return [t_min + i * step for i in range(n_rounds)]
