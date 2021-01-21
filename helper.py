def stats_to_fan_points(statistics: Dict) -> str:
    fan_points = 0
    for stat_name, stat_value in statistics.items():
        if stat_name in stat_modifier:
            fan_points = fan_points + (float(stat_value) * float(get_stat_modifier_by_name(stat_name)))
    return str(round(float(fan_points), 2))
