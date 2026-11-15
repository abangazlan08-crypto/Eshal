# Golf Scorecard (offline app)

A phone app that runs fully offline in the browser and can be added to the home screen. Everything is stored on the device.

## What it does
- **Rounds**: pick or type the course name, the date and the players, then fill in a virtual scorecard (par, stroke index and scores). Every box can be edited, and finished rounds can be edited too.
- **Snap the scorecard**: take a photo or upload one, and the app reads the boxes on the device (Tesseract OCR is bundled in `vendor/`, so it needs no internet). You then check each row it found, choose whether it's par, index or a player, and it fills the card. Boxes filled from the photo are yellow until you check them. The photo stays with the round.
- **Handicap**:
  - Each player has a handicap on record, and it is filled in automatically for every new round.
  - Before a game you can change it for that game only, or tick the box to save it as the new handicap.
  - When a round is finished, the handicap adjusts automatically. It uses WHS score differentials (net double bogey, course rating and slope), and with 3 or more rounds it takes the best N of the last 20. Before that, it blends the starting handicap with the rounds played.
  - You can switch auto-adjust off for each player.
- **Drives & putts**: for each hole, tap the drive box to cycle F (fairway), R (rough), H (hazard); par 3s are skipped. Type putts per hole. The round summary shows fairways, rough, hazard, putts and greens in regulation, and each player page shows fairway %, putts per 18, GIR % and 3-putts. Can be switched off.
- **Courses** are remembered: name, tee, par, stroke index, rating and slope.
- **Backup**:
  - Save or share a `.json` backup file, with or without photos.
  - Restore it on another phone with **Merge** or **Replace**.
  - The app also keeps daily restore points for the last 10 days it was used.
  - It reminds you if your last backup is more than 2 weeks old.

## Running it
It must be served over **https** (or `localhost`), because the offline mode, the camera upload and the OCR worker all need it:

```
cd golf-scorecard && python3 -m http.server 8000   # then open http://localhost:8000
```

To use it on a phone, host the `golf-scorecard/` folder on any static host (Netlify, GitHub Pages, Cloudflare Pages). Open it once, then use **Share → Add to Home Screen**. After that it works with no signal.

## Notes
- Reading handwriting is never perfect. Printed numbers and clear handwriting in a gridded card work best, so lay the card flat with good light. Always check the yellow boxes.
- The 9-hole handicap differential is an approximation of the WHS expected-score method.
