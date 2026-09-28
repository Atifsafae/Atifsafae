# KDP publishing guide – My Super Unicorn Coloring Book (Little Moon Crayons)

Files to upload (folder `output/`):
- **Manuscript:** `interior-KDP.pdf` – 30 pages, 8.5 x 8.5 in, no bleed, fonts embedded, images 300 dpi.
- **Cover:** `cover-KDP.pdf` – 17.318 x 8.75 in (0.125 in bleed, spine 0.068 in for 30 pages on white paper).
  If you change the number of pages, run `python3 finalize.py` again: the spine is recalculated.

## 1. Paperback details (copy/paste)

| Field | Value |
|---|---|
| Language | English |
| Book title | My Super Unicorn Coloring Book |
| Subtitle | 13 Magical Coloring Pages for Kids Ages 4-8: Cute Unicorns, Rainbows, Castles, Mermaids and Birthday Fun |
| Series | (leave empty, or "Little Moon Crayons Coloring Books" if you plan more) |
| Author | Little Moon Crayons |
| Reading age | 4 to 8 |
| Categories | Children's Books > Activities, Crafts & Games > Coloring Books · Children's Books > Animals > Horses · Children's Books > Fairy Tales, Folk Tales & Myths |
| Adult content | No |

**Keywords (7 boxes):**
1. unicorn coloring book for kids ages 4-8
2. unicorn gifts for girls
3. coloring books for girls
4. mermaid unicorn coloring
5. kids activity book birthday gift
6. rainbow castle coloring pages
7. cute animal coloring book toddlers

**Description:**

> Let your little one step into a magical world of unicorns!
>
> **My Super Unicorn Coloring Book** is packed with adorable, happy unicorns ready to be brought to life
> with crayons, pencils and markers. From a magic bakery full of cupcakes to a sunny seaside holiday,
> a candy land, enchanted castles, a mermaid unicorn and a big birthday party, every page is a new adventure.
>
> **Inside you will find:**
> - 13 original unicorn coloring pages
> - Single-sided pages, so markers never bleed through and pages are easy to display
> - Big, bold outlines that are perfect for little hands
> - A "This book belongs to" page and a "Well done, little artist!" certificate
> - A lovely square 8.5 x 8.5 in format
>
> A perfect gift for birthdays, holidays, road trips or a quiet afternoon at home.

## 2. Content

- **ISBN:** get a free KDP ISBN.
- **Print options:** Black & white interior, white paper · Trim size **8.5 x 8.5 in** · **No bleed** · Cover finish **Matte**.
- Upload `interior-KDP.pdf`, then `cover-KDP.pdf` ("Upload a cover you already have").
- **AI-generated content:** answer **Yes**. Images: *"AI-generated, then edited by me"* (the pages were made
  with an AI tool and then edited: translated, cleaned, re-laid out). Text: written by you/with assistance.
- Open the **Previewer** and check every page before continuing.

## 3. Pricing

- Printing cost for 30 B&W pages ≈ $2.30 (Amazon.com).
- Suggested list price: **$7.99** (≈ €7.99 / £6.99). Royalty at 60 % ≈ $2.50 per copy.
- Choose all marketplaces (Amazon.com, .co.uk, .de, .fr …).

## 4. Before you press "Publish"

- [ ] Order an **author proof copy** (a few dollars) and check the printed quality.
- [ ] Previewer shows no warning (margins, resolution, fonts).
- [ ] Barcode area on the back (lower right) is empty – KDP prints it there.

## Tip: make the book more competitive

Most best-selling coloring books have **40-60 pages of designs**. With 13 designs this book is best sold
at a low price or as a gift/party-favour book. Adding more pages later is easy: add them to `source.pdf`
and re-run `finalize.py`, then upload a new interior + cover (the spine changes).
