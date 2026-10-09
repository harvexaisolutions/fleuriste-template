#!/usr/bin/env python3
"""Rebrand the saved Blocksy "Furniture" starter pages into a floral shop demo.

Reads the untouched pages from _original/ and writes:
  Home/index.html
  Product/index.html

Photos are picked up from images/<slot>.(jpg|jpeg|png|webp). Any slot without a
file keeps the original template image, so this can be re-run as photos arrive:

  python3 tools/rebrand.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
BRAND = "Fleuriste"
EXTS = (".jpg", ".jpeg", ".png", ".webp")
REMOTE = "https://startersites.io/blocksy/furniture"
PRODUCT_PAGE = "../Product/index.html"
HOME_PAGE = "../Home/index.html"

PALETTE = {
    "#274C4F": "#9E4F63",  # primary (buttons, links)
    "#456A6D": "#C27489",  # primary hover
    "#42504b": "#5B4A4E",  # body text
    "#152420": "#2B1D21",  # headings
    "#E2EDEF": "#EBDCDD",  # borders
    "#EEF4F5": "#F6EDEE",  # soft section background
    "#FBFCFC": "#FCF8F8",  # light background
}

# Old category label -> new label (menus, breadcrumbs, footer)
CATEGORIES = {
    "Armchairs": "Bouquets",
    "Chairs": "Roses",
    "Storage": "Plants",
    "Sofas": "Seasonal",
    "Beds": "Luxury",
    "Tables": "Sympathy",
    "Decor": "Gifts",
}

# old name -> (new name, category, {old price: new price})
PRODUCTS = {
    # Home: bestsellers
    "Aliquam Blandit": ("Blush Rose Bouquet", "Bouquets", {"320.00": "89.00"}),
    "Augue Lacus": ("Peach Garden Roses", "Luxury", {"800.00": "129.00"}),
    "Augue Mauris": ("White Hydrangea Kraft Bouquet", "Bouquets", {"85.00": "75.00"}),
    "Bibendum Arcu": ("Lilac Tulip Bouquet", "Seasonal", {"65.00": "59.00", "40.00": "45.00"}),
    "Commodo Amcorper": ("Wild Garden Arrangement", "Luxury", {"1,250.00": "195.00"}),
    "Diam Arcu": ("Red Aster Bottle Posy", "Seasonal", {"450.00": "45.00", "380.00": "39.00"}),
    "Diam Volutpat": ("Dried Flower Posy", "Gifts", {"250.00": "39.00"}),
    "Dolore Magna": ("Purple Carnation Posy", "Bouquets", {"1,000.00": "35.00"}),
    # Home: top selling
    "Massa Scelerisque": ("White Rose Tribute", "Sympathy", {"790.00": "110.00"}),
    "Sem Integer": ("Eucalyptus in Ceramic Jug", "Plants", {"280.00": "65.00", "200.00": "49.00"}),
    "Lectus Proin": ("Baby&#039;s Breath Noir Bouquet", "Luxury", {"680.00": "85.00", "600.00": "69.00"}),
    "Mollis Nunc": ("White Blossom Dome", "Seasonal", {"750.00": "58.00"}),
    # Product page: related
    "Quis Commodo": ("Peach Garden Roses", "Luxury", {"120.00": "129.00"}),
    "Tempor Commodo": ("Lilac Tulip Bouquet", "Seasonal", {"125.00": "59.00", "99.00": "45.00"}),
    "Turpis Cursus": ("White Hydrangea Kraft Bouquet", "Bouquets", {"320.00": "75.00"}),
    "Semper Auctor": ("Build Your Own Bouquet", "Bouquets", {"950.00": "45.00"}),
}
MAIN_PRODUCT = ("Eleifend Donec", "Blush Rose Bouquet", "580.00", "89.00")
MAIN_SLOT = "product-blush-rose"

# original image base name -> images/ slot name (fallback slot optional)
IMAGE_SLOTS = {
    "home-hero-image-1": ["hero-main"],
    "home-hero-image-2": ["hero-secondary"],
    "home-avatar-1": ["avatar-1"],
    "home-avatar-2": ["avatar-2"],
    "home-avatar-3": ["avatar-3"],
    "product-35": [MAIN_SLOT],
    "product-37": ["product-peach-garden-roses"],
    "product-10": ["product-white-hydrangea"],
    "product-3": ["product-lilac-tulips"],
    "product-41": ["product-wild-garden"],
    "product-7": ["product-red-aster"],
    "product-25": ["product-dried-posy"],
    "product-43": ["product-purple-carnation"],
    "product-32": ["product-white-rose-tribute"],
    "product-30": ["product-eucalyptus-jug"],
    "product-31": ["product-babys-breath-noir"],
    "product-29": ["product-white-blossom-dome"],
    "browse-by-rooms-image-1-1": ["occasion-birthday"],
    "browse-by-rooms-image-2-1": ["occasion-anniversary"],
    "browse-by-rooms-image-3": ["occasion-sympathy"],
    "browse-by-rooms-image-4-1": ["occasion-get-well"],
    "offers-image-1": ["offer-mothers-day"],
    "offers-image-3": ["offer-subscription"],
    "offers-image-2": ["offer-birthday-bundle"],
    "home-mask-image": ["about-florist"],
    "subscribe-section-image": ["subscribe-cutout"],
    "product-17": [MAIN_SLOT],
    # Extra gallery angles; slides without their own photo are removed (see trim_gallery).
    "product-17_2": [f"{MAIN_SLOT}-2"],
    "product-17_3": [f"{MAIN_SLOT}-3"],
    "product-17_4": [f"{MAIN_SLOT}-4"],
    "product-17_5": [f"{MAIN_SLOT}-5"],
    "product-17_6": [f"{MAIN_SLOT}-6"],
    "product-2": ["product-peach-garden-roses"],
    "product-1": ["product-lilac-tulips"],
    "product-16": ["product-white-hydrangea"],
    "product-21": ["product-build-your-own"],
}

COMMON_TEXT = [
    (">Showrooms<", ">Our Studio<"),
    (">Custom Work<", ">Weddings &amp; Events<"),
    (">Variable Product<", ">All Bouquets<"),
    (">Product Gallery<", ">Same-Day Delivery<"),
    (">Advanced Reviews<", ">Flower Subscriptions<"),
    (">Custom Tab<", ">Corporate Flowers<"),
    (">Related Products – Slider<", ">Gift Hampers<"),
    (">News<", ">Journal<"),
    (">Design Services<", ">Wedding Flowers<"),
    (">Delivery<", ">Delivery Areas<"),
    (">Important updates waiting for you!<", ">Join our flower club<"),
    (">Subscribe and grab 20% OFF!<", ">Subscribe and get 15% off your first bouquet.<"),
    (">Lorem ipsum dolor sit amet consectetur.<",
     ">Questions about an order or a custom arrangement? Our florists are happy to help.<"),
    ("9AM - 5PM / 10AM - 3PM", "Mon–Sat 8AM - 6PM / Sun 9AM - 1PM"),
    (">CreativeThemes<", f">{BRAND}<"),
]

HOME_TEXT = [
    ("<title>Furniture</title>", f"<title>{BRAND} – Fresh Flowers Delivered</title>"),
    (">Exquisite design combined with functionalities<", ">Fresh flowers, hand-tied and delivered today<"),
    (">Pellentesque ullamcorper dignissim condimentum volutpat consequat mauris nunc lacinia quis.<",
     ">Seasonal bouquets arranged by our florists every morning. Order by 2pm for same-day delivery across the city.<"),
    (">Contact with our expert<", ">Talk to a florist<"),
    (">Wooden Chair<", ">Today's market picks<"),
    (">$199<", ">From $35<"),
    (">Pretium Elite<", ">Meet our florists<"),
    (">$130<", ">Custom orders welcome<"),
    (">25% OFF<", ">15% OFF<"),  # hero badge (first occurrence)
    (">Donec ac odio tempor dapibus.<", ">On your first order with code BLOOM15.<"),
    (">Quam elementum pulvinar etiam non quam. Faucibus nisl tincidunt eget nullam non nisi elementum sagittis vitae et leo duis ut diam quam.<",
     ">Our most-loved arrangements this week, hand-tied fresh and ready for delivery today.<"),
    (">Browse by rooms<", ">Shop by occasion<"),
    (">Sit massa etiam urna id. Non pulvinar aenean ultrices lectus vitae imperdiet vulputate a eu. Aliquet ullamcorper leo mi vel sit pretium euismod eget.<",
     ">From birthdays to heartfelt goodbyes, find the right flowers for every moment.<"),
    (">Living Room<", ">Birthday<"),
    (">15 products<", ">32 bouquets<"),
    (">Bedroom<", ">Love &amp; Anniversary<"),
    (">24 products<", ">27 bouquets<"),
    (">Walk-in Closet<", ">Sympathy<"),
    (">30 products<", ">18 arrangements<"),
    (">Kitchen<", ">Get Well Soon<"),
    (">24 products<", ">15 bouquets<"),
    (">Top selling furniture<", ">Top selling arrangements<"),
    (">Quam elementum pulvinar etiam non quam. Faucibus nisl tincidunt eget nullam non nisi elementum sagittis vitae et leo duis ut diam quam.<",
     ">Customer favourites, from classic red roses to long-lasting plants.<"),
    (">Quam elementum pulvinar etiam non quam tincidunt eget nullam non.<",
     ">Seasonal savings on bouquets, subscriptions and gift bundles.<"),
    (">Special Discount<", ">Mother's Day Pre-order<"),
    (">30% OFF<", ">20% OFF<"),
    (">Aliquet sagittis purus faucibus egestas.<", ">Reserve early and save on all Mother's Day bouquets.<"),
    (">Weekly Discount<", ">Flower Subscription<"),
    (">25% OFF<", ">25% OFF<"),
    (">Nulla facilisi cras fermentum odio feugiat.<", ">Fresh blooms delivered weekly, fortnightly or monthly.<"),
    (">Birthday Discount<", ">Birthday Bundle<"),
    (">40% OFF<", ">15% OFF<"),
    (">Porta non pulvinar neque laoreet suspendisse.<", ">Add chocolates and a balloon to any bouquet and save.<"),
    (">Luxurious Furniture Starts with the Best Quality Materials<", ">Every Bouquet Starts with the Freshest Blooms<"),
    (">Donec et odio pellentesque diam volutpat commodo amet consectetur adipiscing elit ut aliquam purus vitae et leo duis ut diam quam nulla porttitor. Sodales ut eu sem integer vitae justo eget magna.<",
     ">We source directly from local growers and trusted flower farms, condition every stem by hand and arrange each order on the morning it is delivered. If your flowers don't last 7 days, we'll replace them.<"),
]

PRODUCT_TEXT = [
    ("<title>Eleifend Donec – Furniture</title>", f"<title>Blush Rose Bouquet – {BRAND}</title>"),
    ("<p>Egestas egestas fringilla phasellus faucibus scelerisque eleifend donec pretium. Duis ut diam quam nulla. Aliquet lectus proin nibh nisl condimentum id venenatis. Mauris nunc congue nisi vitae suscipit. Augue interdum velit euismod in pellentesque massa placerat duis.</p>",
     "<p>A soft, romantic bouquet of pink garden roses, white waxflower and golden solidago, wrapped in ivory tissue and finished with a ribbon. Arranged by our florists on the morning of delivery.</p>"),
    ("<p>Porttitor massa id neque aliquam vestibulum morbi blandit cursus risus.</p>",
     "<p>Rose varieties change with the season. We always match the palette and size, with blooms of equal or greater value.</p>"),
    ("<p>Sit amet nulla facilisi morbi tempus iaculis. Phasellus vestibulum lorem sed risus ultricies tristique.</p>",
     "<p><strong>Flower care</strong></p>"),
    ("<p>Urna neque viverra justo nec ultrices dui sapien eget mi. Dignissim sodales ut eu sem integer vitae justo. Porttitor lacus luctus accumsan tortor posuere ac ut. Amet luctus venenatis lectus magna fringilla urna. At erat pellentesque adipiscing commodo elit at imperdiet dui.</p>",
     "<p>Trim 2cm from each stem at an angle and place in a clean vase with fresh water and the flower food provided. Keep away from direct sunlight, heaters and ripening fruit.</p>"),
    ("<p>Quis varius quam quisque id. Facilisis gravida neque convallis a cras semper auctor neque vitae. Proin sagittis nisl rhoncus mattis rhoncus urna neque viverra. Dolor magna eget est lorem ipsum. Integer quis auctor elit sed vulputate mi sit amet mauris.</p>",
     "<p>Change the water every two days and re-trim the stems. Roses open fully within 2–3 days of delivery.</p>"),
    ('scope="row">Color<', 'scope="row">Colour palette<'),
    ("<p>Orange</p>", "<p>Blush pink, ivory, gold</p>"),
    ('scope="row">Material<', 'scope="row">Flowers<'),
    ("<p>Leather</p>", "<p>Garden roses, waxflower, solidago</p>"),
    (">Size Guide<", ">Bouquet Sizes<"),
    (">Free Shipping<", ">Same-Day Delivery<"),
    (">Gifts &amp; Sales<", ">Freshness Guarantee<"),
    (">Gifts & Sales<", ">Freshness Guarantee<"),
    (">24/7 Support<", ">Real Florists<"),
    (">Tellus gravida ipsum aut facilisis tempus at et aliquam estsem.<",
     ">Pay safely with all major cards, Apple Pay and Google Pay.<"),
    (">Non pulvinar aenean ultrices lectus vitae imperdiet vulputate a eu.<",
     ">Order before 2pm for delivery the same day across the city.<"),
    (">Aliquet ullamcorper leo mi vel sit pretium euismod eget libero.<",
     ">Every bouquet is guaranteed to stay fresh for at least 7 days.<"),
    (">Nullam iaculis vestibulum arcu id urnain pellentesque volutpat quis.<",
     ">Talk to our florists about custom and event arrangements.<"),
]

ADDONS = [
    # (group, label, price, image slot)
    ("size", "Classic", 0, None),
    ("size", "Deluxe", 30, None),
    ("size", "Grand", 60, None),
    ("vase", "No vase", 0, None),
    ("vase", "Glass vase", 15, "addon-vase-glass"),
    ("vase", "Ceramic vase", 25, "addon-vase-ceramic"),
    ("extra", "Chocolates", 12, "addon-chocolates"),
    ("extra", "Teddy bear", 18, "addon-teddy"),
    ("extra", "Balloon", 8, "addon-balloon"),
    ("extra", "Scented candle", 22, "addon-candle"),
]

EXTRA_HEAD = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&display=swap" rel="stylesheet">
<style id="fleuriste-overrides">
:root:root {
  --theme-palette-color-1: #9E4F63 !important; --theme-palette-color-2: #C27489 !important;
  --theme-palette-color-3: #5B4A4E !important; --theme-palette-color-4: #2B1D21 !important;
  --theme-palette-color-5: #EBDCDD !important; --theme-palette-color-6: #F6EDEE !important;
  --theme-palette-color-7: #FCF8F8 !important; --theme-palette-color-8: #ffffff !important;
}
.ct-product-brands-single { display: none !important; }
h1, h2, h3, h4, h5, h6, .woocommerce-loop-product__title, .product_title {
  font-family: "Cormorant Garamond", Georgia, "Times New Roman", serif !important;
  letter-spacing: 0.01em;
}
.fl-logo {
  font-family: "Cormorant Garamond", Georgia, serif;
  font-size: 30px; font-weight: 600; font-style: italic;
  color: var(--theme-palette-color-4); line-height: 1; white-space: nowrap;
}
.fl-logo b { color: var(--theme-palette-color-1); font-weight: 600; }
img[src*="subscribe-cutout"] { filter: invert(1); mix-blend-mode: screen; opacity: .85; }
.altEmail_container, .wpa_hidden_field { display: none !important; }
</style>
"""

ADDON_CSS = """
<style id="fleuriste-addons-css">
.fl-addons { margin: 0 0 24px; display: grid; gap: 20px; }
.fl-group > .fl-label { display: block; font-weight: 600; margin-bottom: 8px; color: var(--theme-palette-color-4); }
.fl-label small { font-weight: 400; color: var(--theme-palette-color-3); }
.fl-opts { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 10px; }
.fl-opt { position: relative; cursor: pointer; }
.fl-opt input { position: absolute; opacity: 0; pointer-events: none; }
.fl-opt span {
  display: flex; flex-direction: column; align-items: center; gap: 6px; height: 100%;
  padding: 10px 8px; border: 1px solid var(--theme-palette-color-5); border-radius: 12px;
  background: #fff; text-align: center; font-size: 14px; line-height: 1.3; transition: border-color .15s, box-shadow .15s;
}
.fl-opt span img { width: 56px; height: 56px; object-fit: cover; border-radius: 8px; }
.fl-opt em { font-style: normal; font-size: 13px; color: var(--theme-palette-color-1); }
.fl-opt input:checked + span { border-color: var(--theme-palette-color-1); box-shadow: 0 0 0 1px var(--theme-palette-color-1); background: var(--theme-palette-color-7); }
.fl-opt input:focus-visible + span { outline: 2px solid var(--theme-palette-color-2); outline-offset: 2px; }
.fl-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
@media (max-width: 480px) { .fl-row { grid-template-columns: 1fr; } }
.fl-addons textarea, .fl-addons input[type=date], .fl-addons select { width: 100%; }
.fl-addons textarea { min-height: 90px; }
.fl-count { display: block; text-align: right; font-size: 12px; color: var(--theme-palette-color-3); margin-top: 4px; }
.fl-check { display: flex; gap: 8px; align-items: center; margin-top: 8px; font-size: 14px; }
.fl-total {
  display: flex; justify-content: space-between; align-items: baseline;
  padding: 14px 16px; border-radius: 12px; background: var(--theme-palette-color-6);
  font-weight: 600; color: var(--theme-palette-color-4);
}
.fl-total strong { font-size: 20px; color: var(--theme-palette-color-1); }
</style>
"""

ADDON_JS = """
<script id="fleuriste-addons-js">
(function () {
  var box = document.querySelector('.fl-addons');
  if (!box) return;
  var form = box.closest('form');
  var base = parseFloat(box.dataset.base);
  var fmt = function (n) { return '$' + n.toFixed(2); };
  var date = box.querySelector('input[type=date]');
  var d = new Date(); var pad = function (n) { return String(n).padStart(2, '0'); };
  date.min = date.value = d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
  var msg = box.querySelector('textarea'), count = box.querySelector('.fl-count');
  function update() {
    var unit = base;
    box.querySelectorAll('input[data-price]:checked').forEach(function (i) { unit += parseFloat(i.dataset.price); });
    var sel = box.querySelector('select option:checked');
    if (sel) unit += parseFloat(sel.dataset.price || 0);
    var qty = parseInt((form.querySelector('input.qty') || {}).value, 10) || 1;
    box.querySelector('.fl-total strong').textContent = fmt(unit * qty);
    document.querySelectorAll('.summary .price .amount bdi, .ct-floating-bar .price .amount bdi').forEach(function (el) {
      el.innerHTML = '<span class="woocommerce-Price-currencySymbol">$</span>' + unit.toFixed(2);
    });
    if (msg && count) count.textContent = msg.value.length + ' / ' + msg.maxLength;
  }
  form.addEventListener('change', update);
  form.addEventListener('input', update);
  form.addEventListener('click', function () { setTimeout(update, 0); });
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  update();
})();
</script>
"""


def image_for(slots):
    for slot in slots:
        for ext in EXTS:
            if (IMAGES / f"{slot}{ext}").exists():
                return f"../images/{slot}{ext}"
    return None


def replace_once(s, old, new):
    if old not in s:
        print(f"  ! not found: {old[:70]}")
        return s
    return s.replace(old, new, 1)


def swap_images(s):
    s = re.sub(r'\s(?:data-)?srcset="[^"]*"', "", s)
    s = re.sub(r'\ssizes="[^"]*"', "", s)
    used = 0
    for base, slots in IMAGE_SLOTS.items():
        new = image_for(slots)
        if not new:
            continue
        b = re.escape(base)
        pat = (r'(?:\./[^"\'()]*?_files/|https://startersites\.io/blocksy/furniture/wp-content/uploads/\d{4}/\d{2}/)'
               + b + r'(?:-\d+x\d+)?\.webp')
        s, n = re.subn(pat, new, s)
        used += n > 0
    return s, used


def rebrand_products(s):
    # Each product card starts with <li class="product ...> (grids) or <div class="product ...> (related
    # slider); edit names/prices/categories per card.
    parts = re.split(r'(?=<(?:li|div) class="product type-product )', s)
    for i, part in enumerate(parts):
        for old, (name, cat, prices) in PRODUCTS.items():
            if f'alt="{old}"' not in part:
                continue
            for op, np in prices.items():
                part = re.sub(r'(?<=</span>)' + re.escape(op) + r'(?=</bdi>)', np, part)
                part = part.replace(f"${op}.", f"${np}.")
            part = re.sub(r'(rel="tag"[^>]*>)[^<]+(</a>)', r'\g<1>' + cat + r'\2', part, count=1)
            parts[i] = part
            break
    s = "".join(parts)
    for old, (name, _, _) in PRODUCTS.items():
        s = s.replace(old, name)
    return s


def common(s):
    for old, new in PALETTE.items():
        s = re.sub(re.escape(old), new, s, flags=re.I)
    s = re.sub(r'<svg[^>]*class="[^"]*default-logo[^"]*"[^>]*>.*?</svg>',
               f'<span class="fl-logo">Fleur<b>iste</b></span>', s, flags=re.S)
    for old, new in COMMON_TEXT:
        s = s.replace(old, new)
    for old, new in CATEGORIES.items():
        s = s.replace(f">{old}<", f">{new}<").replace(f'"name">{old}', f'"name">{new}')
    s = s.replace("</head>", EXTRA_HEAD + "</head>", 1)
    # Point links at the local demo pages; neutralise everything else on the furniture demo.
    s = re.sub(rf'href="{REMOTE}/product/[^"]*"', f'href="{PRODUCT_PAGE}"', s)
    s = re.sub(rf'href="{REMOTE}/"', f'href="{HOME_PAGE}"', s)
    s = re.sub(rf'(<a\b[^>]*?)href="{REMOTE}/[^"]*"', r'\1href="#"', s)
    return s


def addons_html():
    def opt(group, label, price, slot, kind):
        img = image_for([slot]) if slot else None
        img_tag = f'<img src="{img}" alt="">' if img else ""
        price_tag = f"<em>+${price}</em>" if price else "<em>Included</em>"
        checked = " checked" if kind == "radio" and price == 0 else ""
        return (f'<label class="fl-opt"><input type="{kind}" name="fl_{group}{"[]" if kind == "checkbox" else ""}" '
                f'value="{label}" data-price="{price}"{checked}><span>{img_tag}{label}{price_tag}</span></label>')

    def group(key, kind):
        return "".join(opt(*a, kind) for a in ADDONS if a[0] == key)

    return f"""
<div class="fl-addons" data-base="{MAIN_PRODUCT[3]}">
  <div class="fl-group"><span class="fl-label">Bouquet size</span>
    <div class="fl-opts">{group("size", "radio")}</div></div>
  <div class="fl-group"><span class="fl-label">Add a vase</span>
    <div class="fl-opts">{group("vase", "radio")}</div></div>
  <div class="fl-group"><span class="fl-label">Make it extra special <small>(optional)</small></span>
    <div class="fl-opts">{group("extra", "checkbox")}</div></div>
  <div class="fl-group"><span class="fl-label">Delivery</span>
    <div class="fl-row">
      <input type="date" name="fl_delivery_date" aria-label="Delivery date">
      <select name="fl_delivery_slot" aria-label="Delivery time">
        <option data-price="0">Anytime (9am – 7pm)</option>
        <option data-price="0">Morning (9am – 12pm)</option>
        <option data-price="0">Afternoon (12pm – 4pm)</option>
        <option data-price="10">Evening (4pm – 7pm) +$10</option>
      </select>
    </div></div>
  <div class="fl-group"><label class="fl-label" for="fl_message">Gift card message <small>(free)</small></label>
    <textarea id="fl_message" name="fl_message" maxlength="200" placeholder="Write your message, we'll handwrite it on our card"></textarea>
    <span class="fl-count"></span>
    <label class="fl-check"><input type="checkbox" name="fl_anonymous"> Send anonymously</label></div>
  <div class="fl-total"><span>Total</span><strong></strong></div>
</div>
"""


def trim_gallery(s):
    """Drop gallery slides (and their thumbnails) that have no photo of their own."""
    kept = 1
    for n in range(2, 7):
        if image_for([f"{MAIN_SLOT}-{n}"]):
            kept += 1
            continue
        s = re.sub(r'<div class="flexy-item"><figure class="ct-media-container" data-src="[^"]*product-17_%d\.webp".*?</figure></div>' % n, "", s, flags=re.S)
        s = re.sub(r'<li><span class="ct-media-container" aria-label="Slide %d">.*?</span></li>' % n, "", s, flags=re.S)
    if kept == 1:
        s = s.replace("</head>", "<style>.woocommerce-product-gallery .flexy-pills, .woocommerce-product-gallery .flexy-arrow-prev, .woocommerce-product-gallery .flexy-arrow-next { display: none !important; }</style></head>", 1)
    return s


def build_home():
    s = (ROOT / "_original/home.html").read_text(encoding="utf-8")
    s = rebrand_products(s)
    for old, new in HOME_TEXT:
        s = replace_once(s, old, new)
    s = common(s)
    s, n = swap_images(s)
    (ROOT / "Home/index.html").write_text(s, encoding="utf-8")
    print(f"Home/index.html written ({n} image slots filled)")


def build_product():
    s = (ROOT / "_original/product.html").read_text(encoding="utf-8")
    old, name, op, np = MAIN_PRODUCT
    s = re.sub(r'(?<=</span>)' + re.escape(op) + r'(?=</bdi>)', np, s)
    s = rebrand_products(s)
    for o, n in PRODUCT_TEXT:
        s = s.replace(o, n)
    s = re.sub(re.escape(old) + r'(?! – Furniture_files)', name, s)  # keep asset folder paths intact
    s = common(s)
    s = trim_gallery(s)
    s = re.sub(r'<span class="posted_in">Brand:.*?</span>', '', s)
    s = replace_once(s, '<div class="ct-cart-actions">', addons_html() + '<div class="ct-cart-actions">')
    s = s.replace("</head>", ADDON_CSS + "</head>", 1)
    s = s.replace("</body>", ADDON_JS + "</body>", 1)
    s, n = swap_images(s)
    (ROOT / "Product/index.html").write_text(s, encoding="utf-8")
    print(f"Product/index.html written ({n} image slots filled)")


if __name__ == "__main__":
    build_home()
    build_product()
