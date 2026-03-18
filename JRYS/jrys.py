import json
import random
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter

from gsuid_core.bot import Bot
from gsuid_core.config import core_config
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.fonts.fonts import core_font
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import get_qq_avatar

from .jrys_config import JRYSConfig
from .utils.resource.RESOURCE_PATH import BG_IMAGE_PATH, CACHE_PATH

FORTUNE_DATA = [
    {"score": 98, "items": [
        {"level": "大吉·乾卦上九", "desc": "禄存星耀财帛宫，地产投资正逢时，金蟾献宝登门来，契约一签百事兴", "advice": "北方藏有金蟾宝，契约暗含吉利数，贵人登门莫错过，把握今日好时机"},
        {"level": "大吉·离卦九五", "desc": "文昌星临命宫旺，笔墨生辉百事成，才华锋芒不可挡，名利双收喜事临", "advice": "东南方位逢贵人，所谋之事必得偿，文书签订大吉日，声名远播四方扬"},
    ]},
    {"score": 95, "items": [
        {"level": "大吉·坤卦六五", "desc": "紫微入命百煞消，四方贵气竞来朝，财星高照运势旺，逢凶化吉步步高", "advice": "巳时出行得财喜，遇水之地藏机缘，贵人相助事竟成，南方有路通锦绣"},
        {"level": "大吉·震卦九四", "desc": "天乙贵人扶身旁，所图之事皆吉祥，红鸾星动好姻缘，出门向南百事顺", "advice": "红鸾星动情缘至，出门向南百事顺，贵人指路破迷津，今日签文占上上"},
    ]},
    {"score": 90, "items": [
        {"level": "大吉·巽卦九三", "desc": "禄马交驰财路宽，贵人指路破迷关，午时动身逢吉兆，西北藏有意外财", "advice": "午时起事事半功倍，西北方向藏意外之财，遇木之人可助力，今日宜大展宏图"},
        {"level": "大吉·兑卦九二", "desc": "金星入垣照命强，功名财帛俱昌旺，龙年吉月逢吉日，今日签文压群芳", "advice": "龙年吉月逢吉日，今日签文压群芳，财官双美前程亮，把握时机莫彷徨"},
    ]},
    {"score": 85, "items": [
        {"level": "大吉·乾卦九五", "desc": "福德宫中吉星聚，财官双美照前程，辰时动身逢吉兆，遇木之人可助力", "advice": "辰时动身逢吉兆，遇木之人可助力，财星拱照运气旺，好事将至不必急"},
        {"level": "大吉·艮卦九三", "desc": "山岳稳固根基深，积德行善福自临，贵人暗助拨云雾，吉星拱照百业兴", "advice": "稳中求进是上策，贵人暗助莫错过，积德之举有善报，今日诸事皆顺遂"},
    ]},
    {"score": 80, "items": [
        {"level": "中吉·艮卦六二", "desc": "月德合日百事顺，稳步前行积厚福，不宜急进宜守成，向东一步有转机", "advice": "不宜急进宜守成，向东一步有转机，蓄势待发正当时，厚积薄发终有成"},
        {"level": "中吉·坎卦九五", "desc": "水星照命财运通，逢水之地得贵助，巳午之间利交涉，签约合作可为之", "advice": "巳午之间利交涉，签约合作可为之，遇水之人有善缘，稳扎稳打运自来"},
    ]},
    {"score": 75, "items": [
        {"level": "中吉·离卦六三", "desc": "文星拱照万事宜，心诚则灵得天助，今日宜静不宜动，守中待时福自来", "advice": "今日宜静不宜动，守中待时福自来，诚心正意天自知，吉星暗助莫心慌"},
        {"level": "中吉·震卦六五", "desc": "天德月德合时令，求谋有望得善缘，向南出行逢吉星，午时前后利交际", "advice": "向南出行逢吉星，午时前后利交际，善缘将至需把握，天时地利人和聚"},
    ]},
    {"score": 70, "items": [
        {"level": "中平·坤卦六三", "desc": "日月合璧照平安，无风无浪渡此关，平常心待非常事，守正不偏自安然", "advice": "平常心待非常事，守正不偏自安然，波澜不惊是福气，岁月静好亦难得"},
        {"level": "中平·巽卦六四", "desc": "风平浪静守本分，顺势而为莫强求，默默耕耘自有获，守得云开见月明", "advice": "顺势而为莫强求，默默耕耘自有获，今日平顺是福分，积累实力待时机"},
    ]},
    {"score": 65, "items": [
        {"level": "小吉·兑卦初九", "desc": "小有波折终归顺，耐心等待时来运，勿与口舌之人争，向西北方得小利", "advice": "勿与口舌之人争，向西北方得小利，忍一时风平浪静，退一步海阔天空"},
        {"level": "小吉·乾卦初九", "desc": "潜龙勿用养精神，厚积薄发待时机，小事可为大事缓，步步为营稳前行", "advice": "小事可为大事缓，步步为营稳前行，此时不宜冒进，养精蓄锐是良策"},
    ]},
    {"score": 60, "items": [
        {"level": "小吉·巽卦初六", "desc": "风过无痕事渐明，潜心积累待春风，今日不宜大动作，细水长流方为上", "advice": "今日不宜大动作，细水长流方为上，平稳行事少是非，积少成多自然丰"},
        {"level": "小吉·坤卦初六", "desc": "履霜坚冰渐积成，点滴之功莫小觑，踏实行事人心服，终有一日厚积发", "advice": "踏实行事人心服，终有一日厚积发，莫因小利失大局，守正持中迎转机"},
    ]},
    {"score": 55, "items": [
        {"level": "末吉·艮卦初六", "desc": "山重水复疑无路，柳暗花明静心候，寅卯之时宜处事，遇土之人可商议", "advice": "寅卯之时宜处事，遇土之人可商议，困境之中莫气馁，转机就在前方处"},
        {"level": "末吉·离卦初九", "desc": "初出茅庐须谨慎，厉行节约莫轻率，守住本心不动摇，吉星迟早会眷顾", "advice": "谨慎行事莫轻率，守住本心不动摇，静待时机莫急躁，柳暗花明在后头"},
    ]},
    {"score": 50, "items": [
        {"level": "末吉·坎卦初六", "desc": "水星伏令财路滞，宜守不宜轻出击，避开西南凶煞方，向东一步可化解", "advice": "避开西南凶煞方，向东一步可化解，守财不漏是关键，等待转机需耐心"},
        {"level": "末吉·震卦初六", "desc": "雷伏地中待时机，蓄势须忍莫冒进，守住根基不动摇，天时到来自奋起", "advice": "守住根基不动摇，天时到来自奋起，此时守成胜过进，积蓄力量等良机"},
    ]},
    {"score": 45, "items": [
        {"level": "末凶·坤卦初六", "desc": "六爻皆动变数多，此时静观胜躁进，忌见官讼与借贷，低调处事保平安", "advice": "忌见官讼与借贷，低调处事保平安，变数之中需沉静，以退为进待转机"},
        {"level": "末凶·兑卦初六", "desc": "口舌是非纠缠多，言多必失需谨慎，今日出言须三思，祸从口出防小人", "advice": "言多必失需谨慎，出言须三思而行，防范小人暗中伤，沉默是金保周全"},
    ]},
    {"score": 40, "items": [
        {"level": "末凶·震卦初九", "desc": "雷声滚滚震惊起，蛰伏待机莫轻动，今日诸事宜从缓，积蓄能量待时变", "advice": "今日诸事宜从缓，积蓄能量待时变，动则生非不如静，养精蓄锐待东风"},
        {"level": "末凶·坎卦九二", "desc": "坎中有险需谨行，求小得小莫贪进，脚踏实地步步稳，方能渡过难关境", "advice": "求小得小莫贪进，脚踏实地步步稳，此时不宜大动作，谨慎行事可化险"},
    ]},
    {"score": 30, "items": [
        {"level": "凶·离卦初九", "desc": "火星克命诸事滞，小人暗算须防备，出行避开南方位，见火之事不吉利", "advice": "出行避开南方位，见火之事不吉利，防范小人暗中害，忍让为上莫争锋"},
        {"level": "凶·乾卦九三", "desc": "君子终日乾乾兢，多行多错少行安，反躬自省识时务，退守方能保无咎", "advice": "多行多错少行安，反躬自省识时务，今日宜少动多思，退守自保等时运"},
    ]},
    {"score": 20, "items": [
        {"level": "大凶·乾卦上六", "desc": "亢龙有悔势已衰，孤立无援凶象来，今日切忌大动干戈，静守家中可避灾", "advice": "今日切忌大动干戈，静守家中可避灾，过刚易折需柔化，低调蛰伏待来日"},
        {"level": "大凶·坤卦上六", "desc": "龙战于野血玄黄，天地交战难自保，诸事皆凶宜斋戒，默念平安保其身", "advice": "诸事皆凶宜斋戒，默念平安保其身，此时万事莫强求，静候时运自然转"},
    ]},
    {"score": 10, "items": [
        {"level": "极凶·坎卦上六", "desc": "系用徽纆陷丛棘，凶象已极四路绝，此签至凶勿出门，诚心向善可转圜", "advice": "此签至凶勿出门，诚心向善可转圜，居家静心修己德，待得否极泰来时"},
    ]},
]

TITLE_MAP = [
    {"min": 90, "titles": [
        "乾卦·飞龙在天", "离卦·赤乌破晓", "震卦·雷动九霄", "巽卦·风行天下",
    ]},
    {"min": 75, "titles": [
        "兑卦·金泽滋润", "艮卦·山岳稳固", "坤卦·厚德载物", "坎卦·水善利万",
    ]},
    {"min": 60, "titles": [
        "泰卦·天地交泰", "既济·水火相济", "恒卦·雷风恒久", "谦卦·地山谦逊",
    ]},
    {"min": 40, "titles": [
        "蹇卦·水山蹇难", "困卦·泽水困厄", "解卦·雷水待解", "未济·火水未济",
    ]},
    {"min": 0,  "titles": [
        "剥卦·山地剥落", "否卦·天地否塞", "蒙卦·山水初蒙", "坎卦·重水险陷",
    ]},
]

THEMES = [
    {"name": "秋叶",  "bg": (253,249,243), "primary": (164, 52, 34), "tag_bg": (156, 59, 36), "tag_text": (255,255,255), "card_bg": (255,255,255), "card_border": (245,222,179), "advice_bg": (255,248,231), "advice_border": (242,199,142), "star_fill": (231, 93, 41)},
    {"name": "樱花",  "bg": (255,240,245), "primary": (209, 73,107), "tag_bg": (209, 73,107), "tag_text": (255,255,255), "card_bg": (255,255,255), "card_border": (245,198,203), "advice_bg": (255,245,247), "advice_border": (245,198,203), "star_fill": (240, 98,146)},
    {"name": "冰雪",  "bg": (240,248,255), "primary": ( 59,107,158), "tag_bg": ( 59,107,158), "tag_text": (255,255,255), "card_bg": (255,255,255), "card_border": (184,218,255), "advice_bg": (245,250,255), "advice_border": (184,218,255), "star_fill": ( 92,146,209)},
    {"name": "森系",  "bg": (244,251,238), "primary": ( 74,122, 60), "tag_bg": ( 74,122, 60), "tag_text": (255,255,255), "card_bg": (255,255,255), "card_border": (195,230,203), "advice_bg": (249,252,245), "advice_border": (195,230,203), "star_fill": (124,179, 66)},
    {"name": "星空",  "bg": (248,244,255), "primary": (107, 74,158), "tag_bg": (107, 74,158), "tag_text": (255,255,255), "card_bg": (255,255,255), "card_border": (214,195,230), "advice_bg": (252,250,255), "advice_border": (214,195,230), "star_fill": (156, 39,176)},
]

IMG_WIDTH = 540
SSAA = 2

sv_jrys = SV("今日运势", priority=5000)


def _str_hash(s: str) -> int:
    h = 0
    for c in s:
        h = (((h << 5) - h) + ord(c)) & 0xFFFFFFFF
    if h >= 0x80000000:
        h -= 0x100000000
    return abs(h)


def _generate_fortune_data(user_id: str, date_str: str) -> dict:
    seed = _str_hash(f"{user_id}-{date_str}")

    weights = []
    total = 0
    for entry in FORTUNE_DATA:
        s = entry["score"]
        if s >= 80:
            w = 40
        elif s >= 60:
            w = 30
        elif s >= 40:
            w = 10
        else:
            w = 2
        weights.append(w)
        total += w

    rand_val = seed % total
    picked = FORTUNE_DATA[0]
    for i, entry in enumerate(FORTUNE_DATA):
        if rand_val < weights[i]:
            picked = entry
            break
        rand_val -= weights[i]

    fortune = picked["items"][(seed >> 2) % len(picked["items"])]
    luck_score: int = picked["score"]

    title_arr = next(m["titles"] for m in TITLE_MAP if luck_score >= m["min"])
    main_title: str = title_arr[(seed >> 3) % len(title_arr)]
    star_count: int = min(10, max(0, round(luck_score / 10)))

    categories = [
        {"name": "财运", "score": seed % 4},
        {"name": "机缘", "score": (seed >> 1) % 4},
        {"name": "事业", "score": (seed >> 2) % 4},
        {"name": "人品", "score": (seed >> 3) % 4},
    ]

    poem_lines = _split_poem(fortune["desc"])
    theme = THEMES[seed % len(THEMES)]

    return {
        "date_str": date_str,
        "luck_score": luck_score,
        "theme": theme,
        "fortune": {
            "main_title": main_title,
            "star_count": star_count,
            "poem": poem_lines,
            "advice": fortune["advice"],
            "categories": categories,
        },
    }


def _split_poem(desc: str) -> List[List[str]]:
    """将四句爻辞拆成 [[行1左, 行1右], [行2左, 行2右]] 两列两行结构。
    desc 格式：句1，句2，句3，句4（逗号分隔四句）。
    """
    parts = [p.strip() for p in re.split(r"[，,]", desc) if p.strip()]
    while len(parts) < 4:
        parts.append("静待机缘时至")
    return [[parts[0], parts[1]], [parts[2], parts[3]]]


def _get_cache_path(user_id: str) -> Path:
    return CACHE_PATH / f"{user_id}.json"


def _load_cache(user_id: str) -> Optional[dict]:
    p = _get_cache_path(user_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_cache(user_id: str, data: dict) -> None:
    _get_cache_path(user_id).write_text(
        json.dumps(data, ensure_ascii=False), encoding="utf-8"
    )


def _get_background() -> Optional[Image.Image]:
    files = [
        f for f in BG_IMAGE_PATH.iterdir()
        if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ]
    if not files:
        return None
    try:
        return Image.open(random.choice(files)).convert("RGBA")
    except Exception as e:
        logger.warning(f"[JRYS] 读取背景图失败: {e}")
        return None


def F(size: int):
    return core_font(size)


def _rrect(draw: ImageDraw.ImageDraw, xy: Tuple, r: int,
           fill: Tuple, outline: Optional[Tuple] = None, lw: int = 1):
    draw.rounded_rectangle(list(xy), radius=r, fill=fill,
                            outline=outline, width=lw)


def _tw(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]
    except Exception:
        return len(text) * font.size


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> List[str]:
    lines: List[str] = []
    for para in text.split("\n"):
        cur = ""
        for ch in para:
            test = cur + ch
            if _tw(draw, test, font) <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = ch
        if cur:
            lines.append(cur)
    return lines or [""]


def _rounded_avatar(avatar: Image.Image, size: int, radius: int) -> Image.Image:
    avatar = avatar.resize((size, size), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size, size], radius=radius, fill=255)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(avatar, (0, 0), mask)
    return result


def _make_header_bg(bg_img: Image.Image, W: int, H: int, bg_color: Tuple) -> Image.Image:
    bw, bh = bg_img.size
    scale = max(W / bw, H / bh)
    resized = bg_img.resize((int(bw * scale), int(bh * scale)), Image.LANCZOS)
    cx = (resized.width - W) // 2
    cropped = resized.crop((cx, 0, cx + W, H)).convert("RGBA")

    mask = Image.new("L", (W, H), 255)
    md = ImageDraw.Draw(mask)
    fade_start = int(H * 0.55)
    for row in range(fade_start, H):
        a = int(255 * (1.0 - (row - fade_start) / max(H - fade_start, 1)))
        md.line([(0, row), (W, row)], fill=a)

    base = Image.new("RGBA", (W, H), tuple(bg_color) + (255,))
    base.paste(cropped, (0, 0), mask)
    return base


async def _draw_card(theme: dict, data: dict, nickname: str, user_id: str,
                     is_got: bool, is_gaiming: bool, today_md: str,
                     bg_img: Optional[Image.Image],
                     bot_name: str = "命运") -> Image.Image:
    S   = SSAA
    W   = IMG_WIDTH * S
    PAD = 24 * S
    GAP = 12 * S

    bg_color:    Tuple = tuple(theme["bg"])
    primary:     Tuple = tuple(theme["primary"])
    card_bg:     Tuple = tuple(theme["card_bg"])
    card_border: Tuple = tuple(theme["card_border"])
    advice_bg:   Tuple = tuple(theme["advice_bg"])
    advice_bdr:  Tuple = tuple(theme["advice_border"])
    star_fill:   Tuple = tuple(theme["star_fill"])
    tag_bg:      Tuple = tuple(theme["tag_bg"])
    tag_text:    Tuple = tuple(theme["tag_text"])

    fortune  = data["fortune"]
    HEADER_H = 260 * S

    canvas_h = 2400
    img = Image.new("RGBA", (W, canvas_h), bg_color + (255,))
    draw = ImageDraw.Draw(img)

    if bg_img:
        header = _make_header_bg(bg_img, W, HEADER_H, bg_color)
        img.paste(header, (0, 0))

    NAV_Y  = 24 * S
    fn_nav = F(18 * S)
    if is_gaiming:
        tag_str = "☆ ❀ 逆天改命·成功"
    elif is_got:
        tag_str = "☆ ❀ 今日运势·已获取"
    else:
        tag_str = "☆ ❀ 今日运势"

    tag_tw     = _tw(draw, tag_str, fn_nav)
    tag_pill_w = tag_tw + 32 * S
    _rrect(draw, (PAD, NAV_Y, PAD + tag_pill_w, NAV_Y + 36 * S), 18 * S,
           fill=card_bg + (215,))
    draw.text((PAD + 16 * S, NAV_Y + 18 * S), tag_str, font=fn_nav,
              fill=primary + (255,), anchor="lm")
    draw.text((W - PAD, NAV_Y + 18 * S), today_md, font=fn_nav,
              fill=(255, 255, 255, 210), anchor="rm")

    y          = HEADER_H - 52 * S
    AVATAR_SZ  = 72 * S
    AV_RADIUS  = 16 * S
    CARD_H     = 104 * S
    _rrect(draw, (PAD, y, W - PAD, y + CARD_H), 20 * S, fill=card_bg + (255,))

    av_x = PAD + 16 * S
    av_y = y + (CARD_H - AVATAR_SZ) // 2
    try:
        avatar_raw = await get_qq_avatar(user_id)
        rnd_av     = _rounded_avatar(avatar_raw, AVATAR_SZ, AV_RADIUS)
        img.alpha_composite(rnd_av, (av_x, av_y))
        draw.rounded_rectangle(
            [av_x - 2 * S, av_y - 2 * S,
             av_x + AVATAR_SZ + 2 * S, av_y + AVATAR_SZ + 2 * S],
            radius=AV_RADIUS + 2 * S, outline=card_border + (255,), width=3 * S)
    except Exception as e:
        logger.warning(f"[JRYS] 头像获取失败: {e}")
        _rrect(draw, (av_x, av_y, av_x + AVATAR_SZ, av_y + AVATAR_SZ),
               AV_RADIUS, fill=advice_bdr + (255,), outline=card_border + (255,), lw=2 * S)
        draw.text((av_x + AVATAR_SZ // 2, av_y + AVATAR_SZ // 2),
                  "?", font=F(30 * S), fill=primary + (200,), anchor="mm")

    fn_name  = F(24 * S)
    fn_stag  = F(14 * S)
    name_x   = av_x + AVATAR_SZ + 18 * S
    name_y   = y + 24 * S
    nick_str = nickname if len(nickname) <= 10 else nickname[:9] + "…"
    draw.text((name_x, name_y), nick_str, font=fn_name,
              fill=(25, 25, 25, 255), anchor="lt")

    if is_gaiming:
        stag, stag_bg, stag_fg = "逆天改命成功！", tag_bg, tag_text
    elif is_got:
        stag, stag_bg, stag_fg = "今日已获取", advice_bg, primary
    else:
        stag, stag_bg, stag_fg = "的今日运势", tag_bg, tag_text

    stag_tw = _tw(draw, stag, fn_stag)
    stag_y  = name_y + 38 * S
    _rrect(draw, (name_x, stag_y, name_x + stag_tw + 22 * S, stag_y + 24 * S), 12 * S,
           fill=stag_bg + (255,))
    draw.text((name_x + 11 * S, stag_y + 12 * S), stag, font=fn_stag,
              fill=stag_fg + (255,), anchor="lm")

    y += CARD_H + GAP + 4 * S

    draw.text((W // 2, y + 26 * S), fortune["main_title"], font=F(38 * S),
              fill=primary + (255,), anchor="mm")
    y += 56 * S

    fn_star    = F(26 * S)
    star_count = fortune["star_count"]
    STAR_GAP   = 10 * S
    star_bb    = draw.textbbox((0, 0), "★", font=fn_star)
    star_w     = star_bb[2] - star_bb[0]
    stars_w    = 10 * star_w + 9 * STAR_GAP
    sx         = (W - stars_w) // 2
    for i in range(10):
        ch    = "★" if i < star_count else "☆"
        color = star_fill + (255,) if i < star_count else (195, 192, 188, 255)
        draw.text((sx + i * (star_w + STAR_GAP), y), ch,
                  font=fn_star, fill=color, anchor="lt")
    y += star_bb[3] - star_bb[1] + GAP + 4 * S

    fn_poem   = F(19 * S)
    poem_rows = fortune["poem"]   # [[左1, 右1], [左2, 右2]]
    ROW_H     = 42 * S
    POEM_PV   = 26 * S
    poem_h    = POEM_PV * 2 + len(poem_rows) * ROW_H
    _rrect(draw, (PAD, y, W - PAD, y + poem_h), 18 * S,
           fill=card_bg + (255,), outline=card_border + (200,), lw=1 * S)
    draw.text((PAD + 16 * S, y + 6 * S), "\u201c", font=F(56 * S),
              fill=card_border + (180,), anchor="lt")
    draw.text((W - PAD - 12 * S, y + poem_h - 6 * S), "\u201d", font=F(56 * S),
              fill=card_border + (180,), anchor="rb")
    mid_x = W // 2
    sep_top    = y + POEM_PV + ROW_H // 4
    sep_bottom = y + poem_h - POEM_PV - ROW_H // 4
    draw.line([(mid_x, sep_top), (mid_x, sep_bottom)],
              fill=card_border + (120,), width=1 * S)
    for ri, (left, right) in enumerate(poem_rows):
        row_cy = y + POEM_PV + ri * ROW_H + ROW_H // 2
        draw.text((PAD + (mid_x - PAD) // 2, row_cy),
                  left, font=fn_poem, fill=(50, 55, 72, 255), anchor="mm")
        draw.text((mid_x + (W - PAD - mid_x) // 2, row_cy),
                  right, font=fn_poem, fill=(50, 55, 72, 255), anchor="mm")
    y += poem_h + GAP

    fn_cat = F(16 * S)
    CATS_H = 90 * S
    _rrect(draw, (PAD, y, W - PAD, y + CATS_H), 18 * S, fill=card_bg + (255,))
    COL_W     = (W - PAD * 2) // 4
    BAR_SEG_W = 36 * S
    SEG_GAP   = 6 * S
    BAR_H     = 10 * S
    BAR_TOTAL = 3 * BAR_SEG_W + 2 * SEG_GAP
    for i, cat in enumerate(fortune["categories"]):
        cx_ = PAD + i * COL_W + COL_W // 2
        draw.text((cx_, y + 20 * S), cat["name"], font=fn_cat,
                  fill=(95, 95, 100, 255), anchor="mm")
        score = max(1, min(3, cat["score"]))
        bx    = cx_ - BAR_TOTAL // 2
        for j in range(3):
            bx_j  = bx + j * (BAR_SEG_W + SEG_GAP)
            bfill = primary + (255,) if j < score else (220, 222, 226, 255)
            draw.rounded_rectangle(
                [bx_j, y + 56 * S, bx_j + BAR_SEG_W, y + 56 * S + BAR_H],
                radius=5 * S, fill=bfill)
    y += CATS_H + GAP

    fn_adv    = F(16 * S)
    ICON_W    = 32 * S
    adv_body  = fortune["advice"] + "~"
    adv_full  = f"{bot_name}：{adv_body}"
    adv_max   = W - PAD * 2 - 20 * S * 2 - ICON_W
    adv_lines = _wrap_text(draw, adv_full, fn_adv, adv_max)
    ADV_PV    = 18 * S
    ADV_LH    = 26 * S
    adv_h     = ADV_PV * 2 + len(adv_lines) * ADV_LH
    _rrect(draw, (PAD, y, W - PAD, y + adv_h), 18 * S,
           fill=advice_bg + (255,), outline=advice_bdr + (200,), lw=2 * S)
    draw.text((PAD + 16 * S, y + adv_h // 2), "✨", font=F(20 * S),
              fill=(255, 195, 0, 255), anchor="lm")
    for li, ln in enumerate(adv_lines):
        draw.text((PAD + 16 * S + ICON_W, y + ADV_PV + li * ADV_LH),
                  ln, font=fn_adv, fill=(55, 55, 60, 255), anchor="lt")
    y += adv_h + GAP

    fn_hint = F(14 * S)
    if is_got:
        hint = "🌿 今日已获取过运势了哦，运势不佳可尝试「逆天改命」"
        draw.text((W // 2, y + 16 * S), hint, font=fn_hint,
                  fill=primary + (185,), anchor="mm")
        y += 36 * S

    draw.text((W // 2, y + 18 * S), "仅供娱乐  ·  相信科学  ·  请勿迷信",
              font=F(13 * S), fill=(175, 175, 178, 255), anchor="mm")
    y += 44 * S

    final_h = y
    return img.crop((0, 0, W, final_h)).resize(
        (IMG_WIDTH, final_h // S), Image.LANCZOS
    )


@sv_jrys.on_command(("今日运势", "运势", "jrys"))
async def cmd_jrys(bot: Bot, ev: Event):
    user_id  = str(ev.user_id)
    date_str = datetime.now().strftime("%Y/%m/%d")
    today_md = datetime.now().strftime("%m/%d")
    nickname = ev.sender.get("nickname", user_id) if ev.sender else user_id
    bot_name = JRYSConfig.get_config("BotName").data or "命运"

    cache = _load_cache(user_id)
    is_got = False
    if cache and cache.get("date_str") == date_str and cache.get("fortune"):
        data = cache
        is_got = True
    else:
        data = _generate_fortune_data(user_id, date_str)
        _save_cache(user_id, data)

    bg = _get_background()
    img = await _draw_card(data["theme"], data, nickname, user_id,
                     is_got=is_got, is_gaiming=False, today_md=today_md,
                     bg_img=bg, bot_name=bot_name)
    await bot.send(await convert_img(img))


@sv_jrys.on_command(("悔签", "重新抽取运势"))
async def cmd_huiqian(bot: Bot, ev: Event):
    user_id  = str(ev.user_id)
    date_str = datetime.now().strftime("%Y/%m/%d")
    today_md = datetime.now().strftime("%m/%d")
    nickname = ev.sender.get("nickname", user_id) if ev.sender else user_id
    bot_name = JRYSConfig.get_config("BotName").data or "命运"

    cache = _load_cache(user_id)
    if cache and cache.get("date_str") == date_str and cache.get("is_huiqian"):
        await bot.send("今天已经悔过签了，不能太贪心哦~")
        return

    data = _generate_fortune_data(user_id + "-huiqian", date_str)
    data["is_huiqian"] = True
    _save_cache(user_id, data)

    await bot.send("异象骤生，运势竟然改变了……")
    bg = _get_background()
    img = await _draw_card(data["theme"], data, nickname, user_id,
                     is_got=True, is_gaiming=False, today_md=today_md,
                     bg_img=bg, bot_name=bot_name)
    await bot.send(await convert_img(img))


@sv_jrys.on_command(("逆天改命", "改命", "nitiangaiming"))
async def cmd_gaiming(bot: Bot, ev: Event):
    user_id  = str(ev.user_id)
    date_str = datetime.now().strftime("%Y/%m/%d")
    today_md = datetime.now().strftime("%m/%d")
    nickname = ev.sender.get("nickname", user_id) if ev.sender else user_id
    bot_name = JRYSConfig.get_config("BotName").data or "命运"

    masters: list = core_config.get_config("masters")
    is_master = user_id in masters

    cache = _load_cache(user_id)
    if not cache or cache.get("date_str") != date_str or not cache.get("fortune"):
        await bot.send("你今日尚未起卦，请先发送「运势」获取今日运势，再来挑战改命之术~")
        return

    gaiming_count = cache.get("gaiming_count", 0)

    if not is_master and gaiming_count >= 2:
        await bot.send(f"今日改命之力已耗尽（已用 {gaiming_count}/2 次），天道难违，明日再试吧~")
        return

    if not is_master:
        roll = random.randint(1, 100)
        if roll <= 20:
            fail_msgs = [
                f"天机不可强求……改命失败了（掷骰：{roll}，需>20），命运之轮纹丝未动。",
                f"逆天之举，遭天道反噬！（掷骰：{roll}）改命失败，运势未变，再接再厉~",
                f"星象混沌，改命受阻（掷骰：{roll}）……或许这就是你今日的宿命？",
                f"紫微星黯淡，改命落空（掷骰：{roll}），但次数已消耗，请珍惜最后机会！",
            ]
            cache["gaiming_count"] = gaiming_count + 1
            _save_cache(user_id, cache)
            await bot.send(random.choice(fail_msgs))
            return

    seed_str = f"{user_id}-{date_str}-gaiming{gaiming_count + 1}-{int(datetime.now().timestamp())}"
    new_seed = _str_hash(seed_str)
    bias_roll = (new_seed % 100) + 1

    if bias_roll <= 70:
        good_entries = [e for e in FORTUNE_DATA if e["score"] >= 60]
        picked = good_entries[new_seed % len(good_entries)]
        fortune_item = picked["items"][(new_seed >> 2) % len(picked["items"])]
        luck_score = picked["score"]
        title_arr = next(m["titles"] for m in TITLE_MAP if luck_score >= m["min"])
        new_data: dict = {
            "date_str": date_str,
            "luck_score": luck_score,
            "theme": THEMES[new_seed % len(THEMES)],
            "fortune": {
                "main_title": title_arr[(new_seed >> 3) % len(title_arr)],
                "star_count": min(10, max(0, round(luck_score / 10))),
                "poem": _split_poem(fortune_item["desc"]),
                "advice": fortune_item["advice"],
                "categories": [
                    {"name": "财运", "score": new_seed % 4},
                    {"name": "机缘", "score": (new_seed >> 1) % 4},
                    {"name": "事业", "score": (new_seed >> 2) % 4},
                    {"name": "人品", "score": (new_seed >> 3) % 4},
                ],
            },
        }
    else:
        new_data = _generate_fortune_data(f"{user_id}-gaiming{int(datetime.now().timestamp())}", date_str)

    if not is_master:
        new_data["gaiming_count"] = gaiming_count + 1
    else:
        new_data["gaiming_count"] = gaiming_count
    _save_cache(user_id, new_data)

    bg = _get_background()
    img = await _draw_card(new_data["theme"], new_data, nickname, user_id,
                     is_got=True, is_gaiming=True, today_md=today_md,
                     bg_img=bg, bot_name=bot_name)
    await bot.send(await convert_img(img))


@sv_jrys.on_command(("jrysn", "随机背景", "随机运势图"))
async def cmd_jrysn(bot: Bot, _ev: Event):
    bg = _get_background()
    if not bg:
        await bot.send("获取背景图失败，请在 JRYS/bg/ 目录下放置图片后重试！")
        return
    W, target_h = IMG_WIDTH, 380
    bw, bh = bg.size
    scale = max(W / bw, target_h / bh)
    resized = bg.resize((int(bw * scale), int(bh * scale)), Image.LANCZOS)
    cx = (resized.width - W) // 2
    preview = resized.crop((cx, 0, cx + W, target_h)).convert("RGBA")
    draw = ImageDraw.Draw(preview)
    draw.text((W - 18, target_h - 18), "背景预览", font=F(18),
              fill=(255, 255, 255, 190), anchor="rb")
    await bot.send(await convert_img(preview))
