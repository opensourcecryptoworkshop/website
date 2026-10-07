/**
 * OSCW Call for Sessions helpers for the proposal-form response Sheet.
 *
 * Paste this file into Extensions > Apps Script of the Sheet linked to the
 * phase-1 proposal form. See tools/cfp/README.md for setup and the expected
 * Config, Reviewers, and Templates tabs.
 *
 * Nothing here sends mail: decision emails are created as Gmail drafts for an
 * organizer to read and send.
 */

const RESPONSES_SHEET = 'Form Responses 1';
const CONFIG_SHEET = 'Config';
const REVIEWERS_SHEET = 'Reviewers';
const TEMPLATES_SHEET = 'Templates';
const REVIEWS_SHEET = 'Reviews';
const DECISIONS_SHEET = 'Decisions';

// Proposal form column headers; keep in sync with the form and README.md.
const COL_ID = 'Submission ID';
const COL_EMAIL = 'Email Address';
const COL_PRESENTERS = 'Presenter name(s)';
const COL_TITLE = 'Session title';

const REVIEW_HEADERS = [
  'Submission ID', 'Title', 'Reviewer', 'Score (1-4)', 'Confidence (1-3)',
  'Comments for authors', 'Comments for committee only',
];
const DECISION_HEADERS = [
  'Submission ID', 'Title', 'Presenters', 'Email', 'Reviews', 'Mean score',
  'Min', 'Max', 'Decision', 'Assigned length', 'Drafted',
];

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('OSCW CFP')
    .addItem('Assign missing submission IDs', 'assignMissingIds')
    .addItem('Build / extend Reviews tab', 'buildReviews')
    .addItem('Summarize into Decisions tab', 'summarize')
    .addItem('Draft decision emails', 'draftDecisionEmails')
    .addToUi();
}

/** Installable trigger: From spreadsheet > On form submit. */
function onFormSubmit(e) {
  assignMissingIds();
}

// ---------------------------------------------------------------------------
// Helpers

function sheet_(name) {
  const sheet = SpreadsheetApp.getActive().getSheetByName(name);
  if (!sheet) throw new Error(`Missing tab "${name}"; see tools/cfp/README.md`);
  return sheet;
}

function sheetOrCreate_(name, headers) {
  const ss = SpreadsheetApp.getActive();
  let sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
    sheet.appendRow(headers);
    sheet.setFrozenRows(1);
    // IDs like 2027-01 would otherwise be parsed as dates.
    sheet.getRange('A:A').setNumberFormat('@');
  }
  return sheet;
}

/** Returns the rows of a tab as objects keyed by header. */
function records_(sheet) {
  const values = sheet.getDataRange().getValues();
  const headers = values.shift();
  return values.map((row) => Object.fromEntries(headers.map((h, i) => [h, row[i]])));
}

/** Config tab: column A is the key, column B the value. */
function config_() {
  const values = sheet_(CONFIG_SHEET).getDataRange().getValues();
  return Object.fromEntries(values.map(([k, v]) => [String(k).trim(), v]));
}

function columnIndex_(sheet, header) {
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  let idx = headers.indexOf(header);
  if (idx === -1) {
    idx = headers.length;
    sheet.getRange(1, idx + 1).setValue(header);
  }
  return idx + 1;
}

function fill_(template, values) {
  return template.replace(/\{\{(\w+)\}\}/g, (m, key) => (key in values ? values[key] : m));
}

// ---------------------------------------------------------------------------
// Submission IDs

/** Gives every response a stable ID like 2027-07. Safe to run repeatedly. */
function assignMissingIds() {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const year = String(config_()['Year']);
    const sheet = sheet_(RESPONSES_SHEET);
    const col = columnIndex_(sheet, COL_ID);
    const lastRow = sheet.getLastRow();
    if (lastRow < 2) return;
    const range = sheet.getRange(2, col, lastRow - 1, 1);
    // IDs like 2027-01 would otherwise be parsed as dates.
    range.setNumberFormat('@');
    const ids = range.getValues();
    let next = 1 + Math.max(0, ...ids.map(([id]) => Number(String(id).split('-')[1]) || 0));
    for (const row of ids) {
      if (!row[0]) row[0] = `${year}-${String(next++).padStart(2, '0')}`;
    }
    range.setValues(ids);
  } finally {
    lock.releaseLock();
  }
}

// ---------------------------------------------------------------------------
// Reviews

/**
 * Adds a Reviews row for each (submission, reviewer) pair that doesn't have
 * one yet, skipping conflicts. Never removes or edits existing reviews.
 */
function buildReviews() {
  assignMissingIds();
  const submissions = records_(sheet_(RESPONSES_SHEET));
  const reviewers = records_(sheet_(REVIEWERS_SHEET)).filter((r) => r['Reviewer']);
  const sheet = sheetOrCreate_(REVIEWS_SHEET, REVIEW_HEADERS);
  const existing = new Set(records_(sheet).map((r) => `${r['Submission ID']}|${r['Reviewer']}`));

  const rows = [];
  for (const sub of submissions) {
    for (const rev of reviewers) {
      const conflicts = String(rev['Conflicts'] || '').split(',').map((s) => s.trim());
      if (conflicts.includes(sub[COL_ID])) continue;
      if (existing.has(`${sub[COL_ID]}|${rev['Reviewer']}`)) continue;
      rows.push([sub[COL_ID], sub[COL_TITLE], rev['Reviewer'], '', '', '', '']);
    }
  }
  if (rows.length) {
    sheet.getRange(sheet.getLastRow() + 1, 1, rows.length, REVIEW_HEADERS.length).setValues(rows);
  }
  const lastRow = Math.max(sheet.getLastRow(), 2);
  sheet.getRange(2, 4, lastRow - 1, 1).setDataValidation(
    SpreadsheetApp.newDataValidation().requireNumberBetween(1, 4).build());
  sheet.getRange(2, 5, lastRow - 1, 1).setDataValidation(
    SpreadsheetApp.newDataValidation().requireNumberBetween(1, 3).build());
  SpreadsheetApp.getActive().toast(`Added ${rows.length} review rows`);
}

// ---------------------------------------------------------------------------
// Decisions

/**
 * Rewrites the Decisions tab with score statistics, keeping any Decision,
 * Assigned length, and Drafted values already entered.
 */
function summarize() {
  const submissions = records_(sheet_(RESPONSES_SHEET));
  const reviews = records_(sheet_(REVIEWS_SHEET));
  const sheet = sheetOrCreate_(DECISIONS_SHEET, DECISION_HEADERS);
  const kept = Object.fromEntries(records_(sheet).map((r) => [r['Submission ID'], r]));

  const rows = submissions.map((sub) => {
    const id = sub[COL_ID];
    const scores = reviews
      .filter((r) => r['Submission ID'] === id && r['Score (1-4)'] !== '')
      .map((r) => Number(r['Score (1-4)']));
    const mean = scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : '';
    const prev = kept[id] || {};
    return [
      id, sub[COL_TITLE], sub[COL_PRESENTERS], sub[COL_EMAIL], scores.length,
      mean === '' ? '' : Math.round(mean * 100) / 100,
      scores.length ? Math.min(...scores) : '', scores.length ? Math.max(...scores) : '',
      prev['Decision'] || '', prev['Assigned length'] || '', prev['Drafted'] || '',
    ];
  });

  sheet.getRange(2, 1, Math.max(sheet.getLastRow() - 1, 1), DECISION_HEADERS.length).clearContent();
  if (rows.length) sheet.getRange(2, 1, rows.length, DECISION_HEADERS.length).setValues(rows);
}

/**
 * For each Decisions row with a Decision matching a Templates name and an
 * empty Drafted cell, creates a Gmail draft with the reviewers' comments for
 * authors, then records when it was drafted.
 */
function draftDecisionEmails() {
  const config = config_();
  const templates = Object.fromEntries(
    records_(sheet_(TEMPLATES_SHEET)).map((t) => [String(t['Name']).trim().toLowerCase(), t]));
  const reviews = records_(sheet_(REVIEWS_SHEET));
  const sheet = sheet_(DECISIONS_SHEET);
  const values = sheet.getDataRange().getValues();
  const headers = values[0];
  const col = (h) => headers.indexOf(h);

  let drafted = 0;
  for (let i = 1; i < values.length; i++) {
    const row = values[i];
    const decision = String(row[col('Decision')]).trim().toLowerCase();
    if (!decision || row[col('Drafted')] || !(decision in templates)) continue;

    const id = row[col('Submission ID')];
    const comments = reviews
      .filter((r) => r['Submission ID'] === id && String(r['Comments for authors']).trim())
      .map((r, n) => `Reviewer ${n + 1}:\n${String(r['Comments for authors']).trim()}`);
    const fields = {
      id,
      title: row[col('Title')],
      presenters: row[col('Presenters')],
      length: row[col('Assigned length')],
      feedback: comments.length ? comments.join('\n\n') : '(No written comments.)',
      phase2_link: String(config['Phase 2 prefill URL'] || '')
        .replace('{ID}', encodeURIComponent(id)),
      year: config['Year'],
    };
    const template = templates[decision];
    GmailApp.createDraft(
      row[col('Email')],
      fill_(String(template['Subject']), fields),
      fill_(String(template['Body']), fields),
      config['Reply-To'] ? { replyTo: config['Reply-To'] } : {});
    sheet.getRange(i + 1, col('Drafted') + 1).setValue(new Date());
    drafted++;
  }
  SpreadsheetApp.getActive().toast(`Created ${drafted} Gmail drafts; review and send them from Gmail.`);
}
