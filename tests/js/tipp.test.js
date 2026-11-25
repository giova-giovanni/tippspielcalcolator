/* Tip of the day (docs/app.js): today's tip until 17:00, then the next game day's, manual switch;
 * restarting a lost recalculation. Run with: node --test "tests/js/*.test.js". No network (fetch is mocked). */
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const vm = require('node:vm');

const DOCS = path.join(__dirname, '../../docs');

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
  return ctx.window.TSP;
}

const tip = (date, extra) => Object.assign({ date, recommendation: { vorspeise: { dish: 'V' }, hauptspeise: { dish: 'H' }, beilage: { dish: 'B' } } }, extra || {});
const WED = '2030-01-09';
const THU = '2030-01-10';
const MON = '2030-01-14';
const at = (hh, mm) => hh * 60 + (mm || 0);

test('pickTipDay: today\'s tip until 17:00, then the next one', () => {
  const TSP = loadApp();
  // morning: today.json = today, today_alt.json = provisional tip for tomorrow
  const main = tip(WED), alt = tip(THU, { provisional: true });
  let r = TSP.pickTipDay(main, alt, WED, at(9), null);
  assert.equal(r.which, 'today');
  assert.equal(r.d.date, WED);
  assert.equal(r.next.date, THU);
  // after lunch the engine has moved on: today.json = tomorrow, today_alt.json = today's tip
  const main2 = tip(THU), alt2 = tip(WED, { role: 'today' });
  r = TSP.pickTipDay(main2, alt2, WED, at(13, 30), null);
  assert.deepEqual([r.which, r.d.date, r.manual], ['today', WED, false]);
  r = TSP.pickTipDay(main2, alt2, WED, at(16, 59), null);
  assert.equal(r.d.date, WED);
  r = TSP.pickTipDay(main2, alt2, WED, at(17), null);
  assert.deepEqual([r.which, r.d.date], ['next', THU]);
});

test('pickTipDay: manual switch for the day it was set, ignored otherwise', () => {
  const TSP = loadApp();
  const main = tip(THU), alt = tip(WED);
  let r = TSP.pickTipDay(main, alt, WED, at(13), { day: WED, which: 'next' });
  assert.deepEqual([r.which, r.d.date, r.manual], ['next', THU, true]);
  r = TSP.pickTipDay(main, alt, WED, at(20), { day: WED, which: 'today' });
  assert.deepEqual([r.which, r.d.date, r.manual], ['today', WED, true]);
  r = TSP.pickTipDay(main, alt, WED, at(13), { day: '2030-01-08', which: 'next' }); // yesterday's choice
  assert.deepEqual([r.which, r.manual], ['today', false]);
  r = TSP.pickTipDay(tip(MON), null, '2030-01-12', at(10), { day: '2030-01-12', which: 'today' }); // no tip for today
  assert.deepEqual([r.which, r.d.date], ['next', MON]);
});

test('pickTipDay: weekend, stale or missing files never show a wrong day', () => {
  const TSP = loadApp();
  // Saturday: only Monday's tip
  let r = TSP.pickTipDay(tip(MON), { role: null, date: null }, '2030-01-12', at(10), null);
  assert.deepEqual([r.today, r.which, r.d.date], [null, 'next', MON]);
  // today_alt.json from yesterday (older run): ignored
  r = TSP.pickTipDay(tip(THU), tip('2030-01-08'), WED, at(13), null);
  assert.deepEqual([r.today, r.which, r.d.date], [null, 'next', THU]);
  // only today's tip (no next one yet): today, even in the evening
  r = TSP.pickTipDay(tip(WED), null, WED, at(21), null);
  assert.deepEqual([r.which, r.d.date], ['today', WED]);
  // stale today.json (yesterday) and no alt: shown as is (the page warns), no switch
  const stale = tip('2030-01-08');
  r = TSP.pickTipDay(stale, null, WED, at(9), null);
  assert.deepEqual([r.today, r.next, r.which], [null, null, null]);
  assert.equal(r.d, stale);
  // season over: no recommendation at all
  const over = { date: null, season_over: true, recommendation: null };
  r = TSP.pickTipDay(over, null, WED, at(9), null);
  assert.equal(r.d, over);
});

test('ghDispatch: restarts on-data on the configured branch', async () => {
  const calls = [];
  const TSP = loadApp((url, opts) => {
    calls.push({ url, opts });
    return Promise.resolve({ status: 204, ok: true, text: () => Promise.resolve('') });
  });
  await TSP.ghDispatch({ owner: 'someone', repo: 'tipps', branch: 'main', token: 'x' }, 'on-data.yml');
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, 'https://api.github.com/repos/someone/tipps/actions/workflows/on-data.yml/dispatches');
  assert.equal(calls[0].opts.method, 'POST');
  assert.deepEqual(JSON.parse(calls[0].opts.body), { ref: 'main' });
  const TSP2 = loadApp(() => Promise.resolve({ status: 403, ok: false, text: () => Promise.resolve('{"message":"Resource not accessible"}') }));
  await assert.rejects(TSP2.ghDispatch({ owner: 'someone', repo: 'tipps', branch: 'main', token: 'x' }, 'on-data.yml'), (e) => e.status === 403);
});
