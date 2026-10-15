# Eshal

Video editing workspace for Azlan & Eza's short-form social content.

When the user sends raw video to edit, follow the approved editing style in
`video-style/STYLE.md` and reuse `video-style/build.py` (brand kit, captions,
title, cards, outro). Keep raw footage and renders out of git (`work/` is ignored).

Always keep the TikTok safe zones (user rule): no text or key graphics in the top 150px,
the bottom block below y=1460, or the right action rail (x>940, y 760-1520) of a 1080x1920 frame.
Use `TT_CAPTION_Y` / `TT_CENTER_X` from `video-style/build.py` and check a storyboard with
the zones drawn before rendering. Show a preview before every render, and keep the original
context even if the video ends up over 2 minutes.
