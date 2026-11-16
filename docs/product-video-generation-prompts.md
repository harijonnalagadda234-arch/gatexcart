# GateXKart product video generation prompts

No product videos are included yet. The homepage poster cards are previews only; do not treat a poster or an absent MP4 path as a playable video. Store approved, optimized H.264 MP4 exports under `static/videos/products/` using the filenames below.

## Shared production requirements

- Create a 15- to 20-second, 16:9 landscape product film at 1920 × 1080, 24 or 30 fps.
- Use photorealistic Indian food-export advertising, natural product textures, clean studio or sourcing light, and restrained forest-green, warm ivory, and gold accents.
- Use smooth, unhurried camera movement, cinematic close-ups, and clean transitions. Keep packaging and labels plausible and free of invented certifications or claims.
- Use only the supplied GateXKart mark at `static/images/gatexkart-mark.svg`. Preserve it exactly; do not redraw, recolor, distort, or substitute it. Show the GateXKart name and the exact tagline “Indian Products. Global Markets.”
- Do not add any other brand, watermark, stock-site mark, or audible narration. Deliver muted/silent playback suitable for autoplay.
- Keep generous negative space for the product title and GateXKart brand lockup. End on a clean product-and-brand frame.

## 1. Pure Ghee — `pure-ghee.mp4`

Create a premium, appetizing film of pure golden ghee. Open on a warm macro shot of ghee slowly pouring from a spoon into a small ceramic bowl; show its smooth sheen and rich natural texture. Cut to a neatly styled bowl beside an unbranded premium jar, then finish with the jar and bowl in soft, warm light. Avoid unsupported purity, health, or certification claims. Add the supplied GateXKart mark, name, and exact tagline in the final frame.

## 2. Red Chilli Powder — `red-chilli-powder.mp4`

Show fresh Indian red chillies in crisp natural light, then a slow-motion cascade of fine red chilli powder into a shallow bowl. Use a macro shot to reveal the powder texture and finish with an export-ready, unbranded pouch or jar beside whole chillies. Keep the red color rich but realistic; do not add heat-level or origin claims that were not supplied. Add the supplied GateXKart mark, name, and exact tagline in the final frame.

## 3. Rice & Grains — `rice-grains.mp4`

Open on a close-up of long-grain Indian rice, with individual grains in sharp focus. Show rice pouring smoothly from a measuring scoop into a clean bowl, followed by a tidy export-quality sack with a neutral, unbranded label. Use soft daylight and warm ivory tones to convey careful handling and consistent grain quality without inventing certifications. Add the supplied GateXKart mark, name, and exact tagline in the final frame.

## 4. Groundnuts — `groundnuts.mp4`

Show fresh groundnuts in their shells, then a careful shelling close-up revealing clean kernels. Transition to peanuts moving through a clean sorting surface and a neutral export-ready sack. Use natural earth tones, precise focus, and calm camera movement; avoid implying a specific grade or laboratory inspection. Add the supplied GateXKart mark, name, and exact tagline in the final frame.

## 5. Cooking Oils — `cooking-oils.mp4`

Show a glossy golden stream of cooking oil pouring into a clear glass vessel, then macro shots of suitable oil seeds and the oil's clean color in backlight. Finish with a neat group of unbranded, sealed cooking-oil bottles. Keep the oil and seed visuals plausible without implying a specific oil type, nutrition benefit, or certification. Add the supplied GateXKart mark, name, and exact tagline in the final frame.

## 6. Indian Masalas & Food Products — `indian-masalas.mp4`

Create a refined overhead-to-macro sequence of turmeric, coriander, cumin, black pepper, and a balanced mixed-spice assortment. Let a few whole spices fall gently into frame, then show ground masalas in clean bowls and neutral export packaging. Preserve each spice's natural color and texture; avoid unsupported origin, purity, or health claims. Add the supplied GateXKart mark, name, and exact tagline in the final frame.

## Playback integration checklist

Only add the video element after the corresponding reviewed MP4 exists. Use the matching poster, `controls`, `muted`, `playsinline`, `loop`, and `preload="none"`; attempt muted autoplay only as a progressive enhancement and leave accessible controls available when autoplay is blocked. Keep a visible poster fallback and test the MP4 response type and size before enabling playback.
