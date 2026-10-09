# Image list

**How images work now:** downloaded photos go in `images/originals/`. `tools/prepare_images.py` lists which photo fills each slot and how it's cropped. To swap a photo, edit that list, then run:

    python3 tools/prepare_images.py && python3 tools/rebrand.py && python3 tools/simplify.py

The last step rebuilds the simple pages (`Home/simple.html`, `Product/simple.html`) from the full ones.

Product names now follow the photos. The main product is **Blush Rose Bouquet** (slot `product-blush-rose`), and the per-product slot names are in `tools/prepare_images.py`. The sizes and style notes below still apply. To add gallery angles to the product page, add `product-blush-rose-2` … `-6`; slides without a photo are hidden.

Use the same style for all product photos. Each bouquet should be centred and fill about 70% of the frame, on a plain off-white or very light grey background, with no props.

## Home page

| File name | Size (px) | What to show |
|---|---|---|
| hero-main | 900 × 1600 (tall) | Florist or bouquet lifestyle shot, e.g. hands holding a peony bouquet. Keep the subject in the lower two-thirds because a label sits at the top. |
| hero-secondary | 900 × 900 | Small rose posy on a soft pastel background |
| avatar-1, avatar-2, avatar-3 | 96 × 96 | Florist headshots (optional) |
| product-blush-peony | 1000 × 1000 | Blush peonies, roses and eucalyptus in kraft wrap |
| product-grand-rose-box | 1000 × 1000 | Roses packed in a luxury hat box |
| product-sunflower-sunshine | 1000 × 1000 | Sunflower bouquet |
| product-tulip-medley | 1000 × 1000 | Mixed tulips |
| product-signature-luxe | 1000 × 1000 | Large premium mixed arrangement |
| product-spring-garden-basket | 1000 × 1000 | Spring flowers in a basket |
| product-chocolates-roses-gift | 1000 × 1000 | Roses with a box of chocolates |
| product-orchid-elegance | 1000 × 1000 | White orchid in a pot |
| product-white-lily-wreath | 1000 × 1000 | White lily sympathy wreath |
| product-peace-lily | 1000 × 1000 | Peace lily plant in a pot |
| product-dozen-red-roses | 1000 × 1000 | A dozen red roses |
| product-lavender-eucalyptus | 1000 × 1000 | Lavender and eucalyptus bundle |
| occasion-birthday | 1200 × 940 (landscape) | Bright birthday bouquet scene |
| occasion-anniversary | 1200 × 590 (wide) | Romantic roses scene |
| occasion-sympathy | 800 × 800 | Calm white flowers |
| occasion-get-well | 800 × 800 | Cheerful yellow flowers |
| offer-mothers-day | 800 × 1200 (portrait) | Pink bouquet |
| offer-subscription | 800 × 1200 (portrait) | Fresh weekly flowers on a table |
| offer-birthday-bundle | 800 × 1200 (portrait) | Bouquet with a balloon and chocolates |
| about-florist | 1380 × 1050 | Florist arranging flowers in a studio. The template crops this into rounded panels, so leave space around the subject. |
| subscribe-cutout | 340 × 384, **transparent PNG** | Cut-out of a flower vase or small bouquet |

## Product page

| File name | Size (px) | What to show |
|---|---|---|
| product-blush-peony-2 … -6 | 1600 × 1600 | Up to 5 extra angles or close-ups of the blush peony bouquet. Any missing angle repeats the main photo. |
| product-pastel-rose-posy | 1000 × 1000 | Pastel rose posy |
| product-pink-hydrangea | 1000 × 1000 | Pink hydrangea bouquet |
| product-ranunculus-romance | 1000 × 1000 | Ranunculus bouquet |
| product-build-your-own | 1000 × 1000 | Loose mixed stems |
| addon-vase-glass | 300 × 300 | Clear glass vase |
| addon-vase-ceramic | 300 × 300 | Ceramic vase |
| addon-chocolates | 300 × 300 | Box of chocolates |
| addon-teddy | 300 × 300 | Teddy bear |
| addon-balloon | 300 × 300 | Foil balloon |
| addon-candle | 300 × 300 | Scented candle |

The `product-blush-peony` photo also appears as the main product image. Upload it at 1600 × 1600 so it stays sharp when zoomed.
