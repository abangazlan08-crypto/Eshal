# Azlan & Eza — short-form video editing style

Approved by the user on 2026-10-11 ("Love it! Remember the editing style.").
First video made in this style: **PGLS Norway** (Malay motivational talking-head, 21s).
Use this style for every new raw clip unless the user asks for something different.

## Reference
Modelled on a TikTok motion-graphics video by @itsnotoriously that the user supplied.
Feel: fast and clean, with a visual change every 2–4 seconds, bold rounded type, floating cards and a dark branded outro.

## Format
- Vertical 9:16, 1080×1920, 30 fps, H.264 CRF 19, AAC 160k, loudness normalised to -14 LUFS.
- Horizontal 4K source: crop 9:16 around the face. Don't upscale from 1080p if 4K is available.
- Mild grade: contrast 1.05, saturation 1.12.

## Edit
- Remove fillers ("aa", "um", a trailing "okey") and dead air. Keep about 0.1s of padding and 30ms audio fades at every cut.
- Alternate normal framing with a 107% punch-in on each cut, plus a faint white flash at the cut.
- Keep all meaningful content and never change what is said.

## Brand kit
| Item | Value |
|---|---|
| Logo | `assets/logo.png` ("AZLAN & EZA", red brush AE). On dark backgrounds the black text is recoloured white. |
| Brand red | `#B01E30` |
| Khaki | `#D6D29A` |
| Caption gold | `#F7E4A0` |
| Dark background | `#0E1020` (navy) |
| Glitch accents | cyan `#25F4EE`, pink `#FE2C55` |
| Font | Poppins ExtraBold / Bold (`assets/fonts`) |
| Outro handle | "Azlan & Eza" (the user hasn't given a social handle yet) |

## Graphic elements
1. **Kinetic title (first ~2s, top of frame):** two lines, slightly rotated. Line 1 is brand red with a white outline; line 2 is white and offset right and lower. Bounce-in. Built from words the speaker actually says (e.g. "PGLS / NORWAY").
2. **One-word captions:** one word at a time, synced to speech. Poppins ExtraBold about 104px (auto-shrinks to fit 900px), white-to-gold gradient, dark outline and soft shadow. Placed low (about 87% of the frame height) so the face stays clear, with a quick pop-in scale for each word. Keep the speaker's spelling (Malay plus English mix). Lowercase, except acronyms.
3. **Pop-in cards** in the clear band above the head, never over the face. White pills with icons such as a location pin, a flag, a calendar or a green tick. Keyword ticks appear exactly when each word is spoken. Use stat or progress cards (dark navy with a red-to-gold bar) for ideas like "matter of time".
4. **Cutaway:** a full-screen crumpled-paper background with a dark rounded card (e.g. an animated route map with a plane flying along a dotted path) while the voice continues. Ease in with a zoom and fade, then cut back.
5. **Fun props:** e.g. boarding passes and an "x2" sticker on "double tiket".
6. **Logo watermark:** small, bottom right, 90% opacity.
7. **Outro (3.5s):** navy background, logo bounce-in with a cyan/pink glitch, a search-bar pill (name plus a red "Follow" button) with cyan/pink offset edges, then fade to black.
8. **Sound:** a soft pop on each card, a whoosh on the cutaway and the outro. Add background music only if the user supplies or approves a track.

## Rules
- Never invent claims, numbers, dates or places. On-screen text comes only from what is said or what the user confirms.
- Facts confirmed by the user: the event is **PGLS** (not "PJNS"), and the trip is **Malaysia → Norway** (not from Munich).
- Flag uncertain transcript words to the user (e.g. "pulas", names) instead of guessing.

## How to render
```bash
RAW=/path/to/raw.mp4 OUT=/path/to/out python3 video-style/build.py
python3 video-style/build.py --skip-base   # re-render overlays only after text or graphic tweaks
```
`build.py` is specific to the PGLS Norway clip: its cut list (`SEGS`), word groups (`GROUPS`) and per-segment graphics need updating for each new video. The drawing helpers, caption, title, outro and SFX code are reusable as they are.

Getting word timings: model downloads (Hugging Face, Whisper) are blocked in the cloud sandbox. Get the transcript from Descript (`import_media`, then ask Agent Underlord), then align words to speech-energy regions as `align_words()` does.
Network access needs these allowed domains: `drive.google.com`, `drive.usercontent.google.com`, `media.descriptusercontent.com`, `api.descript.com`. Google Drive file links download through `https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`.
