#!/usr/bin/env python3
"""Build the simplified demo pages from the full rebranded ones.

Reads Home/index.html and Product/index.html (made by rebrand.py) and writes
Home/simple.html and Product/simple.html next to them, so asset paths keep working.
Run after rebrand.py:
  python3 tools/rebrand.py && python3 tools/simplify.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEEP_CATEGORIES = ["Bouquets", "Roses"]
CURRENCY = "Rs "
PRICE = "500"

SIMPLE_CSS = """
<style id="fleuriste-simple">
  .fl-hero-img { height: 440px; border-radius: 24px; overflow: hidden; }
  .fl-hero-img img { width: 100%; height: 100%; object-fit: cover; object-position: center 45%; display: block; }
  .gspb_col-id-gsbp-672ffc6 { display: flex; flex-direction: column; justify-content: center; }
  .ct-header [data-row="bottom"] [data-column="end"] { display: none; }
  .ct-header [data-row="bottom"] .ct-container { display: flex; }
  #main-container { min-height: auto; }
  .site-main { padding-bottom: 80px; }
</style>
"""

HERO_IMAGE = '<div class="fl-hero-img"><img src="../images/product-blush-rose.webp" alt="Blush Rose Bouquet"></div>'

FLOWER_ICON = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
               'stroke-linecap="round"><circle cx="12" cy="8" r="2.2"/><path d="M12 5.8c0-2.4 2.8-3.3 3.8-1.6 1 1.7-.6 3.3-1.6 3.6'
               'M12 5.8c0-2.4-2.8-3.3-3.8-1.6-1 1.7.6 3.3 1.6 3.6M14.2 8.4c2 .9 1.8 3.8-.2 4.1-1.4.2-2-.9-2-2.3M9.8 8.4c-2 .9-1.8 3.8.2 4.1'
               ' 1.4.2 2-.9 2-2.3M12 12.5V21M12 17c-1.5-2-3.8-2.3-5-1.8 1 2 3 2.6 5 1.8zM12 15.5c1.5-1.6 3.5-1.8 4.6-1.3-.9 1.7-2.8 2.2-4.6 1.3z"/></svg>')

TAG = re.compile(r"<(/?)([a-zA-Z][\w-]*)\b[^>]*?(/?)>")
VOID = {"img", "br", "input", "meta", "link", "hr", "source", "wbr"}


def element_at(s, start):
    """Return (start, end) of the element whose opening tag begins at `start`."""
    name = TAG.match(s, start).group(2).lower()
    if name in VOID:
        return start, s.index(">", start) + 1
    depth = 0
    for m in TAG.finditer(s, start):
        if m.group(2).lower() != name or m.group(3):
            continue
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return start, m.end()
    raise ValueError(f"unclosed <{name}> at {start}")


def find(s, marker, pos=0):
    """Start index of the tag containing `marker`, or -1."""
    i = s.find(marker, pos)
    return -1 if i < 0 else s.rfind("<", 0, i + 1)


def remove(s, marker, all_=True):
    while (i := find(s, marker)) >= 0:
        a, b = element_at(s, i)
        s = s[:a] + s[b:]
        if not all_:
            break
    return s


def replace_inner(s, marker, html):
    i = find(s, marker)
    a, b = element_at(s, i)
    open_end = s.index(">", a) + 1
    close_start = s.rindex("</", a, b)
    return s[:open_end] + html + s[close_start:]


def keep_children(s, marker, keep):
    """Inside each element matching `marker`, drop direct <li> children for which keep(li_html) is False."""
    pos = 0
    while (i := find(s, marker, pos)) >= 0:
        a, b = element_at(s, i)
        block = s[a:b]
        ul = block.index("<ul")
        ua, ub = element_at(block, ul)
        inner_start = block.index(">", ua) + 1
        inner, out, j = block[inner_start:ub - 5], [], 0
        while (k := inner.find("<li", j)) >= 0:
            la, lb = element_at(inner, k)
            if keep(inner[la:lb]):
                out.append(inner[la:lb])
            j = lb
        block = block[:inner_start] + "\n".join(out) + block[ub - 5:]
        s = s[:a] + block + s[b:]
        pos = a + len(block)
    return s


def is_category(li):
    return any(f"</span>{c}</a>" in li for c in KEEP_CATEGORIES)


def simplify_header(s):
    s = remove(s, 'data-row="top"')                    # top bar: showrooms, gift cards, socials
    s = remove(s, 'data-id="search-input"')
    s = remove(s, 'class="ct-header-account"')
    s = remove(s, 'class="ct-header-wishlist"')
    s = remove(s, 'class="ct-header-compare')
    s = remove(s, 'class="ct-contact-info"')            # address / phone in the category row
    s = remove(s, 'class="ct-header-socials')
    # Main menu: Home only (desktop and mobile)
    s = keep_children(s, 'id="header-menu-1"', lambda li: ">Home</a>" in li)
    s = keep_children(s, 'data-id="mobile-menu"', lambda li: ">Home</a>" in li)
    # Category menu: two categories, no "More" dropdown
    s = keep_children(s, 'id="header-menu-2"', is_category)
    s = keep_children(s, 'data-id="mobile-menu-secondary"', is_category)
    s = re.sub(r'<span class="ct-icon-container ct-left">(?:(?!</span>).)*</span>(%s)</a>' % "|".join(KEEP_CATEGORIES),
               r'<span class="ct-icon-container ct-left">%s</span>\1</a>' % FLOWER_ICON, s, flags=re.S)
    s = re.sub(r'(<nav id="header-menu-[12]"[^>]*?) data-responsive="yes"', r"\1", s)
    s = s.replace('style="height: 140px;"', "")
    return s


def set_prices(s):
    """Rupees everywhere, every product at the same price, no sale markers."""
    sym = '<span class="woocommerce-Price-currencySymbol">'
    s = re.sub(r'<del aria-hidden="true">.*?</del>\s*(<span class="screen-reader-text">[^<]*</span>\s*)*', "", s, flags=re.S)
    s = re.sub(r'<span class="screen-reader-text">(Original|Current) price[^<]*</span>', "", s)
    s = re.sub(r'<span class="onsale"[^>]*>[^<]*</span>', "", s)
    s = s.replace(sym + "$</span>", sym + CURRENCY + "</span>")
    s = re.sub(r'(?<=%s</span>)[\d,.]+(?=</bdi>)' % re.escape(CURRENCY), PRICE, s)
    # the header cart total stays at zero
    s = s.replace(f'<span class="ct-amount"><span class="woocommerce-Price-amount amount"><bdi>{sym}{CURRENCY}</span>{PRICE}',
                  f'<span class="ct-amount"><span class="woocommerce-Price-amount amount"><bdi>{sym}{CURRENCY}</span>0')
    s = re.sub(r'(<div class="fl-addons" data-base=")[\d.]+', r"\g<1>" + PRICE, s)
    s = s.replace("+$", "+" + CURRENCY)
    s = s.replace("return '$' + n.toFixed(2);", f"return '{CURRENCY}' + n.toFixed(0);")
    s = s.replace("</span>' + unit.toFixed(2)", "</span>' + unit.toFixed(0)")
    s = s.replace('"currency":"$"', f'"currency":"{CURRENCY.strip()}"')
    return s


def finish(s):
    s = remove(s, 'id="footer"')
    s = set_prices(s)
    s = s.replace("../Home/index.html", "../Home/simple.html").replace("../Product/index.html", "../Product/simple.html")
    s = s.replace("</head>", SIMPLE_CSS + "</head>", 1)
    return s


def build_home():
    s = (ROOT / "Home/index.html").read_text(encoding="utf-8")
    s = simplify_header(s)

    # Hero: heading, one short line, button; picture side becomes one bouquet photo
    s = remove(s, 'id="gspb_container-id-gsbp-2560b07"')  # florist avatars + "Talk to a florist"
    s = re.sub(r'(<div id="gspb_text-id-gsbp-9f97b67"[^>]*>).*?</div>',
               r"\1Order by 2pm for same-day delivery.</div>", s, count=1, flags=re.S)
    s = replace_inner(s, 'id="gspb_col-id-gsbp-e8ab431"', HERO_IMAGE)
    s = re.sub(r'(<div class="gspb_button_wrapper gspb_button-id-gsbp-06d9be3"[^>]*><a [^>]*?href=")#',
               r"\1../Product/simple.html", s, count=1)

    # Bestsellers: one row of the first product's card, each copy with the photo of a different product
    i = find(s, 'id="gspb_container-id-gsbp-90d01df"')
    a, b = element_at(s, i)
    block = s[a:b]
    ul = block.index('<ul class="products')
    ua, ub = element_at(block, ul)
    per_row = int(re.search(r'columns-(\d+)', block[ua:ub]).group(1))
    items, pos = [], ua
    while len(items) < per_row and (k := block.find('<li class="product type-product', pos, ub)) >= 0:
        la, lb = element_at(block, k)
        items.append(block[la:lb])
        pos = lb
    photo = lambda li: re.search(r'src="(\.\./images/[^"]+)"', li).group(1)
    cards = [items[0].replace(photo(items[0]), photo(li)) for li in items]
    block = block[:block.index(">", ua) + 1] + "".join(cards) + block[ub - 5:]
    s = s[:a] + block + s[b:]

    # Everything after the bestsellers section inside the page content goes
    content = s.index('<div class="entry-content is-layout-constrained">')
    ca, cb = element_at(s, content)
    end_of_best = s.index(block) + len(block)
    s = s[:end_of_best] + s[cb - 6:]

    s = finish(s)
    (ROOT / "Home/simple.html").write_text(s, encoding="utf-8")
    print("Home/simple.html written")


def build_product():
    s = (ROOT / "Product/index.html").read_text(encoding="utf-8")
    s = simplify_header(s)

    for marker in ['class="ct-breadcrumbs"', 'class="woocommerce-product-details__short-description"',
                   'class="ct-product-divider"', 'class="ct-product-additional-actions"',
                   'class="ct-product-brands-single"', 'class="product_meta"', 'class="ct-share-box',
                   'class="woocommerce-tabs', 'class="related products', 'data-block="hook:424"',
                   'class="ct-floating-bar']:
        s = remove(s, marker)

    # Add-ons: bouquet size and delivery only
    for label in ["Add a vase", "Make it extra special", 'for="fl_message"']:
        a, b = element_at(s, s.rfind('<div class="fl-group">', 0, s.index(label)))
        s = s[:a] + s[b:]

    s = finish(s)
    (ROOT / "Product/simple.html").write_text(s, encoding="utf-8")
    print("Product/simple.html written")


if __name__ == "__main__":
    build_home()
    build_product()
