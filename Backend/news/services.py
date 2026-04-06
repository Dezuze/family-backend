from io import BytesIO
import os

from django.core.cache import cache
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont, ImageOps

from families.models import FamilyMember, Relationship

from .models import Media, Post


def _font(size, *, style='regular'):
    windir = os.environ.get('WINDIR', 'C:/Windows')
    fonts_dir = os.path.join(windir, 'Fonts')

    candidates = {
        'script': ['segoesc.ttf', 'gabriola.ttf', 'timesi.ttf', 'ariali.ttf'],
        'bold': ['arialbd.ttf', 'timesbd.ttf', 'calibrib.ttf'],
        'regular': ['arial.ttf', 'times.ttf', 'calibri.ttf'],
    }

    for name in candidates.get(style, candidates['regular']):
        try:
            return ImageFont.truetype(os.path.join(fonts_dir, name), size)
        except Exception:
            continue

    try:
        return ImageFont.truetype('arial.ttf', size)
    except Exception:
        return ImageFont.load_default()


def _draw_vertical_gradient(draw, width, height, top_rgb, bottom_rgb):
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(top_rgb[0] + (bottom_rgb[0] - top_rgb[0]) * t)
        g = int(top_rgb[1] + (bottom_rgb[1] - top_rgb[1]) * t)
        b = int(top_rgb[2] + (bottom_rgb[2] - top_rgb[2]) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def _draw_rose(draw, center_x, center_y, scale=1.0):
    petal = (150, 35, 55)
    petal_light = (184, 55, 76)
    stem = (35, 98, 60)

    radius = int(20 * scale)
    draw.ellipse([(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)], fill=petal)
    draw.ellipse([(center_x - radius - 8, center_y - 2), (center_x + 4, center_y + radius + 6)], fill=petal_light)
    draw.ellipse([(center_x - 2, center_y - radius - 8), (center_x + radius + 8, center_y + 4)], fill=petal_light)

    stem_y2 = center_y + int(120 * scale)
    draw.line([(center_x, center_y + radius), (center_x, stem_y2)], fill=stem, width=max(2, int(4 * scale)))
    draw.polygon(
        [
            (center_x, center_y + 42 * scale),
            (center_x - 22 * scale, center_y + 62 * scale),
            (center_x, center_y + 72 * scale),
        ],
        fill=(50, 120, 70),
    )


def _draw_balloons(draw, width, height):
    balloon_specs = [
        (0.24, 0.2, (78, 134, 227)),
        (0.36, 0.16, (44, 108, 202)),
        (0.78, 0.2, (78, 134, 227)),
        (0.66, 0.16, (44, 108, 202)),
    ]
    for rel_x, rel_y, color in balloon_specs:
        x = int(width * rel_x)
        y = int(height * rel_y)
        rx = int(width * 0.04)
        ry = int(height * 0.045)
        draw.ellipse([(x - rx, y - ry), (x + rx, y + ry)], fill=color)
        draw.line([(x, y + ry), (x - int(width * 0.01), y + ry + int(height * 0.08))], fill=(228, 240, 255), width=2)


def _draw_wedding_theme(draw, width, height):
    ring_color = (226, 198, 127)
    cx = width // 2
    cy = int(height * 0.24)

    ring_w = int(width * 0.095)
    ring_h = int(height * 0.065)
    offset = int(width * 0.05)
    stroke = max(4, int(width * 0.006))
    draw.ellipse([(cx - offset - ring_w, cy - ring_h), (cx - offset, cy + ring_h)], outline=ring_color, width=stroke)
    draw.ellipse([(cx + offset, cy - ring_h), (cx + offset + ring_w, cy + ring_h)], outline=ring_color, width=stroke)


def _draw_flower(draw, x, y, scale, petal, center, leaf):
    r = max(4, int(14 * scale))
    offsets = [(-r, 0), (r, 0), (0, -r), (0, r), (-int(r * 0.7), -int(r * 0.7)), (int(r * 0.7), int(r * 0.7))]
    for ox, oy in offsets:
        draw.ellipse([(x + ox - r, y + oy - r), (x + ox + r, y + oy + r)], fill=petal)
    draw.ellipse([(x - int(r * 0.7), y - int(r * 0.7)), (x + int(r * 0.7), y + int(r * 0.7))], fill=center)
    draw.ellipse([(x - int(r * 2.2), y + r), (x - int(r * 0.3), y + int(r * 2.8))], fill=leaf)
    draw.ellipse([(x + int(r * 0.3), y + r), (x + int(r * 2.2), y + int(r * 2.8))], fill=leaf)


def _draw_floral_corner(draw, width, height, corner):
    petal = (248, 199, 205)
    center = (243, 138, 90)
    leaf = (167, 204, 179)

    if corner == 'tl':
        base_x, base_y, sx, sy = int(width * 0.08), int(height * 0.08), 1, 1
    elif corner == 'tr':
        base_x, base_y, sx, sy = int(width * 0.92), int(height * 0.08), -1, 1
    elif corner == 'bl':
        base_x, base_y, sx, sy = int(width * 0.08), int(height * 0.92), 1, -1
    else:
        base_x, base_y, sx, sy = int(width * 0.92), int(height * 0.92), -1, -1

    _draw_flower(draw, base_x, base_y, 1.2, petal, center, leaf)
    _draw_flower(draw, base_x + int(sx * width * 0.06), base_y + int(sy * height * 0.03), 0.8, petal, center, leaf)
    _draw_flower(draw, base_x + int(sx * width * 0.1), base_y + int(sy * height * 0.07), 0.65, petal, center, leaf)


def _draw_death_theme(draw, width, height):
    for corner in ('tl', 'tr', 'bl'):
        _draw_floral_corner(draw, width, height, corner)


def _draw_symmetric_frame(draw, width, height, color):
    pad = int(width * 0.04)
    draw.rounded_rectangle([(pad, pad), (width - pad, height - pad)], radius=int(width * 0.03), outline=color, width=2)
    inner = int(width * 0.012)
    draw.rounded_rectangle(
        [(pad + inner, pad + inner), (width - pad - inner, height - pad - inner)],
        radius=int(width * 0.024),
        outline=color,
        width=1,
    )


def _draw_placeholder_monogram(draw, member, left, top, size, accent, circular=False):
    # Keep placeholder clean and aligned with the intended photo frame shape.
    if circular:
        draw.ellipse(
            [(left, top), (left + size, top + size)],
            fill=(224, 231, 244),
            outline=(201, 209, 226),
            width=3,
        )
    else:
        draw.rounded_rectangle(
            [(left, top), (left + size, top + size)],
            radius=int(size * 0.08),
            fill=(224, 231, 244),
            outline=(201, 209, 226),
            width=3,
        )

    name = getattr(member, 'name', '') if member else ''
    parts = [p for p in str(name).split() if p]
    initials = ''.join(p[0] for p in parts[:2]).upper() or 'KF'
    monogram_font = _font(max(28, int(size * 0.2)), style='bold')
    draw.text((left + size // 2, top + size // 2), initials, font=monogram_font, fill=accent, anchor='mm')


def _paste_circular_member_photo(image, member, center_x, center_y, diameter):
    if not (member and getattr(member, 'photo', None)):
        return False

    try:
        with member.photo.open('rb') as photo_file:
            src = Image.open(photo_file).convert('RGB')
            fitted = ImageOps.fit(src, (diameter, diameter), method=Image.Resampling.LANCZOS)

            circle_mask = Image.new('L', (diameter, diameter), 0)
            mask_draw = ImageDraw.Draw(circle_mask)
            mask_draw.ellipse([(0, 0), (diameter - 1, diameter - 1)], fill=255)

            fitted_rgba = fitted.convert('RGBA')
            fitted_rgba.putalpha(circle_mask)
            image.paste(fitted_rgba, (center_x - diameter // 2, center_y - diameter // 2), fitted_rgba)
            return True
    except Exception:
        return False


def _extract_wedding_names(subtitle):
    text = str(subtitle or '').strip()
    if text.startswith('Warm wishes to ') and text.endswith('.'):
        return text[len('Warm wishes to '):-1]
    return text


def _fmt_date(value):
    if not value:
        return None
    try:
        return value.strftime('%B %d, %Y')
    except Exception:
        return None


def _wrap_text(text, font, max_width):
    words = str(text or '').split()
    if not words:
        return ['']

    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        width = font.getbbox(candidate)[2] - font.getbbox(candidate)[0]
        if width <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _text_size(draw, text, font):
    l, t, r, b = draw.textbbox((0, 0), str(text or ''), font=font)
    return max(0, r - l), max(0, b - t)


def _draw_centered_text(draw, x, y, text, font, fill):
    w, h = _text_size(draw, text, font)
    draw.text((int(x - w / 2), int(y - h / 2)), str(text or ''), font=font, fill=fill)


def _fit_font(draw, text, *, style='regular', start=40, min_size=20, max_width=600):
    size = start
    while size >= min_size:
        font = _font(size, style=style)
        w, _ = _text_size(draw, text, font)
        if w <= max_width:
            return font
        size -= 2
    return _font(min_size, style=style)


def _make_poster(title, subtitle, kind, member=None):
    # 3:4 poster ratio tuned for faster loading.
    width, height = 900, 1200
    image = Image.new('RGB', (width, height), color=(22, 45, 42))
    draw = ImageDraw.Draw(image)

    if kind == 'birthday':
        # Birthday template: blue card, top sticker headline, portrait block, name plate.
        _draw_vertical_gradient(draw, width, height, (201, 227, 236), (186, 216, 227))
        _draw_balloons(draw, width, height)
        accent = (19, 74, 163)
        draw.rounded_rectangle([(int(width * 0.05), int(height * 0.04)), (int(width * 0.95), int(height * 0.96))], radius=20, outline=(164, 199, 220), width=2)

        sticker_left = int(width * 0.18)
        sticker_top = int(height * 0.06)
        sticker_right = int(width * 0.56)
        sticker_bottom = int(height * 0.14)
        draw.polygon(
            [
                (sticker_left, sticker_top + 12),
                (sticker_right, sticker_top),
                (sticker_right, sticker_bottom - 12),
                (sticker_left, sticker_bottom),
            ],
            fill=(18, 56, 124),
        )
        _draw_centered_text(draw, int(width * 0.37), int(height * 0.1), 'Happy Birthday', _font(48, style='script'), (255, 255, 255))
        _draw_centered_text(draw, int(width * 0.3), int(height * 0.045), 'WISHING YOU THE BEST', _font(18, style='regular'), (38, 72, 94))

        photo_left = int(width * 0.27)
        photo_top = int(height * 0.2)
        photo_size = int(width * 0.46)

        if member and getattr(member, 'photo', None):
            try:
                with member.photo.open('rb') as photo_file:
                    profile = Image.open(photo_file).convert('RGB').resize((photo_size, photo_size))
                    image.paste(profile, (photo_left, photo_top))
            except Exception:
                _draw_placeholder_monogram(draw, member, photo_left, photo_top, photo_size, (255, 255, 255))
        else:
            _draw_placeholder_monogram(draw, member, photo_left, photo_top, photo_size, (255, 255, 255))

        name = getattr(member, 'name', 'Family Member') if member else 'Family Member'
        name_left = int(width * 0.46)
        name_top = int(height * 0.58)
        name_w = int(width * 0.33)
        name_h = int(height * 0.07)
        draw.rectangle([(name_left, name_top), (name_left + name_w, name_top + name_h)], fill=(28, 83, 170))
        name_font = _fit_font(draw, name, style='script', start=30, min_size=20, max_width=int(name_w * 0.9))
        _draw_centered_text(draw, name_left + name_w // 2, name_top + name_h // 2, name, name_font, (255, 255, 255))

        body = 'Wishing you a wonderful day and many blessings for the year ahead!'
        body_lines = _wrap_text(body, _font(21), int(width * 0.44))
        by = int(height * 0.73)
        for line in body_lines[:2]:
            _draw_centered_text(draw, int(width * 0.56), by, line, _font(21), (42, 78, 103))
            by += int(height * 0.03)
        _draw_centered_text(draw, int(width * 0.53), int(height * 0.82), 'from your loving friends', _font(22, style='script'), (32, 66, 95))

    elif kind == 'death_anniversary':
        # Memorial template: floral corners, cross, circular framed portrait.
        _draw_vertical_gradient(draw, width, height, (249, 245, 245), (241, 236, 236))
        _draw_death_theme(draw, width, height)
        accent = (84, 88, 95)

        _draw_centered_text(draw, width // 2, int(height * 0.12), '+', _font(56, style='regular'), (74, 78, 82))
        _draw_centered_text(draw, width // 2, int(height * 0.2), 'In loving memory of', _font(52, style='script'), (82, 84, 90))

        ring_cx = width // 2
        ring_cy = int(height * 0.43)
        ring_r = int(width * 0.2)
        draw.ellipse([(ring_cx - ring_r - 7, ring_cy - ring_r - 7), (ring_cx + ring_r + 7, ring_cy + ring_r + 7)], outline=(210, 184, 142), width=8)
        draw.ellipse([(ring_cx - ring_r, ring_cy - ring_r), (ring_cx + ring_r, ring_cy + ring_r)], fill=(235, 238, 245))

        pasted = _paste_circular_member_photo(image, member, ring_cx, ring_cy, ring_r * 2)
        if not pasted:
            _draw_placeholder_monogram(
                draw,
                member,
                ring_cx - ring_r,
                ring_cy - ring_r,
                ring_r * 2,
                (92, 96, 106),
                circular=True,
            )

        member_name = getattr(member, 'name', 'Beloved Member') if member else 'Beloved Member'
        name_font = _fit_font(draw, member_name, style='script', start=64, min_size=34, max_width=int(width * 0.78))
        _draw_centered_text(draw, width // 2, int(height * 0.66), member_name, name_font, (71, 74, 79))

        dob = _fmt_date(getattr(member, 'date_of_birth', None) if member else None)
        dod = _fmt_date(getattr(member, 'date_of_death', None) if member else None)
        if dob and dod:
            _draw_centered_text(draw, width // 2, int(height * 0.73), f'{dob} - {dod}', _font(25, style='regular'), accent)
        _draw_centered_text(draw, width // 2, int(height * 0.79), 'Forever remembered with love and prayers', _font(28, style='script'), accent)

    else:
        # Anniversary template: floral corners + oval card and centered hierarchy.
        _draw_vertical_gradient(draw, width, height, (243, 236, 224), (231, 221, 204))
        for corner in ('tl', 'tr', 'bl', 'br'):
            _draw_floral_corner(draw, width, height, corner)

        oval_left = int(width * 0.1)
        oval_top = int(height * 0.04)
        oval_right = int(width * 0.9)
        oval_bottom = int(height * 0.96)
        draw.ellipse([(oval_left, oval_top), (oval_right, oval_bottom)], outline=(133, 125, 76), width=3)

        _draw_centered_text(draw, width // 2, int(height * 0.12), 'HAPPY', _font(72, style='regular'), (36, 36, 36))
        _draw_centered_text(draw, width // 2, int(height * 0.19), 'Anniversary', _font(86, style='script'), (28, 28, 28))

        photo_w = int(width * 0.5)
        photo_h = int(height * 0.22)
        photo_left = (width - photo_w) // 2
        photo_top = int(height * 0.29)
        draw.ellipse([(photo_left - 6, photo_top - 6), (photo_left + photo_w + 6, photo_top + photo_h + 6)], fill=(219, 219, 224))
        draw.rounded_rectangle([(photo_left, photo_top), (photo_left + photo_w, photo_top + photo_h)], radius=45, fill=(228, 233, 241))

        if member and getattr(member, 'photo', None):
            try:
                with member.photo.open('rb') as photo_file:
                    profile = Image.open(photo_file).convert('RGB').resize((photo_w, photo_h))
                    image.paste(profile, (photo_left, photo_top))
            except Exception:
                _draw_placeholder_monogram(draw, member, photo_left, photo_top, min(photo_w, photo_h), (60, 60, 60))
        else:
            _draw_placeholder_monogram(draw, member, photo_left, photo_top, min(photo_w, photo_h), (60, 60, 60))

        pair = _extract_wedding_names(subtitle).upper()
        pair_font = _fit_font(draw, pair, style='regular', start=58, min_size=34, max_width=int(width * 0.74))
        pair_lines = _wrap_text(pair, pair_font, int(width * 0.74))
        py = int(height * 0.57)
        for line in pair_lines[:2]:
            _draw_centered_text(draw, width // 2, py, line, pair_font, (28, 28, 28))
            py += int(height * 0.05)

        _draw_centered_text(draw, width // 2, int(height * 0.68), timezone.localdate().strftime('%B %d, %Y'), _font(46, style='regular'), (32, 32, 32))
        _draw_centered_text(draw, width // 2, int(height * 0.74), 'With love and blessings from KFA', _font(34, style='script'), (56, 56, 56))

    output = BytesIO()
    image.save(output, format='PNG', optimize=True)
    output.seek(0)
    return output


def _create_generated_post(*, key, title, description, kind, member, post_type='news', event_date=None):
    if Post.objects.filter(generated_key=key).exists():
        return

    creator = member or FamilyMember.objects.order_by('id').first()
    if not creator:
        return

    post = Post.objects.create(
        creator=creator,
        post_type=post_type,
        title=title,
        description=description,
        event_date=event_date,
        visibility='members',
        is_auto_generated=True,
        generated_kind=kind,
        generated_for_member=member,
        generated_key=key,
    )

    poster = _make_poster(title=title, subtitle=description, kind=kind, member=member)
    filename = f"poster-{key}.png"
    Media.objects.create(
        uploader=creator,
        post=post,
        media_url=ContentFile(poster.read(), name=filename),
        media_type='image',
    )


def ensure_daily_anniversary_posts():
    today = timezone.localdate()
    cache_key = f"anniversary-generated:{today.isoformat()}"
    if cache.get(cache_key):
        return

    birthdays = FamilyMember.objects.filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day,
        is_deceased=False,
    )
    for member in birthdays:
        member_pk = getattr(member, 'pk', None)
        key = f"birthday-{member_pk}-{today.isoformat()}"
        _create_generated_post(
            key=key,
            title='Birthday Wishes',
            description=f"Celebrating birthday of {member.name}.",
            kind='birthday',
            member=member,
            post_type='news',
        )

    death_anniversaries = FamilyMember.objects.filter(
        is_deceased=True,
        date_of_death__month=today.month,
        date_of_death__day=today.day,
    )
    for member in death_anniversaries:
        member_pk = getattr(member, 'pk', None)
        key = f"death-anniversary-{member_pk}-{today.isoformat()}"
        _create_generated_post(
            key=key,
            title='In Loving Memory',
            description=f"Remembering {member.name} on their death anniversary.",
            kind='death_anniversary',
            member=member,
            post_type='news',
        )

    marriage_anniversaries = Relationship.objects.filter(
        relation_type='SPOUSE',
        anniversary_date__month=today.month,
        anniversary_date__day=today.day,
    ).select_related('from_member', 'to_member')

    for rel in marriage_anniversaries:
        from_pk = getattr(getattr(rel, 'from_member', None), 'pk', None)
        to_pk = getattr(getattr(rel, 'to_member', None), 'pk', None)
        if from_pk is None or to_pk is None:
            continue
        id_pair = sorted([from_pk, to_pk])
        key = f"marriage-anniversary-{id_pair[0]}-{id_pair[1]}-{today.isoformat()}"
        title = 'Wedding Anniversary'
        description = f"Warm wishes to {rel.from_member.name} and {rel.to_member.name}."
        _create_generated_post(
            key=key,
            title=title,
            description=description,
            kind='marriage_anniversary',
            member=rel.from_member,
            post_type='event',
            event_date=timezone.now(),
        )

    cache.set(cache_key, True, timeout=60 * 60)
