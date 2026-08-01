# 2-minute video — script & checklist

## What's actually graded (per instructor)

The **video is the only thing you submit** (a public URL). Publishing to PyPI is
optional — the instructor said you don't have to follow the lecture's steps, and
**code quality is not being evaluated**. The grade is the **effort you put into
making the visuals your own unique aesthetic**. So spend your energy on the two
visuals and the reasoning behind them.

--------------------------------------------------------------------------------
## Before you record (2 minutes of setup)

No PyPI account needed — a prebuilt wheel is included in `dist/`, so your
on-camera `pip install` is real and needs no building.

1. Open a terminal in the project root (the folder with `pyproject.toml`).
2. (Optional, for a clean demo) make a fresh virtual environment:
   ```bash
   python -m venv .demo && source .demo/bin/activate      # Windows: .demo\Scripts\activate
   ```
3. Have two things ready to show on screen: this terminal, and a browser.

--------------------------------------------------------------------------------
## The 2-minute script (aim ~2:00)

Covers the three rubric items: (1) pip install + import + README, (2) your two
favorite visualizations + aesthetic choices, (3) two problems you solved.

### [0:00-0:20] Install, import, README
- Screen: terminal.
- Say: "This is `colorviz`, a small visualization library I built from the xkcd
  Color Survey - 954 color names people crowdsourced."
- Run:
  ```bash
  pip install dist/color_vocabulary_viz_nikeverette-0.1.0-py3-none-any.whl
  python
  >>> import colorviz
  >>> colorviz.family_counts()
  ```
- Briefly show the README (on GitHub or the file): point at the Install and Use
  sections. "No dependencies, the data's bundled in, and there are two chart
  functions."

### [0:20-1:35] The two visualizations + aesthetic choices  (spend your time here)
- Run:
  ```python
  >>> colorviz.drip_chart("drips.html")
  >>> colorviz.spiral_chart("spiral.html")
  ```
- Open `drips.html` in the browser.
  - The finding: "We feel like we name a smooth rainbow, but our words clump -
    oranges and roses get tons of names while blues barely any."
  - Aesthetic: "I drew it as dripping paint because the data *is* color - the
    chart becomes the thing it measures. Each column is that family's real
    surveyed colors, hanging from a rail with a hand-drawn ink outline."
  - The principle (cite this): "I was aiming for what Alberto Cairo calls
    *functional art* - expressive, but the function still restricts the form, so
    I kept the honest encoding: the dashed trend line, the guide-lines, and the
    counts."
- Open `spiral.html`.
  - "The companion is exploratory - all 954 names spiral outward by hue, so the
    crowded families literally trace longer arcs."
  - Demo: hover a couple of dots to show names; click a family chip to filter.
  - Aesthetic: "Dark background so the colors glow, and it blooms outward on load
    to reward exploring rather than just reading."

### [1:35-1:50] Two problems and how you solved them
Pick two (all are real):
- **Data licensing.** "My first dataset's terms didn't allow republishing, so I
  switched to the xkcd survey, which is CC BY-NC, and attributed it."
- **Muddy averages.** "Averaging each family's RGB gave brown sludge, because
  averaging different hues cancels them out. I binned colors by hue and showed
  each family's real swatches instead."
- **Honest shapes.** "My first drip design had droplet dots that looked like they
  encoded data but didn't - so I removed them and stretched the bottoms into
  tapered drips, keeping length as the only real signal."

### [1:50-2:05] Closing thoughts
End on an open question - it shows curiosity and lands better than a hard stop.
Say something like:
- "What this really maps is where our *language* for color is rich and where it
  runs thin - which opens up bigger questions. Is that about how we *see* color,
  what we *name*, or the world around us? For example, Russian has separate basic
  words for light and dark blue - would running this survey in another language
  break up that sparse blue arc? That's where I'd take it next."
Keep it as questions the visualization *raises*, not claims about neuroscience -
that's more honest and sounds more thoughtful.

--------------------------------------------------------------------------------
## Record & submit (Zoom)

1. In Zoom, start a meeting alone, share your screen, choose **Record to the
   Cloud**, and run through the script.
2. When Zoom emails that the recording is ready, open its **share settings** and
   **turn off the passcode** (allow anyone with the link).
3. **Verify publicly:** open a private/incognito window and paste the link. If it
   plays with no sign-in or password prompt, you're good. If it asks for a login
   or a USFCA account, it's still restricted - fix the share settings and re-test.
4. Paste the link into the Canvas assignment's **Website URL** field.

Due: Friday, July 31, 2026, 11:59 PM PDT. A link that requires a password,
sign-in, or USFCA account will not be graded - the incognito test catches this.

--------------------------------------------------------------------------------
## Reference to cite

Alberto Cairo, *The Functional Art: An Introduction to Information Graphics and
Visualization* (New Riders, 2012). Core idea: visualization is "functional art" -
it should be beautiful *and* communicate, and when the goal is communication,
the function restricts the form.

--------------------------------------------------------------------------------
## Publishing to PyPI (optional - not required for the grade)

If you later want the real thing: make a TestPyPI account + API token, then
`python -m pip install build twine`, `python -m build`, `twine check dist/*`,
`twine upload --repository testpypi dist/*`. Publishing the package is separate
from your GitHub repo, which can stay private.
