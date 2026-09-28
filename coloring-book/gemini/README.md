# My Magical Winged Unicorn: assembling the Gemini pages

## 1. Generate the images in Gemini (one image per page)

- **One page per image.** Collages of 9 pages are far too small to print: each page is only about
  350 px wide, which is about 45 dpi, and KDP asks for 300 dpi.
- **Portrait format**, in the largest size Gemini offers. The ideal is 2550 x 3300 px, and at least
  1700 x 2200 px. The script cleans up the lines of images that are a bit too small.
- **Pure black and white**, with no grey and no colour. In the collages, "Painting a Rainbow" and
  "Geology Explorer" have a coloured rainbow, so use the black-and-white versions ("LOT 4").
- Check the **banner text** on every page. The collages have mistakes:
  - "Troll's Bridge" is written under a flower market.
  - "Underwater World" is written under the bridge.
  - "Fishing Trip" is written under the underwater scene.
  - "Birthday Celebration" appears twice.
  - The certificate says "Thank you for your message to every today!", which means nothing.
  - "Coliuring" is misspelled.
- Also check for **small logos or watermarks**. There is one on the "Geology Explorer" page.

Prompt to reuse for each page (only change the scene):

> Black and white colouring book page for children aged 4-8, portrait 8.5x11, thick clean black
> outlines, pure white background, no grey shading, no colour. The same cute baby unicorn with big
> sparkly eyes, a long wavy mane and ornate butterfly wings. Scene: **[SCENE]**. Rounded dotted
> border, and a ribbon banner at the bottom that reads "**[TITLE]**" in bold capitals, correctly spelled.

## 2. Name the files and put them in `gemini/images/`

The number at the start of the name is the page's position in the list of 40 themes:
`01-magical-garden.png`, `02-magic-bakery.png` ... `39-trampoline-jump.png`.
You don't need image no. 40 (the certificate): the script draws it with clean text and a line to
write the name.
Put the colour front cover in `gemini/images/cover.png`.

## 3. Build the book

```bash
pip install pillow reportlab
python3 gemini/assemble.py           # final version (stops if a page is missing or too small)
python3 gemini/assemble.py --draft   # preview even if some pages are missing
```

The results go in `gemini/output/`:
- `interior-KDP.pdf`: 82 pages. "This book belongs to", copyright, the 39 designs each with a blank
  back, and the certificate.
- `cover-KDP.pdf`: the full cover (back, spine and front) with bleed. The spine width is
  calculated from the number of pages.
- `preview-no-blank-pages.pdf`: to look through the book or print it at home.

The script also prints a report: the resolution of each image and the pages to regenerate.

KDP settings: 8.5 x 11 in, no bleed, black and white on white paper, matte cover. Declare the
content as AI-generated (Gemini).
