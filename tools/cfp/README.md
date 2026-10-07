# OSCW Call for Sessions toolkit

A PEPR-style CFP (structured proposals, written reviewer feedback, a second
form for public details) built from Google Forms, one Google Sheet, a pasted
Apps Script, and the Hugo data files in this repo. Nothing runs on the web
server.

```
Phase 1 form ──▶ Response Sheet ──▶ Reviews tab ──▶ Decisions tab ──▶ Gmail drafts
                 (Code.gs adds IDs)  (organizers)    (scores + decision)  (feedback to authors)
                                                                          │
Phase 2 form ◀──────────────── prefilled link in acceptance email ◀───────┘
     │
     └─▶ CSV export ──▶ sheet_to_yaml.py ──▶ data/<year>/sessions.yaml ──▶ {{< schedule >}}
```

## Annual runbook

1. **Copy last year's forms** (or build them from the specs below). Update the
   year, dates, and session lengths. Finalize the questions *before* opening:
   Forms inserts columns for new questions, which can shift the `Submission ID`
   column the script adds.
2. **Link the phase-1 form to a new Sheet** (Responses > Link to Sheets).
3. **Add tabs to that Sheet:**
   - `Config`, column A key / column B value:

     | Key | Example |
     |---|---|
     | `Year` | `2027` |
     | `Phase 2 prefill URL` | `https://docs.google.com/forms/d/e/…/viewform?usp=pp_url&entry.123456={ID}` |
     | `Reply-To` | `organizers@oscwork.shop` |

     Get the prefill URL from the phase-2 form's ⋮ > *Get pre-filled link*:
     type `X` in the Submission ID field, copy the link, and replace `X` with
     `{ID}`.
   - `Reviewers`, with headers `Reviewer` (email) and `Conflicts`
     (comma-separated submission IDs, filled in once IDs exist).
   - `Templates`, with headers `Name`, `Subject`, `Body`. `Name` must match
     the values you'll type in the Decisions tab's `Decision` column (for
     example `accept`, `reject`, `waitlist`). See the
     [starter templates](#starter-email-templates).
4. **Install the script:** Extensions > Apps Script, replace `Code.gs` with
   [`apps-script/Code.gs`](apps-script/Code.gs), and save. Then go to Triggers >
   Add trigger > `onFormSubmit`, event source *From spreadsheet*, event type
   *On form submit*. Reload the Sheet to get the **OSCW CFP** menu.
5. **Do a dry run** in a *copy* of the Sheet before opening the CFP: submit
   2–3 fake proposals, run every menu item, and confirm that drafts appear in
   Gmail and nothing is sent.
6. **Open the CFP:** put the form link and dates in `content/<year>/index.md`
   and `content/_index.md`.
7. **Review:** after the deadline, fill in `Conflicts` and run *Build / extend
   Reviews tab*. Each reviewer filters the tab by their email and fills in a
   score, confidence, and both comment columns. **Comments for authors are
   sent verbatim** (marked only "Reviewer N"). Running the menu item again
   adds rows for late submissions or new reviewers without touching existing
   reviews. Everyone with access to the Sheet can see every review.
8. **Decide:** run *Summarize into Decisions tab*, discuss, and fill in
   `Decision` and `Assigned length`. Re-running Summarize keeps those columns.
9. **Notify:** run *Draft decision emails*. Read each draft in Gmail, edit it
   if needed, and send. The `Drafted` timestamp stops rows from being drafted
   twice; clear it to redraft a row.
10. **Collect public details:** acceptance emails link to the phase-2 form,
    prefilled with the submission ID. Speakers can resubmit to fix things; the
    latest response wins.
11. **Publish:** File > Download > CSV of the phase-2 responses, then:

    ```bash
    tools/cfp/sheet_to_yaml.py data/2027/sessions.yaml --csv ~/Downloads/phase2.csv
    ```

    New sessions are appended with an empty `time`. Set the times, reorder
    them, and add `break` slots by hand. Then check what's still missing:

    ```bash
    tools/cfp/sheet_to_yaml.py data/2027/sessions.yaml --check
    ```

    Put `{{< schedule >}}` in `content/2027/index.md`. `hugo` also warns about
    missing bios and abstracts at build time. Re-run the sync whenever speakers
    send corrections; `time`, `video`, slot order, and breaks are preserved.
    Add `video:` links by hand after the event.

## Form specs

Column headers in the response Sheet come from the question titles, so the
titles in **bold** must match exactly. They're used by `Code.gs` and
`sheet_to_yaml.py`.

### Phase 1: session proposal

Settings: collect email addresses (this produces the **Email Address**
column), allow response editing.

| Question | Type | Notes |
|---|---|---|
| **Presenter name(s)** | Short answer | |
| Presenter affiliation(s) | Short answer | |
| **Session title** | Short answer | |
| Session type | Multiple choice | Presentation / Interactive or hands-on / Panel / Other |
| Preferred length | Checkboxes | 20, 35, or 50 minutes (each including 5 minutes of Q&A) |
| Abstract | Paragraph | Response validation: length ≤ 2000 characters. "What will attendees see in the program?" |
| Outline | Paragraph | "Major sections with rough timings, e.g. *Intro (3 min)*." |
| Audience and takeaways | Paragraph | "Who is this for, and what 2–3 things will they leave with?" |
| Open source projects | Paragraph | Names and links for the projects discussed |
| Prior presentations | Paragraph | Optional. Links to earlier talks on this material and what's new |
| Logistics | Checkboxes + Other | Need a travel stipend / Attendees need laptops / Special A/V |
| Notes for reviewers | Paragraph | Optional and private |

### Phase 2: acceptance details

Doesn't require sign-in. Allow response editing.

| Question | Type | Notes |
|---|---|---|
| **Submission ID** | Short answer | Prefilled from the acceptance email |
| **Final title** | Short answer | As it should appear in the public program |
| **Final abstract** | Paragraph | Public. Markdown allowed |
| **Speaker 1 name** | Short answer | Then **Speaker 1 pronouns**, **Speaker 1 affiliation**, **Speaker 1 link**, **Speaker 1 bio** (3–5 sentences, third person), **Speaker 1 headshot URL** |
| Speaker 2–4 … | | Same six questions with `2`, `3`, `4`. Put each speaker in their own optional section |
| **Recording consent** | Multiple choice | "Yes, under CC BY-NC-ND 4.0" / "No" (anything starting with "Yes" counts) |
| Travel and stipend details | Paragraph | Organizer-only. Not exported to the site |

Use headshot *URLs* rather than file uploads, because Forms file uploads
require respondents to sign in to Google.

## Starter email templates

Placeholders: `{{id}}`, `{{title}}`, `{{presenters}}`, `{{length}}`,
`{{feedback}}`, `{{phase2_link}}`, `{{year}}`.

**accept** / Subject: `OSCW {{year}}: "{{title}}" accepted`

```
Hi {{presenters}},

We're delighted to accept "{{title}}" ({{id}}) for OSCW {{year}} as a {{length}}-minute session.

Please confirm the public details of your session (final title, abstract, bios, and recording consent) here:
{{phase2_link}}

Here's what our reviewers said, which we hope helps as you prepare:

{{feedback}}

Thanks,
The OSCW organizers
```

**reject** / Subject: `OSCW {{year}}: your proposal "{{title}}"`

```
Hi {{presenters}},

Thank you for proposing "{{title}}" ({{id}}) for OSCW {{year}}. We had more strong proposals than slots, and unfortunately we couldn't include yours this year.

Here's what our reviewers said, in case it's useful:

{{feedback}}

We hope to see you at the workshop, and we'd love to see a proposal from you next year.

Thanks,
The OSCW organizers
```

## Tests

The converter's tests use synthetic responses plus `data/2026/sessions.yaml`
as a round-trip fixture:

```bash
uv tool run --with ruamel.yaml --with rich pytest tools/cfp
```

`Code.gs` has no automated tests. Use the dry run in step 5.
