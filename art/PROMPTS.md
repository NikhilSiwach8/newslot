# Infernal Kingdom - art, animation and audio prompt pack

Original visual identity for INFERNAL KINGDOM. Nothing here references an existing game's
artwork. Generated from `art/generate.py` (same prompts); regenerate this file if you edit them.

Copy-ready version (style already merged into every prompt, plus audio prompts): `art/PROMPTS_COPY.md`.

Status: **not generated yet.** The game runs on labelled placeholders from `art/placeholders.py`.
File names match `docs/ASSET_MANIFEST.md`, so final art replaces placeholders one for one.

## How to use

1. Generate the hero symbol (`h1`, the Demon King) first and approve it; attach it as a style reference to every other generation so scale, perspective and lighting stay consistent.
2. Symbols, seals, souls, pacts, crown, frame and logo go on flat magenta `#FF00FF`; `art/process.py` keys it out. Do not ask the model for transparency.
3. Save results to `art/raw/<name>.png`, then run `python3 art/process.py && python3 art/build_game_assets.py`.

## Shared style block (appended to every prompt)

> Premium cinematic 3D casino-game render, dark fantasy: molten gold #D6A04A, blood crimson #A51D24, infernal orange #FF6A00, obsidian #080708 and blackened iron #211A1A, with rare emerald soul light #14B86E and violet magic #923DCE as accents. Physically based materials (forged iron, polished gold, glowing lava, faceted gems), one strong warm key light from the upper left, a cool rim light, crisp silhouette readable at small size, consistent three-quarter front perspective and scale across the set. Original design, not based on any existing game. No watermark, no border.

Every prompt except the logo and the letter symbols also gets: *"No text, no letters, no numbers."*

## Prompts

| File | Size | Prompt |
|---|---|---|
| `h1.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the Demon King, a horned infernal monarch, head and shoulders, obsidian skin with molten cracks, a black iron crown, burning gold eyes, regal and menacing. |
| `h2.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: an Infernal Dragon head in molten armour plates, lava glowing between the scales, jaws open with ember breath. |
| `h3.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a Cursed Crown of black iron with jagged spikes and burning crimson gemstones. |
| `h4.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a golden Blood Chalice with engraved runes, swirling red magical energy rising from the cup. |
| `h5.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a cursed gold Soul Ring holding a large emerald with a trapped glowing soul inside. |
| `l1.png` | 1024x1024 | Single slot-game card symbol, centred, filling about 75 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the capital letter A in a heavy engraved serif, crimson enamel with a molten gold edge. |
| `l2.png` | 1024x1024 | Single slot-game card symbol, centred, filling about 75 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the capital letter K in a heavy engraved serif, polished gold with dark engraving. |
| `l3.png` | 1024x1024 | Single slot-game card symbol, centred, filling about 75 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the capital letter Q in a heavy engraved serif, emerald enamel with a gold edge. |
| `l4.png` | 1024x1024 | Single slot-game card symbol, centred, filling about 75 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the capital letter J in a heavy engraved serif, brushed silver with dark engraving. |
| `l5.png` | 1024x1024 | Single slot-game card symbol, centred, filling about 75 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the number 10 in a heavy engraved serif, aged bronze with dark engraving. |
| `w.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the Infernal Wild: the Demon King's burning crown emblem on a black iron shield edged with molten gold, flames rising behind. |
| `hs.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the Hellstar: a five-pointed star forged from blackened iron with a white-hot molten core and orange flame points. |
| `s.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the Hell Gate scatter: a gothic infernal portal arch of obsidian with violet fire swirling inside. |
| `wb.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the Wild Bomb: a round black iron bomb bound with gold bands, a burning fuse, cracks leaking orange light. |
| `gb.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the Golden Wild Bomb: a larger ornate bomb of polished molten gold with crimson gems and a blazing fuse. |
| `sp.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the Split Symbol: a cracked obsidian rune tablet splitting into two halves with gold light pouring from the crack. |
| `do.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the Demon Overlord: the Demon King in full figure, wings spread, mid-transformation into a pillar of flame. |
| `seal_wrath.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a round infernal seal medallion of blackened iron and gold, the sigil of WRATH engraved at its centre, unlit. |
| `seal_greed.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a round infernal seal medallion of blackened iron and gold, the sigil of GREED engraved at its centre, unlit. |
| `seal_envy.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a round infernal seal medallion of blackened iron and gold, the sigil of ENVY engraved at its centre, unlit. |
| `seal_pride.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a round infernal seal medallion of blackened iron and gold, the sigil of PRIDE engraved at its centre, unlit. |
| `seal_lust.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a round infernal seal medallion of blackened iron and gold, the sigil of LUST engraved at its centre, unlit. |
| `seal_sloth.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a round infernal seal medallion of blackened iron and gold, the sigil of SLOTH engraved at its centre, unlit. |
| `seal_gluttony.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a round infernal seal medallion of blackened iron and gold, the sigil of GLUTTONY engraved at its centre, unlit. |
| `seal_despair.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a round infernal seal medallion of blackened iron and gold, the sigil of DESPAIR engraved at its centre, unlit. |
| `seal_dominion.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a round infernal seal medallion of blackened iron and gold, the sigil of DOMINION engraved at its centre, unlit. |
| `soul_wrath.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a glowing soul gem, crimson, a faint ghostly face inside, gold claw setting. |
| `soul_greed.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a glowing soul gem, gold, a faint ghostly face inside, gold claw setting. |
| `soul_envy.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a glowing soul gem, emerald, a faint ghostly face inside, gold claw setting. |
| `soul_pride.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a glowing soul gem, violet, a faint ghostly face inside, gold claw setting. |
| `soul_lust.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a glowing soul gem, magenta, a faint ghostly face inside, gold claw setting. |
| `soul_sloth.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a glowing soul gem, deep blue, a faint ghostly face inside, gold claw setting. |
| `soul_gluttony.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: a glowing soul gem, orange, a faint ghostly face inside, gold claw setting. |
| `apocalypse_crown.png` | 1024x1024 | Single slot-game symbol, centred, filling about 80 percent of the frame, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background: the Apocalypse Crown: the Demon King's crown reforged in white-gold fire, seven coloured soul gems set around it. |
| `pact_blood.png` | 1024x1536 | An infernal contract scroll, crimson parchment, molten weapons crossed above it, glowing crimson runes, a wax seal of blood, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background. |
| `pact_soul.png` | 1024x1536 | An infernal contract scroll, golden parchment, emerald soul crystals above it, green magical runes, an emerald wax seal, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background. |
| `bg_base_landscape.png` | 1536x1024 | A gigantic infernal fortress on a volcanic plain, rivers of lava, volcanic mountains, demonic statues and burning chains, smoke and embers. Keep the centre of the image darker and calmer so a 6 by 4 reel set can sit over it. |
| `bg_base_portrait.png` | 1024x1536 | A gigantic infernal fortress seen from below, rivers of lava at the bottom, volcanic mountains, demonic statues and burning chains. Keep the centre of the image darker and calmer so a 6 by 4 reel set can sit over it. |
| `bg_bonus_landscape.png` | 1536x1024 | Inside the Demon King's throne hall, an obsidian throne, emerald soul flames in braziers, gold and iron pillars. Keep the centre of the image darker and calmer so a 6 by 4 reel set can sit over it. |
| `bg_takeover_landscape.png` | 1536x1024 | The infernal fortress engulfed in crimson light, the sky turned red, the huge silhouette of the Demon King rising behind it. Keep the centre of the image darker and calmer so a 6 by 4 reel set can sit over it. |
| `frame.png` | 1024x1024 | A square slot reel frame of blackened iron with molten-gold borders and engraved infernal runes, thin (about 6 percent of the width on each side), touching the image edges, the large empty centre flat solid magenta #FF00FF, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background. |
| `logo.png` | 1536x1024 | Game logo lettering reading exactly "INFERNAL KINGDOM" on two lines, forged molten-gold letters with blackened iron edges, small flames, a horned crown above, isolated on a perfectly flat solid magenta #FF00FF background with no gradient and no shadow on the background. |

## Animation briefs (Spine or sprite sheets; all presentation only)

Animations must never delay or alter the result: the book already holds it. Turbo must shorten all of them.

| Animation | Trigger (book event) | Brief |
|---|---|---|
| Reel spin | `reveal` | Symbols fall in reel by reel with a heavy iron thud; ember trails. |
| Cascade | `tumbleBoard` | Winning symbols burn to ash from the edges inward; survivors drop with weight; new symbols fall through a heat shimmer. |
| Symbol win | `winInfo` | Per-symbol loop: Demon King eyes ignite, Dragon exhales embers, Crown gems flare, Chalice overflows, Ring soul pulses; letters glint. |
| Wild landing / multiplier | wild lands | Crown emblem slams down; multiplier tag forged on the corner in gold. |
| Wild Bomb | `specialResolve` wildBomb | Fuse burns down, 2x2 orange shockwave, cells flip to wilds. |
| Golden Wild Bomb | `specialResolve` goldenWildBomb | Slower, bigger gold detonation over 3x3, molten-gold rain, distinct from the Wild Bomb. |
| Split Symbol | `specialResolve` split | Rune tablet cracks, light pours out, the new symbol appears doubled with a '2x' brand. |
| Demon Overlord | `specialResolve` overlord | Demon King rises on his reel, wings unfold into a wild column, multiplier spreads to every wild. |
| Hell Seal lights | `sealLit` | The seal's sigil ignites from the centre outward; line glow when a pattern completes. |
| Hellfire / Soul Harvest / Cataclysm | `sealPattern` | Hellfire: a reel engulfed in fire turns wild. Harvest: symbols drawn into the seal board as souls. Cataclysm: reels shatter and collapse. |
| Infernal Takeover | `infernalTakeover` | Background bleeds to crimson, the Demon King looms behind the reels, two reels crack and burn into wild reels. |
| Demon's Bargain | `demonsBargain` | Two contracts unroll; the chosen one is sealed in wax, the other burns. |
| Soul collection | `soulCollected` | Orb leaves its symbol and flies into its slot on the Seven Souls meter; shards crackle. |
| Soul Apocalypse | `soulApocalypse` | Reels freeze and darken; seven souls orbit the crown; it becomes the Apocalypse Crown; white-gold fire floods two or three reels. |
| Maximum win | `wincap` | Full-screen molten-gold 66,666x with the Demon King and tagline RULE BEYOND THE FLAMES. |

## Audio brief

Infernal ambience, heavy metal impacts, magical energy, demonic vocal textures, cinematic orchestral layers. The current build plays the Stake Web SDK sample sounds, which may not ship.

| Sound | Brief |
|---|---|
| `bgm_main` | Slow, heavy orchestral loop with low choir and distant drums, seamless 60-90 s. |
| `bgm_freespin` | Faster, brass and choir, metal guitar undertone; seamless loop. |
| `bgm_takeover` | Short crimson sting into a pounding loop under the Takeover. |
| `bgm_apocalypse` | Rising choir and organ to a held climax. |
| `sfx_reel_stop` | Iron slab landing, short. |
| `sfx_cascade` | Ash burn + crumble. |
| `sfx_win_small` / `_big` / `_max` | Gold coins on stone, escalating with orchestral hits; max win with demonic laugh layer. |
| `sfx_wild_land`, `sfx_bomb`, `sfx_golden_bomb`, `sfx_split`, `sfx_overlord` | Distinct impacts per special; golden bomb larger and brighter. |
| `sfx_seal_<name>` | One sigil ignition per seal, shared base with a tonal variation each. |
| `sfx_soul_collect`, `sfx_shard` | Ghostly whoosh into a chime; shard is a glassy crack. |
| `vo_demon_king_*` | Short demonic vocal textures (no words needed) for Takeover, Bargain and Apocalypse. |
