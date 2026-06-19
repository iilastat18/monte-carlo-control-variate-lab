from __future__ import annotations

from pathlib import Path


def write_line_chart_svg(
    *,
    title: str,
    subtitle: str,
    x_values: list[float],
    left_values: list[float],
    right_values: list[float],
    left_label: str,
    right_label: str,
    output_path: Path,
) -> None:
    width, height = 1500, 920
    left, right, top, bottom = 140, 1350, 200, 780
    chart_width = right - left
    chart_height = bottom - top

    x_min, x_max = min(x_values), max(x_values)
    y_min = min(min(left_values), min(right_values))
    y_max = max(max(left_values), max(right_values))
    y_span = max(y_max - y_min, 1.0e-8)
    y_min -= 0.08 * y_span
    y_max += 0.10 * y_span
    y_span = y_max - y_min

    def px(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * chart_width

    def py(value: float) -> float:
        return bottom - (value - y_min) / y_span * chart_height

    left_path = " ".join(
        ("M" if i == 0 else "L") + f" {px(x):.2f} {py(y):.2f}"
        for i, (x, y) in enumerate(zip(x_values, left_values))
    )
    right_path = " ".join(
        ("M" if i == 0 else "L") + f" {px(x):.2f} {py(y):.2f}"
        for i, (x, y) in enumerate(zip(x_values, right_values))
    )

    svg = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="1500" height="920" rx="28" fill="#0B1220"/>',
        f'<text x="{left}" y="108" fill="#F5F7FB" font-size="40" font-weight="700" font-family="SF Pro Display, Helvetica, Arial, sans-serif">{title}</text>',
        f'<text x="{left}" y="146" fill="#91A4BD" font-size="18" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{subtitle}</text>',
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#32455E" stroke-width="2"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#32455E" stroke-width="2"/>',
        '<rect x="1040" y="84" width="18" height="18" rx="4" fill="#FFC86E"/>',
        f'<text x="1072" y="99" fill="#DDE8F4" font-size="16" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{left_label}</text>',
        '<rect x="1200" y="84" width="18" height="18" rx="4" fill="#61D9FF"/>',
        f'<text x="1232" y="99" fill="#DDE8F4" font-size="16" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{right_label}</text>',
    ]

    for grid in range(5):
        y = bottom - chart_height * grid / 4
        value = y_min + y_span * grid / 4
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#1B2B40" stroke-width="1"/>')
        svg.append(f'<text x="42" y="{y + 6:.1f}" fill="#7890AA" font-size="16" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{value:.5f}</text>')

    for x in x_values:
        xpos = px(x)
        svg.append(f'<line x1="{xpos:.1f}" y1="{top}" x2="{xpos:.1f}" y2="{bottom}" stroke="#132338" stroke-width="1"/>')
        svg.append(f'<text x="{xpos - 28:.1f}" y="820" fill="#AABED6" font-size="15" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{int(x):,}</text>')

    svg.append(f'<path d="{left_path}" stroke="#FFC86E" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    svg.append(f'<path d="{right_path}" stroke="#61D9FF" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    for x, y in zip(x_values, left_values):
        svg.append(f'<circle cx="{px(x):.2f}" cy="{py(y):.2f}" r="7" fill="#FFC86E"/>')
    for x, y in zip(x_values, right_values):
        svg.append(f'<circle cx="{px(x):.2f}" cy="{py(y):.2f}" r="7" fill="#61D9FF"/>')
    svg.append("</svg>")
    output_path.write_text("\n".join(svg), encoding="utf-8")


def write_bar_chart_svg(
    *,
    title: str,
    subtitle: str,
    categories: list[str],
    values: list[float],
    output_path: Path,
) -> None:
    width, height = 1500, 920
    left, right, top, bottom = 150, 1350, 200, 780
    chart_width = right - left
    chart_height = bottom - top
    maximum = max(values) * 1.12 if values else 1.0
    category_width = chart_width / max(len(categories), 1)

    svg = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="1500" height="920" rx="28" fill="#0B1220"/>',
        f'<text x="{left}" y="108" fill="#F5F7FB" font-size="40" font-weight="700" font-family="SF Pro Display, Helvetica, Arial, sans-serif">{title}</text>',
        f'<text x="{left}" y="146" fill="#91A4BD" font-size="18" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{subtitle}</text>',
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#32455E" stroke-width="2"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#32455E" stroke-width="2"/>',
    ]

    for grid in range(5):
        y = bottom - chart_height * grid / 4
        value = maximum * grid / 4
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#1B2B40" stroke-width="1"/>')
        svg.append(f'<text x="54" y="{y + 6:.1f}" fill="#7890AA" font-size="16" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{value:.1f}x</text>')

    for index, (category, value) in enumerate(zip(categories, values)):
        bar_width = min(110.0, category_width * 0.45)
        center = left + category_width * (index + 0.5)
        bar_height = chart_height * value / maximum
        x = center - bar_width / 2
        y = bottom - bar_height
        svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" rx="14" fill="#76F1C5"/>')
        svg.append(f'<text x="{x - 5:.1f}" y="{y - 10:.1f}" fill="#D7F9EA" font-size="15" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{value:.1f}x</text>')
        svg.append(f'<text x="{center - category_width * 0.16:.1f}" y="820" fill="#AABED6" font-size="15" font-family="SF Pro Text, Helvetica, Arial, sans-serif">{category}</text>')

    svg.append("</svg>")
    output_path.write_text("\n".join(svg), encoding="utf-8")
