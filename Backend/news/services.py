from io import BytesIO

from django.core.cache import cache
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from families.models import FamilyMember, Relationship

from .models import Media, Post


def _font(size):
    try:
        return ImageFont.truetype('arial.ttf', size)
    except Exception:
        return ImageFont.load_default()


def _make_poster(title, subtitle, member=None):
    width, height = 1080, 1350
    image = Image.new('RGB', (width, height), color=(30, 64, 58))
    draw = ImageDraw.Draw(image)

    # Decorative gradient-like bands for visual depth.
    draw.rectangle([(0, 0), (width, 220)], fill=(199, 155, 91))
    draw.rectangle([(0, height - 240), (width, height)], fill=(18, 42, 38))

    if member and getattr(member, 'photo', None):
        try:
            with member.photo.open('rb') as photo_file:
                profile = Image.open(photo_file).convert('RGB')
                profile = profile.resize((520, 520))
                image.paste(profile, ((width - 520) // 2, 300))
        except Exception:
            draw.rectangle([(280, 300), (800, 820)], fill=(88, 118, 86))
    else:
        draw.rectangle([(280, 300), (800, 820)], fill=(88, 118, 86))

    title_font = _font(64)
    subtitle_font = _font(44)
    body_font = _font(34)

    draw.text((width // 2, 90), title, font=title_font, fill=(25, 25, 25), anchor='mm')
    draw.text((width // 2, 900), subtitle, font=subtitle_font, fill=(255, 255, 255), anchor='mm')
    draw.text(
        (width // 2, 980),
        f"{timezone.localdate().strftime('%d %b %Y')}",
        font=body_font,
        fill=(230, 230, 230),
        anchor='mm',
    )

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

    poster = _make_poster(title=title, subtitle=description, member=member)
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
