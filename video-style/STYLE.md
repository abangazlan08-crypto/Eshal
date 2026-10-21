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

## TikTok safe zones (required)
TikTok's UI covers parts of a 1080×1920 frame, so text and key graphics must stay out of:
- **Top** y < 150 (For You / Following tabs)
- **Bottom** y > 1460 (caption text, username, sound name, nav bar)
- **Right rail** x > 940 for 760 < y < 1520 (avatar, like, comment, save, share)

Use `fit_pill()` for any pill with long text (it shrinks to the safe width). Use `TT_CAPTION_Y` (1390) for one-word captions and `TT_CENTER_X` for full-screen cards (scaled to about 90%). Put the logo watermark on the left side (about x 95, y 1010), not the bottom-right. Before rendering, check the storyboard with the zones drawn over it (`PREVIEW_tiktok_safezone.jpg`).
Note: videos 1–4 put captions at about 84–88% height, inside the bottom zone. Re-render them if they are reposted.

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

## Videos made in this style
| # | Video | Script |
|---|---|---|
| 1 | PGLS Norway (Munich, hotel entrance) | `build.py` |
| 2 | "Part time masih bekerja" (on the tour bus) | `videos/02_part_time_bus.py` |
| 3 | 3 kelebihan simpan emas konsisten (studio, 1:13, with 2 gold-bar photos) | `videos/03_konsisten_emas.py` |
| 4 | Simpan dulu, baru berseronok (in-car selfie, 1:16, stock music) | `videos/04_simpan_dulu.py` |
| 5 | Jangan simpan duit banyak-banyak dalam bank (studio, 2:05, news photo, stock music) | `videos/05_jangan_simpan_dalam_bank.py` |
| 6 | Kenapa China masih beli emas (studio, 3:07, 2 Reuters/The Edge screenshots, stock music) | `videos/06_kenapa_china_beli_emas.py` |
| 7 | Bonus tahunan dah jadi harta? (in-car, 2:20, cash photo + Public Gold staff photo + BH Online screenshot) | `videos/07_bonus_tahunan.py` |
| 8 | Bila ada duit baru simpan? (studio, 2:58, AI infographic by Eza, slow zoom-ins) | `videos/08_simpan_dulu_baru_belanja.py` |

User rule (video 5): **keeping the original context matters more than the under-2-minute target.** Don't cut a line that carries meaning just to hit 2:00; ask or keep it.
Caption tokens `display~syllables` (e.g. `RM1.99~9`) show numbers compactly while keeping word timing. Music helpers: `music_ss` < 0 delays the track, and `music_tempo` stretches it (atempo, same pitch) so its natural ending lands on the outro.

Music: ask Descript's Agent Underlord to put a stock track alone in a new "Music" composition, publish it as Audio, download it, and pass it to `composite(..., music=...)`. It ducks under the voice (sidechain) and rises on the outro. Make an audio-only preview with `--audio-preview` before rendering. Licensed music files stay out of git.

### Workflow the user asked for on video 3 (use again)
1. Transcribe first (Descript SRT), mark false starts and repeated takes, and cut every pause over about 0.3s (speech-energy regions, ±0.1s padding). Keep the video under 2 minutes.
2. Make the hook strong: start on the first spoken word, with kinetic text building to a gold "slam" word plus a whoosh.
3. Premium grade and relight (see `GRADE` / `RELIGHT` in `03_konsisten_emas.py`): contrast 1.10, warm mids, cool highlights, an S-curve, a soft face key-light mask (`03_assets/facemask.png`), vignette and light sharpening.
4. Place user photos as white-framed cards with a gold shine sweep where the speech matches them.
5. **Show a preview before rendering** (`--preview` makes a storyboard of graded stills with the real overlays, plus a before/after grade comparison). Render only after the user says "render".

For a new video, copy `videos/02_part_time_bus.py`. It imports the shared helpers, outro, SFX and compositing from `build.py`, so only the cut list, cues and graphics change.
Caption timing on noisy audio (e.g. a bus): use Descript's SRT cues and distribute words inside each cue by syllable count.

## How to render
```bash
RAW=/path/to/raw.mp4 OUT=/path/to/out python3 video-style/build.py
python3 video-style/build.py --skip-base   # re-render overlays only after text or graphic tweaks
```
`build.py` is specific to the PGLS Norway clip: its cut list (`SEGS`), word groups (`GROUPS`) and per-segment graphics need updating for each new video. The drawing helpers, caption, title, outro and SFX code are reusable as they are.

Getting word timings: model downloads (Hugging Face, Whisper) are blocked in the cloud sandbox. Get the transcript from Descript (`import_media`, then ask Agent Underlord), then align words to speech-energy regions as `align_words()` does.
Network access needs these allowed domains: `drive.google.com`, `drive.usercontent.google.com`, `media.descriptusercontent.com`, `api.descript.com`. Google Drive file links download through `https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`.


News screenshots: crop out ads, and credit the source shown in the screenshot (e.g. "Sumber: Reuters via The Edge Malaysia, 7 Okt 2026"). On-screen numbers come from the speech; flag any that the screenshot doesn't confirm.

Music choice: avoid tracks with religious titles or a church/choir character (the audience is Muslim). iPhone ProRAW (.DNG) photos open with PIL plus `ImageOps.exif_transpose`. If Descript AI credits run out, reuse an approved track, crossfaded to length.

Slow zoom-in (video 8): `zoom_vf()` / `slow_amt()` add an +8% zoom across a segment (scale with eval=frame, then crop around the face). Use it on emphasis moments. For the preview, send a short low-res demo clip, since stills can't show motion.
