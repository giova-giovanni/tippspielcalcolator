/* Tests for docs/piano-core.js – run with: node --test tests/js
 * Fictitious profiles and dates only (never real personal data). */
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');

const C = require('../../docs/piano-core.js');
const TABLE = JSON.parse(fs.readFileSync(path.join(__dirname, '../../docs/piano/dish_nutrition.json'), 'utf8'));

const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) < eps, `${a} != ${b}`);

// Fictitious reference profile (agreed fixture): man, 30 y, 180 cm, 90 kg, factor 1.45, deficit 700.
const PROFILE = { sex: 'm', age: 30, heightCm: 180, startWeightKg: 90, startDate: '2030-01-07' };
const GOALS = { activity: 1.45, deficit: 700 };

// Small synthetic dish table with known values.
const MINI = {
  dishes: {
    vorspeise: {
      'Pasta Rossa': { kcal: 500, prot: 15, tags: ['carbo'] },
      'Pasta Panna': { kcal: 700, prot: 20, tags: ['cremoso', 'carbo'] }
    },
    hauptspeise: {
      'Pollo': { kcal: 250, prot: 40, tags: ['magro'] },
      'Cotoletta': { kcal: 450, prot: 30, tags: ['impanato'] },
      'Salsiccia': { kcal: 500, prot: 20, tags: ['carne_grassa'] }
    },
    beilage: {
      'Riso': { kcal: 250, prot: 5, tags: ['carbo'] },
      'Patatine': { kcal: 400, prot: 5, tags: ['fritto', 'carbo'] },
      'Insalata': { kcal: 80, prot: 2, tags: ['verdura'] }
    }
  },
  rules: [{ cat: 'hauptspeise', match: 'schnitzel', kcal: 460, prot: 32, tags: ['impanato'] }]
};
const idx = C.dishIndex(MINI);

// ------------------------------------------------------------------ targets
test('targets: reference fixture 1880 / 2726 / 2050 kcal / 110 g', () => {
  const t = C.targets(PROFILE, GOALS);
  assert.equal(t.bmr, 1880);
  near(t.tdee, 2726, 1e-6);
  assert.equal(t.kcal, 2050);
  assert.equal(t.protein, 110);
  assert.equal(t.proteinAuto, true);
});

test('targets: women formula, current weight, limits and manual protein', () => {
  near(C.bmr({ sex: 'f', kg: 60, heightCm: 165, age: 40 }), 1270.25);
  assert.equal(C.targets(PROFILE, GOALS, 80).bmr, 1780); // latest weigh-in replaces the start weight
  assert.equal(C.targets(PROFILE, { activity: 2.5, deficit: 50 }).activity, 1.8);
  assert.equal(C.targets(PROFILE, { activity: 2.5, deficit: 50 }).deficit, 300);
  const m = C.targets(PROFILE, { proteinG: 142 });
  assert.equal(m.protein, 140);
  assert.equal(m.proteinAuto, false);
  assert.equal(C.targets({ sex: 'm', age: '', heightCm: 180, startWeightKg: 90 }, GOALS), null);
  assert.equal(C.targets(PROFILE, { activity: '1,45', deficit: '700' }).kcal, 2050); // strings from inputs
});

test('validation of profile and goals', () => {
  assert.equal(C.validateProfile(PROFILE).ok, true);
  const bad = C.validateProfile({ sex: 'x', age: 5, heightCm: 300, startWeightKg: 10, startDate: '2030-02-30' });
  assert.deepEqual(Object.keys(bad.errors).sort(), ['age', 'heightCm', 'sex', 'startDate', 'startWeightKg']);
  assert.equal(C.validateGoals({ activity: 1.45, deficit: 700, breakfastKcal: 490, breakfastProt: 15 }).ok, true);
  assert.equal(C.validateGoals({ activity: 1.9, deficit: 700, breakfastKcal: 490, breakfastProt: 15, proteinG: '' }).ok, false);
  assert.deepEqual(C.zone2(30), [114, 133]);
});

test('parseNum and roundTo', () => {
  assert.equal(C.parseNum('129,4'), 129.4);
  assert.equal(C.parseNum(' 90 '), 90);
  assert.equal(C.parseNum('abc'), null);
  assert.equal(C.parseNum(''), null);
  assert.equal(C.parseNum('1,2,3'), null);
  assert.equal(C.roundTo(2026, 50), 2050);
  assert.equal(C.roundTo(108, 5), 110);
});

// ------------------------------------------------------------------ dishes
test('dish lookup on the real table: exact, rules, category mean', () => {
  const real = C.dishIndex(TABLE);
  assert.equal(C.dishInfo(real, 'beilage', 'Pommes').source, 'table');
  assert.equal(C.dishInfo(real, 'vorspeise', 'nudel mit käsesosse').source, 'table'); // case and ß
  const s = C.dishInfo(real, 'hauptspeise', 'Hendlschnitzel');
  assert.equal(s.source, 'rule');
  assert.ok(s.tags.includes('impanato'));
  assert.ok(C.dishInfo(real, 'hauptspeise', 'Puten-Cordon-Bleu').tags.includes('fritto'));
  assert.equal(C.dishInfo(real, 'vorspeise', 'Tomatencremesuppe').kcal, 320);
  const d = C.dishInfo(real, 'vorspeise', 'Xyz');
  assert.equal(d.source, 'default');
  assert.equal(d.kcal, real.means.vorspeise.kcal);
  assert.equal(C.dishInfo(real, 'vorspeise', '  '), null);
  for (const c of C.CATS) assert.ok(real.means[c].kcal > 0 && real.means[c].kcal <= 1500);
});

// ------------------------------------------------------------------ lunch
test('lunch estimate: portions and manual entry', () => {
  const picks = { vorspeise: 'Pasta Rossa', hauptspeise: 'Pollo', beilage: 'Riso' };
  assert.equal(C.lunchEstimate(idx, picks, 'all').kcal, 1000);
  assert.equal(C.lunchEstimate(idx, picks, 'noPrimo').kcal, 500);
  assert.equal(C.lunchEstimate(idx, picks, 'halfPrimo').kcal, 750);
  assert.equal(C.lunchEstimate(idx, picks, 'bis').kcal, 1500);
  assert.equal(C.lunchEstimate(idx, picks, 'all').prot, 60);
  const e = C.lunchEstimate(idx, picks, 'elsewhere', { kcal: '900' });
  assert.deepEqual([e.kcal, e.prot, e.protAssumed, e.manual], [900, C.ELSEWHERE_PROT, true, true]);
  assert.equal(C.lunchEstimate(idx, picks, 'elsewhere', { kcal: 900, prot: '45' }).prot, 45);
  assert.equal(C.lunchEstimate(idx, picks, 'elsewhere', {}).unknown, true); // no kcal yet
  const partial = C.lunchEstimate(idx, { vorspeise: 'Pasta Rossa', hauptspeise: null, beilage: 'Riso' }, 'all');
  assert.equal(partial.items.length, 2);
  const unk = C.lunchEstimate(idx, null, 'all');
  assert.equal(unk.unknown, true);
  assert.equal(unk.kcal, idx.means.vorspeise.kcal + idx.means.hauptspeise.kcal + idx.means.beilage.kcal);
  assert.equal(C.lunchEstimate(idx, { vorspeise: 'Qwerty' }, 'all').generic, true);
});

test('lunch level: red, green, yellow rules', () => {
  const lv = (picks, portion) => C.classifyLunch(C.lunchEstimate(idx, picks, portion || 'all'));
  // red by kcal (700 + 500 + 400 = 1600) – also matches the structural rules
  assert.equal(lv({ vorspeise: 'Pasta Panna', hauptspeise: 'Salsiccia', beilage: 'Patatine' }).level, 'red');
  // red: breaded main + fried side, only 1350 kcal
  const fc = lv({ vorspeise: 'Pasta Rossa', hauptspeise: 'Cotoletta', beilage: 'Patatine' });
  assert.deepEqual([fc.level, fc.reasons], ['red', ['fried_combo']]);
  // red: creamy first + fatty meat, 1280 kcal
  const cf = lv({ vorspeise: 'Pasta Panna', hauptspeise: 'Salsiccia', beilage: 'Insalata' });
  assert.deepEqual([cf.level, cf.reasons], ['red', ['creamy_fatty']]);
  // ... but not when the first course was skipped
  assert.equal(lv({ vorspeise: 'Pasta Panna', hauptspeise: 'Salsiccia', beilage: 'Insalata' }, 'noPrimo').level, 'green');
  // green: <= 1150 and nothing fried/breaded
  assert.equal(lv({ vorspeise: 'Pasta Rossa', hauptspeise: 'Pollo', beilage: 'Riso' }).level, 'green');
  // yellow: <= 1150 but breaded
  assert.deepEqual(lv({ vorspeise: 'Pasta Rossa', hauptspeise: 'Cotoletta', beilage: 'Insalata' }).reasons, ['fried']);
  // yellow: between the thresholds
  assert.equal(lv({ vorspeise: 'Pasta Panna', hauptspeise: 'Pollo', beilage: 'Riso' }).level, 'yellow'); // 1200
  assert.equal(C.classifyLunch(C.lunchEstimate(idx, null, 'all')).level, 'yellow'); // unknown menu
  // manual kcal: thresholds only, boundaries included
  const man = (k) => C.lunchLevel(C.lunchEstimate(idx, null, 'elsewhere', { kcal: k }));
  assert.deepEqual([man(1450), man(1449), man(1151), man(1150)], ['red', 'yellow', 'yellow', 'green']);
});

// ------------------------------------------------------------------ dinner
test('dinner level follows the lunch, one level up on training days', () => {
  assert.equal(C.dinnerLevel('red', false), 'red');
  assert.equal(C.dinnerLevel('red', true), 'yellow');
  assert.equal(C.dinnerLevel('yellow', true), 'green');
  assert.equal(C.dinnerLevel('green', true), 'green');
  assert.equal(C.dinnerLevel('???', false), 'yellow');
});

test('dinner budget and protein gap', () => {
  // 2050 - 490 - 40 - 600 = 920 (no training: no snack)
  const b = C.dinnerBudget({ targetKcal: 2050, lunchKcal: 600, training: false });
  assert.deepEqual([b.kcal, b.clamped, b.snack, b.coffee], [920, null, 0, 40]);
  // 2050 - 490 - 200 - 40 - 1220 = 100 -> limited to 500
  const lo = C.dinnerBudget({ targetKcal: 2050, lunchKcal: 1220, training: true });
  assert.deepEqual([lo.raw, lo.kcal, lo.clamped], [100, 500, 'min']);
  const hi = C.dinnerBudget({ targetKcal: 3000, lunchKcal: 600, training: false });
  assert.deepEqual([hi.kcal, hi.clamped], [1100, 'max']);
  assert.equal(C.dinnerBudget({ targetKcal: 2050, lunchKcal: 600, training: false, goals: { breakfastKcal: 450 } }).kcal, 960);
  // 110 - 15 - 16 - 50 = 29
  assert.equal(C.proteinGap({ targetProt: 110, lunchProt: 50, training: true }), 29);
  assert.equal(C.proteinGap({ targetProt: 60, lunchProt: 80, training: false }), 0);
});

const RECIPES = [
  { id: 'r1', level: 'red', kcal: 450, prot: 54, protein: 'pollo' },
  { id: 'r2', level: 'red', kcal: 530, prot: 57, protein: 'uova' },
  { id: 'r3', level: 'red', kcal: 440, prot: 60, protein: 'pesce' },
  { id: 'y1', level: 'yellow', kcal: 630, prot: 65, protein: 'pollo' },
  { id: 'y2', level: 'yellow', kcal: 660, prot: 46, protein: 'pesce' },
  { id: 'y3', level: 'yellow', kcal: 600, prot: 46, protein: 'tonno' },
  { id: 'y4', level: 'yellow', kcal: 670, prot: 66, protein: 'pollo' },
  { id: 'g1', level: 'green', kcal: 810, prot: 55, protein: 'tonno' },
  { id: 'g2', level: 'green', kcal: 760, prot: 59, protein: 'pollo' }
];

test('dinner proposals: level, budget, protein, recent, variety', () => {
  const p = C.proposeDinners(RECIPES, { level: 'yellow', budget: 700, proteinGap: 66, recent: [] });
  assert.equal(p.length, 3);
  assert.equal(p[0].recipe.id, 'y4'); // closest protein
  assert.notEqual(p[1].recipe.protein, 'pollo'); // variety before a second chicken dish
  assert.ok(p.every((x) => x.recipe.level === 'yellow' && x.recipe.kcal <= 700 && !x.otherLevel));
  const r = C.proposeDinners(RECIPES, { level: 'yellow', budget: 700, proteinGap: 66, recent: ['y4', 'y1'] });
  assert.ok(!r.slice(0, 2).some((x) => ['y4', 'y1'].includes(x.recipe.id)));
  // only two yellow dishes fit and are fresh -> third comes from a lighter level, flagged
  assert.equal(r[2].otherLevel, true);
  assert.equal(r[2].recipe.level, 'red');
  // nothing fits a tiny budget -> lightest recipes, flagged over budget
  const t = C.proposeDinners(RECIPES, { level: 'green', budget: 300, proteinGap: 40, recent: [] });
  assert.equal(t.length, 3);
  assert.ok(t.every((x) => x.overBudget));
  assert.equal(t[0].recipe.id, 'r3');
});

test('extra suggestion when more than 150 kcal are left', () => {
  assert.equal(C.extraFor(150, 30), null);
  assert.equal(C.extraFor(151, 30).id, 'yogurt');
  assert.equal(C.extraFor(300, 5).id, 'frutto');
  const p = C.proposeDinners(RECIPES, { level: 'green', budget: 1000, proteinGap: 80, recent: [] });
  assert.equal(p[0].extra.id, 'yogurt');
  assert.deepEqual(C.recentDinners({ '2030-01-08': { dinner: { id: 'y1' } }, '2030-01-06': { dinner: { id: 'g1' } } }, '2030-01-09'), ['y1', 'g1']);
});

// ------------------------------------------------------------------ checks, streak, workouts
const ALL = { colazione: true, passi: true, allenamento: true, cena: true, acqua: true, snack: true, letto: true };
const FIVE = { colazione: true, passi: true, cena: true, acqua: true, snack: true }; // no training
const day = (checks) => ({ checks });

test('day score: 5 of 7, non-applicable training counts as done', () => {
  assert.equal(C.dayScore(day(ALL), true).ok, true);
  assert.equal(C.dayScore(day({}), true).done, 0);
  const fr = C.dayScore(day({ colazione: true, passi: true, cena: true, acqua: true }), false); // Friday
  assert.deepEqual([fr.done, fr.applicable, fr.ok], [5, 6, true]);
  const mo = C.dayScore(day({ colazione: true, passi: true, cena: true, acqua: true }), true);
  assert.deepEqual([mo.done, mo.ok], [4, false]);
  assert.deepEqual(mo.missing, ['allenamento', 'snack', 'letto']);
});

test('streak: weekends and days off do not break it, today in progress does not count', () => {
  // 2030-01-07 is a Monday (fictitious dates)
  const days = {
    '2030-01-07': day(ALL), '2030-01-08': day(FIVE), '2030-01-09': day(ALL), '2030-01-10': day(ALL),
    '2030-01-11': day(FIVE), '2030-01-14': day(ALL)
  };
  const o = { start: '2030-01-07', today: '2030-01-15' };
  assert.equal(C.streak(days, o), 6); // Tue 15 not done yet: still 6
  assert.equal(C.streak(Object.assign({}, days, { '2030-01-15': day(ALL) }), o), 7);
  assert.equal(C.streak(Object.assign({}, days, { '2030-01-10': day({}) }), o), 2); // broken on Thu
  assert.equal(C.streak(days, { start: '2030-01-09', today: '2030-01-15' }), 4);
  assert.equal(C.streak(days, { start: '2030-01-20', today: '2030-01-15' }), 0); // before start
  // a day at home is skipped like a weekend
  const off = (iso) => C.isWeekend(iso) || iso === '2030-01-10';
  assert.equal(C.streak(Object.assign({}, days, { '2030-01-10': day({}) }), Object.assign({ isOff: off }, o)), 5);
});

test('workouts of the week', () => {
  const days = { '2030-01-07': day(ALL), '2030-01-08': day(FIVE), '2030-01-09': day(ALL) };
  assert.deepEqual(C.weekWorkouts(days, { monday: '2030-01-07' }), { planned: 4, done: 2 });
  assert.deepEqual(C.weekWorkouts(days, { monday: '2030-01-07', start: '2030-01-09' }), { planned: 2, done: 1 });
  const off = (iso) => C.isWeekend(iso) || iso === '2030-01-07';
  assert.deepEqual(C.weekWorkouts(days, { monday: '2030-01-07', isOff: off }), { planned: 3, done: 1 });
  assert.equal(C.trainingToday('2030-01-07', { training: false }), false);
  assert.equal(C.trainingToday('2030-01-11', {}), false); // Friday: rest
  assert.equal(C.trainingToday('2030-01-08', {}), true); // Tuesday: cardio
});

// ------------------------------------------------------------------ cycle
test('12-week cycle and sets per week', () => {
  assert.deepEqual(C.cycleInfo('2030-01-07', '2030-01-03'), { started: false, daysToStart: 4, week: 0, phase: 'before' });
  assert.equal(C.cycleInfo('2030-01-07', '2030-01-07').phase, 'settle');
  assert.equal(C.cycleInfo('2030-01-07', '2030-01-20').week, 2);
  assert.deepEqual([C.cycleInfo('2030-01-07', '2030-01-21').week, C.cycleInfo('2030-01-07', '2030-01-21').phase], [3, 'cut']);
  assert.equal(C.cycleInfo('2030-01-07', '2030-03-18').phase, 'deload'); // day 70
  assert.equal(C.cycleInfo('2030-01-07', '2030-03-25').phase, 'check'); // day 77
  assert.equal(C.cycleInfo('2030-01-07', '2030-04-01').phase, 'after');
  assert.equal(C.cycleInfo('', '2030-01-07'), null);
  assert.deepEqual([C.setsFor(3, 1), C.setsFor(3, 3), C.setsFor(3, 11), C.setsFor(2, 11), C.setsFor(3, 0)], [2, 3, 2, 1, 3]);
});

// ------------------------------------------------------------------ weight
test('weigh-ins: series, due, trend', () => {
  const s = C.weightSeries({ '2030-01-21': 98, '2030-01-07': 100, '2030-01-14': 99, 'x': 5, '2030-01-15': 'a' });
  assert.deepEqual(s.map((p) => p.date), ['2030-01-07', '2030-01-14', '2030-01-21']);
  const t = C.weightTrend(s, '2030-01-22');
  near(t.kgPerWeek, -1);
  assert.equal(t.n, 3);
  near(t.at('2030-01-28'), 97);
  assert.equal(C.weightTrend(s.slice(0, 1), '2030-01-22'), null); // one weigh-in
  assert.equal(C.weightTrend([{ date: '2030-01-07', kg: 100 }, { date: '2030-01-10', kg: 99 }], '2030-01-12'), null); // < 7 days
  assert.equal(C.weightTrend(s, '2030-04-30'), null); // all outside the 42-day window
  const due = C.weighDue(s, '2030-01-27', 7);
  assert.deepEqual([due.daysSince, due.due], [6, false]);
  assert.equal(C.weighDue(s, '2030-01-28', 7).due, true);
  assert.equal(C.weighDue(s, '2030-01-28', 14).due, false);
  assert.equal(C.weighDue([], '2030-01-28', 7).due, true);
});

// ------------------------------------------------------------------ export / import
test('export / import round trip and validation', () => {
  const data = { profile: PROFILE, weights: { '2030-01-07': 100 }, foo: 1 };
  const exp = C.buildExport(data, '2030-01-07T10:00:00Z');
  assert.equal(exp.app, 'tippspiel-piano');
  assert.equal('foo' in exp.data, false); // unknown keys are never exported
  const back = C.parseImport(JSON.stringify(exp));
  assert.equal(back.ok, true);
  assert.deepEqual(back.data.weights, { '2030-01-07': 100 });
  assert.equal(C.parseImport('{oops').error, 'json');
  assert.equal(C.parseImport(JSON.stringify({ app: 'x', version: 1, data: {} })).error, 'app');
  assert.equal(C.parseImport(JSON.stringify(Object.assign({}, exp, { version: 99 }))).error, 'version');
  assert.equal(C.parseImport(JSON.stringify({ app: 'tippspiel-piano', version: 1, data: { token: 'x' } })).error, 'key');
  assert.equal(C.parseImport('').error, 'empty');
});
