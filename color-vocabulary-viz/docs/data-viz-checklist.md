# How these visualizations meet the Data Visualization Checklist

Notes on how the two pieces line up with the Evergreen & Emery *Data
Visualization Checklist*, for the static drip chart in particular.

## Text
- **Descriptive title, upper-left.** "We name a whole rainbow, but our words
  clump" states the finding rather than the topic.
- **Subtitle adds interpretation.** The one-line subtitle names the specific
  pattern (oranges and roses deep, blues shallow).
- **Text hierarchy.** Title > subtitle > family labels > counts > source line.
- **Horizontal text throughout.**
- **Data labeled directly.** Family names and counts sit at each column; no
  separate legend to bounce between.

## Arrangement
- **Accurate proportions.** Column length is directly proportional to the count;
  dashed guide-lines at 50 / 100 / 150 let a viewer measure.
- **Intentional order.** Columns follow the hue wheel (red -> rose), with the
  neutral grey family last.
- **Two-dimensional.** No 3-D, bevels, or distortion.
- **Free of decoration that misleads.** The paint styling is expressive but the
  encoded quantity is only the column length; no chartjunk carries false meaning.

## Color
- **Color is the subject, chosen intentionally.** Every column shows its
  family's real surveyed colors, not an arbitrary palette.
- **Contrast.** Dark text on a light gallery wall.

## Lines
- **No heavy gridlines or border.** Only faint dashed reference lines.
- **One horizontal rail, one implied vertical scale.**

## Overall
- **Clear finding.** The "vocabulary clumps" conclusion is the whole point.
- **Appropriate chart type.** A magnitude comparison across categories -> a bar
  chart (here, an inverted, stylized one).
- **Comparison built in.** All thirteen families are shown together, so the
  imbalance is self-evident.
- **Elements reinforce one message.** Title, color, length, and the trend line
  all point at the same takeaway.

The spiral is the exploratory companion: it trades some strict measurability for
discoverability (hover to read any of the 954 names, filter by family), and is
intended to be experienced live rather than measured with a ruler.
