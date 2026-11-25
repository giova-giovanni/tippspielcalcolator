/* Eingabe (docs/app.js): tips of the other players – pure helpers and the one-commit save.
 * Run with: node --test "tests/js/*.test.js". Fictitious players, no network (fetch is mocked). */
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const vm = require('node:vm');

const DOCS = path.join(__dirname, '../../docs');
const plain = (x) => JSON.parse(JSON.stringify(x)); // values from the vm realm -> plain JSON

function memStorage() {
  const m = new Map();
  return { getItem: (k) => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, String(v)), removeItem: (k) => m.delete(k) };
}

/** docs/i18n.js + docs/app.js in a sandbox without DOM (boot() waits for DOMContentLoaded, which never comes). */
function loadApp(fetchImpl) {
  const ctx = {
    console, setTimeout, clearTimeout, TextEncoder, TextDecoder, atob, btoa,
    fetch: (...a) => fetchImpl(...a),
    window: {},
    document: { readyState: 'loading', addEventListener() {}, documentElement: { setAttribute() {}, getAttribute() { return null; }, lang: '' } },
    localStorage: memStorage(),
    sessionStorage: memStorage(),
    location: { hostname: 'localhost', pathname: '/', hash: '' }
  };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(DOCS, 'i18n.js'), 'utf8'), ctx);
  vm.runInContext(fs.readFileSync(path.join(DOCS, 'app.js'), 'utf8'), ctx);
  return { TSP: ctx.window.TSP, I18N: ctx.window.I18N };
}

const HEADER = 'date,player,vorspeise,hauptspeise,beilage,points,points_sheet,source';
const CSV = [HEADER,
  '2026-11-23,Anna,Lasagne,Gulasch,Reis,0.5,0.5,xlsx',
  '2026-11-23,Ich,Hirten,Gulasch,Pommes,0,,form',
  '2026-11-24,Ich,Lasagne,Leberkas,Pommes,1,,form'].join('\n') + '\n';
const KEYS = ['date', 'player'];
const TIP_HEADER = HEADER.split(',');

test('parseTipLine: "V / H / B" from a chat, optional "Name:" prefix', () => {
  const { TSP } = loadApp();
  assert.deepEqual(plain(TSP.parseTipLine('Carbonara / Leberkas / Pommes')), ['Carbonara', 'Leberkas', 'Pommes']);
  assert.deepEqual(plain(TSP.parseTipLine('Anna: Carbonara/Leberkas/Pommes')), ['Carbonara', 'Leberkas', 'Pommes']);
  assert.deepEqual(plain(TSP.parseTipLine('  Nudel mit Ragu  /  Hühnerbrust / Kartoffelsalat ')), ['Nudel mit Ragu', 'Hühnerbrust', 'Kartoffelsalat']);
  assert.equal(TSP.parseTipLine('Aglio olio / Nudel mit Ragu'), null); // two options of one category: no split
  assert.equal(TSP.parseTipLine('A / / C'), null);
  assert.equal(TSP.parseTipLine('A / B / C / D'), null);
  assert.equal(TSP.parseTipLine(''), null);
});

test('parsePoints: comma or dot, 0…max in steps of 0.5, empty = automatic', () => {
  const { TSP } = loadApp();
  assert.equal(TSP.parsePoints('', 3), null);
  assert.equal(TSP.parsePoints('   ', 3), null);
  assert.equal(TSP.parsePoints('1,5', 3), 1.5);
  assert.equal(TSP.parsePoints('1.5', 3), 1.5);
  assert.equal(TSP.parsePoints('0', 3), 0);
  assert.equal(TSP.parsePoints('3', 3), 3);
  for (const bad of ['4', '15', '0,3', '-1', 'abc', '1,5,5', '1.25']) {
    assert.ok(Number.isNaN(TSP.parsePoints(bad, 3)), `${bad} dovrebbe essere rifiutato`);
  }
  assert.equal(TSP.parsePoints('4', 4), 4);
});

test('coDateCheck: rule 6 – the others only after that day\'s deadline', () => {
  const { TSP } = loadApp();
  const today = '2026-11-24'; // Tuesday
  const dl = TSP.deadlineFor(today, '12:00');
  assert.equal(TSP.coDateCheck(today, today, dl - 1, dl, false), 'open');
  assert.equal(TSP.coDateCheck(today, today, dl, dl, false), 'ok');
  assert.equal(TSP.coDateCheck('2026-11-23', today, dl - 3600e3, TSP.deadlineFor('2026-11-23', '12:00'), false), 'ok');
  assert.equal(TSP.coDateCheck('2026-11-25', today, dl + 3600e3, TSP.deadlineFor('2026-11-25', '12:00'), false), 'future');
  assert.equal(TSP.coDateCheck('2026-11-22', today, dl, 0, false), 'weekend');
  assert.equal(TSP.coDateCheck('2026-11-20', today, dl, 0, true), 'free');
  assert.equal(TSP.coDateCheck('24.11.2026', today, dl, 0, false), 'bad');
});

test('scoreHits: rule 9 scoring (full menu = 3)', () => {
  const { TSP } = loadApp();
  const S = {};
  assert.equal(TSP.scoreHits(S, { vorspeise: true, hauptspeise: true, beilage: true }), 3);
  assert.equal(TSP.scoreHits(S, { vorspeise: true, hauptspeise: true, beilage: false }), 1.5);
  assert.equal(TSP.scoreHits(S, { vorspeise: false, hauptspeise: true, beilage: true }), 1);
  assert.equal(TSP.scoreHits(S, { vorspeise: false, hauptspeise: false, beilage: true }), 0.5);
  assert.equal(TSP.scoreHits(S, { vorspeise: false, hauptspeise: false, beilage: false }), 0);
  assert.equal(TSP.scoreHits({ full_menu_total: 4 }, { vorspeise: true, hauptspeise: true, beilage: true }), 4);
});

test('tipValues: points typed by hand go to points_sheet', () => {
  const { TSP } = loadApp();
  assert.equal(TSP.tipValues('2026-11-24', 'Anna', 'A', 'B', 'C', 1.5).points_sheet, '1.5');
  assert.equal(TSP.tipValues('2026-11-24', 'Anna', 'A', 'B', 'C', 0).points_sheet, '0');
  assert.equal(TSP.tipValues('2026-11-24', 'Anna', 'A', 'B', 'C').points_sheet, '');
  assert.equal(TSP.tipValues('2026-11-24', 'Anna', 'A', 'B', 'C', null).points_sheet, '');
});

test('upsertCsvMany: insert + update in one text, sorted, idempotent', () => {
  const { TSP } = loadApp();
  const list = [
    TSP.tipValues('2026-11-24', 'Bruno', 'Carbonara', 'Leberkas', 'Pommes'),
    TSP.tipValues('2026-11-23', 'anna', 'Hirten', 'Gulasch', 'Reis', 1.5), // same player, other case -> update
    TSP.tipValues('2026-11-24', 'Carla', '', '', '', 0.5)                  // points only
  ];
  const up = TSP.upsertCsvMany(CSV, list, KEYS, TIP_HEADER);
  assert.equal(up.inserted, 2);
  assert.equal(up.updated, 1);
  const lines = up.text.trimEnd().split('\n');
  assert.equal(lines[0], HEADER);
  assert.deepEqual(lines.slice(1), [
    '2026-11-23,anna,Hirten,Gulasch,Reis,,1.5,form',
    '2026-11-23,Ich,Hirten,Gulasch,Pommes,0,,form',
    '2026-11-24,Bruno,Carbonara,Leberkas,Pommes,,,form',
    '2026-11-24,Carla,,,,,0.5,form',
    '2026-11-24,Ich,Lasagne,Leberkas,Pommes,1,,form'
  ]);
  assert.ok(up.text.endsWith('\n'));
  assert.equal(TSP.upsertCsvMany(up.text, list, KEYS, TIP_HEADER).text, up.text, 'same rows again: same file');
});

/** fetch mock for the GitHub contents API: one file, optional 409 on the first PUT. */
function githubMock(initialText, opts = {}) {
  const st = { text: initialText, sha: 'sha-1', puts: [], gets: 0, conflicts: opts.conflicts || 0 };
  const reply = (status, body) => Promise.resolve({ status, ok: status >= 200 && status < 300, text: () => Promise.resolve(JSON.stringify(body)) });
  st.fetch = (url, init) => {
    assert.ok(url.startsWith('https://api.github.com/repos/o/r/contents/data/tips.csv'), url);
    if ((init.method || 'GET') === 'GET') {
      st.gets++;
      assert.ok(url.endsWith('?ref=main'));
      return reply(200, { sha: st.sha, encoding: 'base64', content: Buffer.from(st.text, 'utf8').toString('base64') });
    }
    const body = JSON.parse(init.body);
    st.puts.push(body);
    if (st.conflicts > 0) { st.conflicts--; st.sha = 'sha-x'; return reply(409, { message: 'conflict' }); }
    assert.equal(body.sha, st.sha);
    st.text = Buffer.from(body.content, 'base64').toString('utf8');
    st.sha = 'sha-' + (st.puts.length + 1);
    return reply(200, { commit: { sha: 'c' + st.puts.length, html_url: 'https://github.com/o/r/commit/c' } });
  };
  return st;
}
const CFG = { owner: 'o', repo: 'r', branch: 'main', token: 'test-token' };

test('commitRows: every row in one commit, with the given message', async () => {
  const gh = githubMock(CSV);
  const { TSP } = loadApp(gh.fetch);
  const list = [
    TSP.tipValues('2026-11-24', 'Anna', 'Carbonara', 'Leberkas', 'Pommes'),
    TSP.tipValues('2026-11-24', 'Bruno', 'Hirten', 'Gulasch', 'Reis', 1)
  ];
  const steps = [];
  const res = plain(await TSP.commitRows(CFG, 'tip', list, 'Tipps 2026-11-24 Anna, Bruno via Website', (s) => steps.push(s), { skipUnchanged: true }));
  assert.equal(gh.puts.length, 1);
  assert.equal(gh.puts[0].message, 'Tipps 2026-11-24 Anna, Bruno via Website');
  assert.equal(gh.puts[0].branch, 'main');
  assert.equal(res.action, 'insert');
  assert.equal(res.inserted, 2);
  assert.equal(res.path, 'data/tips.csv');
  assert.deepEqual(steps, ['load', 'save']);
  assert.ok(gh.text.includes('2026-11-24,Anna,Carbonara,Leberkas,Pommes,,,form\n'));
  assert.ok(gh.text.includes('2026-11-24,Bruno,Hirten,Gulasch,Reis,,1,form\n'));
  // the same rows again: nothing to commit
  const again = plain(await TSP.commitRows(CFG, 'tip', list, 'x', null, { skipUnchanged: true }));
  assert.equal(again.action, 'none');
  assert.equal(gh.puts.length, 1);
});

test('commitRows: retries once after a 409 and keeps the single-row commitRow message', async () => {
  const gh = githubMock(CSV, { conflicts: 1 });
  const { TSP } = loadApp(gh.fetch);
  const res = plain(await TSP.commitRow(CFG, 'tip', TSP.tipValues('2026-11-23', 'Anna', 'Lasagne', 'Gulasch', 'Pommes')));
  assert.equal(gh.gets, 2);
  assert.equal(gh.puts.length, 2);
  assert.equal(gh.puts[1].message, 'Tipp 2026-11-23 Anna via Website');
  assert.equal(res.action, 'update');
  assert.ok(gh.text.includes('2026-11-23,Anna,Lasagne,Gulasch,Pommes,,,form\n'));
});

test('i18n: every co.* key used by app.js exists in DE and IT', () => {
  const { I18N } = loadApp();
  const src = fs.readFileSync(path.join(DOCS, 'app.js'), 'utf8');
  const used = new Set([...src.matchAll(/\bt\('(co\.[\w.]+)'/g)].map((m) => m[1]));
  assert.ok(used.size >= 10, 'la card dei colleghi usa le chiavi co.*');
  for (const k of used) {
    assert.ok(k in I18N.de, `DE: ${k}`);
    assert.ok(k in I18N.it, `IT: ${k}`);
  }
});
