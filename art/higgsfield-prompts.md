# Stormglass Keep - art prompts for Higgsfield

First-pass static art. Generate the style sheet first, then attach it as an image
reference to every other generation so the set stays consistent.

Suggested model: **Nano Banana Pro** (or GPT Image 2 at high quality), 2k resolution.

## How to deliver

Download each result as PNG and name it exactly as in the tables below, or leave them in
your Higgsfield history and tell me - I can read the result links from there.

Symbols are generated on a flat magenta background (`#FF00FF`) so the background can be
removed cleanly afterwards. Do not ask the model for transparency; it is unreliable.

## Shared style block

Paste this at the end of every prompt:

> Hand-painted digital illustration in the style of a professional 2D mobile game art team: bold simplified shapes, a thick clean dark outline, flat colour areas with two or three hard-edged shading steps, visible confident brush strokes, one clear light source from the upper left, limited palette of deep teal, slate blue, brass and amber. Stylised, not photorealistic. No glossy plastic sheen, no lens flare, no bloom, no sparkles, no particles, no smoke, no excessive fine detail, no ornate filigree, no watermark, no border. No text, no letters, no numbers.

## 1. Style sheet (generate first)

| File | Aspect | Prompt |
|---|---|---|
| `style_sheet.png` | 16:9 | Concept art sheet for a slot game set in a lone lighthouse in a violent storm at night: the lighthouse lantern room with glowing amber lamp, crashing teal waves, lightning in dark clouds, and a row of small item studies below (brass key, anchor, ship's bell, compass, pieces of sea glass, lantern, lightning bolt). + style block |

## 2. Symbols (1:1, each centred, filling about 80% of the frame, flat magenta `#FF00FF` background)

Prefix each with: *"Single slot-game symbol icon, centred, isolated on a flat solid magenta
#FF00FF background, no shadow on the background:"*

| File | Symbol | Prompt |
|---|---|---|
| `h1.png` | Keeper's key (top) | an ornate antique brass lighthouse keeper's key with a glowing amber gem in the bow, gold rim |
| `h2.png` | Anchor | a heavy iron ship's anchor wrapped with wet rope, teal patina, gold rim highlights |
| `h3.png` | Bell | a brass ship's bell on a small bracket, polished with storm reflections |
| `h4.png` | Compass | an open brass navigator's compass with a glowing needle |
| `l1.png` | Sea glass, red | a smooth rounded piece of sea glass, deep ruby red, faceted like a gem |
| `l2.png` | Sea glass, amber | a smooth rounded piece of sea glass, warm amber, teardrop shape |
| `l3.png` | Sea glass, green | a smooth rounded piece of sea glass, emerald green, hexagonal shape |
| `l4.png` | Sea glass, blue | a smooth rounded piece of sea glass, cobalt blue, diamond shape |
| `l5.png` | Sea glass, violet | a smooth rounded piece of sea glass, pale violet, round pebble shape |
| `w.png` | Wild | a jagged bolt of white-gold lightning trapped inside a round glass orb with a brass ring |
| `s.png` | Scatter | a storm lantern with a blazing amber flame, brass frame |

The five sea-glass pieces must differ in **shape as well as colour** so they are readable
at small size and for colour-blind players.

## 3. Backgrounds (no magenta; full scenes)

| File | Aspect | Prompt |
|---|---|---|
| `bg_base_landscape.png` | 16:9 | Night storm seascape seen from a cliff, a tall stone lighthouse on the right third with its amber beam cutting through rain, crashing teal waves, lightning in heavy clouds, the centre of the image kept darker and calmer so a game board can sit over it |
| `bg_base_portrait.png` | 9:16 | Same scene composed vertically, lighthouse rising at the top, waves at the bottom, calm dark centre |
| `bg_bonus_landscape.png` | 16:9 | Inside the lighthouse lantern room at the height of the storm, huge glass lens glowing amber, rain streaming down the windows, lightning outside, calm dark centre |
| `bg_drowned_landscape.png` | 16:9 | The same lantern room sunk deep underwater, lamp extinguished, cold blue-green light filtering down, drifting bubbles and kelp, eerie and quiet, calm dark centre |

## 4. Board frame and logo

| File | Aspect | Prompt |
|---|---|---|
| `frame.png` | 1:1 | A square ornate frame made of riveted brass and weathered iron lighthouse window glazing bars, empty centre, frame only about 6% of the width on each side, isolated on a flat solid magenta #FF00FF background, centre also magenta |
| `logo.png` | 3:2 | Game logo lettering reading exactly "STORMGLASS KEEP", bold cast-brass letters with glass inlays lit from within by amber light, small lightning bolt accent, isolated on a flat solid magenta #FF00FF background (omit the "no text" line of the style block for this one) |

## 5. Game tile (for the Stake Engine tile editor)

Stake rejects tiles with dark edges or text baked in.

| File | Aspect | Prompt |
|---|---|---|
| `tile_background.png` | 3:4 | Bright storm-lit sky and sea, glowing teal and amber clouds lit from behind by lightning, bright all the way to the edges, no dark vignette, no text |
| `tile_foreground.png` | 3:4 | The lighthouse lantern with blazing amber light and a lightning bolt striking it, large and centred, isolated on a flat solid magenta #FF00FF background, no text |

## Checklist before sending

- Symbols: square, object fully inside the frame, magenta background with no gradient.
- No text anywhere except `logo.png`.
- One consistent painting style across all files.
