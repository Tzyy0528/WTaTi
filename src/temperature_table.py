"""Temperature windows for automatic scheduling.

The staged workflow uses explicitly approved MD conditions.
Populate this table only if automatic scheduling is separately validated.
"""


TEMPERATURE_TABLE = {}


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
    """在熔点和沸点之间生成指定数量的采样温度。"""
    if n_rounds < 1:
        return []

    melting_point, boiling_point = get_temperature_window(symbols)
    t_min = melting_point + margin * (boiling_point - melting_point)
    t_max = boiling_point - margin * (boiling_point - melting_point)

    if n_rounds == 1:
        return [(t_min + t_max) / 2.0]

    step = (t_max - t_min) / (n_rounds - 1)
    return [t_min + i * step for i in range(n_rounds)]
