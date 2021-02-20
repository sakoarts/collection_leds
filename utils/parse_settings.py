

def determine_exclude_choice_leds(exclude_choice, segments):
    exclude_leds = exclude_choice['exclude_leds']
    for xs in exclude_choice['exclude_segments']:
        exclude_leds += list(range(xs))
    if exclude_choice['exclude_ends']:
        for s in segments:
            exclude_leds += s[:exclude_choice['exclude_ends_n']] + s[-exclude_choice['exclude_ends_n']:]
    return exclude_leds


def determine_segments(segment_settings):
    segments = []
    for seg in segment_settings:
        seg[1] += 1
        segments.append(list(range(*seg)))

    return segments
