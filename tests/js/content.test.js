/* Static Piano content (docs/piano/*.json) and UI texts (docs/i18n.js) – run with: node --test tests/js */
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const vm = require('node:vm');

const DOCS = path.join(__dirname, '../../docs');
const readJSON = (rel) => JSON.parse(fs.readFileSync(path.join(DOCS, rel), 'utf8'));
const LEVELS = ['red', 'yellow', 'green'];
const UNITS = [null, 'g', 'ml', 'l', 'pc', 'can', 'slice', 'bag', 'tbsp', 'tsp', 'pack'];
const AISLES = ['produce', 'chilled', 'meat', 'frozen', 'pantry', 'bakery'];
const TAGS = ['batch', 'microonde', '5min'];

const nonEmpty = (s) => typeof s === 'string' && s.trim().length > 0;
const bilingual = (o, where) => {
  assert.ok(o && nonEmpty(o.de) && nonEmpty(o.it), `${where}: testo DE/IT mancante`);
};

function loadI18n() {
  const ctx = {
    window: {},
    localStorage: { getItem: () => null },
    document: { documentElement: { setAttribute() {}, lang: '' } }
  };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(DOCS, 'i18n.js'), 'utf8'), ctx);
  return ctx.window.I18N;
}

test('dinners.json: recipes and basic shopping list', () => {
  const d = readJSON('piano/dinners.json');
  assert.equal(d.version, 1);
  for (const l of LEVELS) {
    bilingual(d.levels[l], `levels.${l}`);
    assert.ok(Array.isArray(d.levels[l].kcal) && d.levels[l].kcal[0] < d.levels[l].kcal[1]);
  }
  bilingual(d.extras.yogurt, 'extras.yogurt');
  bilingual(d.extras.frutto, 'extras.frutto');
  assert.ok(d.recipes.length >= 16);
  const ids = new Set();
  for (const r of d.recipes) {
    const w = `ricetta ${r.id}`;
    assert.ok(nonEmpty(r.id) && !ids.has(r.id), `${w}: id mancante o doppio`);
    ids.add(r.id);
    assert.ok(LEVELS.includes(r.level), `${w}: livello`);
    assert.ok(r.kcal >= 200 && r.kcal <= 1200, `${w}: kcal`);
    assert.ok(r.prot >= 0 && r.prot <= 150, `${w}: proteine`);
    assert.ok(r.minutes > 0 && Number.isInteger(r.servings) && r.servings >= 1, `${w}: minuti/porzioni`);
    assert.ok(nonEmpty(r.protein), `${w}: fonte proteica`);
    assert.ok(Array.isArray(r.tags) && r.tags.every((t) => TAGS.includes(t)), `${w}: tag`);
    bilingual(r.name, `${w}.name`);
    assert.ok(r.ingredients.length > 0, `${w}: ingredienti`);
    for (const i of r.ingredients) {
      assert.ok(nonEmpty(i.id) && nonEmpty(i.de) && nonEmpty(i.it), `${w}: ingrediente ${i.id}`);
      assert.ok(UNITS.includes(i.unit) && AISLES.includes(i.aisle), `${w}: unità/reparto di ${i.id}`);
      assert.ok(i.qty === null || i.qty > 0, `${w}: quantità di ${i.id}`);
      assert.equal(i.qty === null, i.unit === null, `${w}: quantità e unità di ${i.id}`);
    }
    for (const lang of ['de', 'it']) {
      const s = r.steps[lang];
      assert.ok(Array.isArray(s) && s.length >= 3 && s.length <= 5 && s.every(nonEmpty), `${w}: 3–5 passi ${lang}`);
    }
    assert.equal(r.steps.de.length, r.steps.it.length, `${w}: stessi passi in DE e IT`);
  }
  for (const l of LEVELS) assert.ok(d.recipes.filter((r) => r.level === l).length >= 3, `almeno 3 ricette ${l}`);
  assert.ok(d.shopping_base.length > 0);
  for (const i of d.shopping_base) {
    assert.ok(nonEmpty(i.id) && nonEmpty(i.de) && nonEmpty(i.it) && AISLES.includes(i.aisle) && UNITS.includes(i.unit), `spesa base ${i.id}`);
  }
});

test('workouts.json: plan, workouts and exercises', () => {
  const w = readJSON('piano/workouts.json');
  assert.equal(w.version, 1);
  const ids = new Set(w.workouts.map((x) => x.id));
  assert.equal(ids.size, w.workouts.length, 'id delle schede doppi');
  for (const v of Object.values(w.schedule)) assert.ok(ids.has(v), `schedule -> ${v}`);
  assert.ok(ids.has(w.away.workout));
  w.rules.forEach((r, i) => bilingual(r, `rules[${i}]`));
  bilingual(w.note, 'note');
  bilingual(w.zone2, 'zone2');
  bilingual(w.zone2NoAge, 'zone2NoAge');
  for (const lang of ['de', 'it']) assert.ok(w.zone2[lang].includes('{lo}') && w.zone2[lang].includes('{hi}'));
  for (const wo of w.workouts) {
    bilingual(wo.name, `scheda ${wo.id}`);
    assert.ok(wo.minutes > 0 && wo.exercises.length > 0, `scheda ${wo.id}`);
    for (const k of ['finisher', 'intro', 'optional']) if (wo[k]) bilingual(wo[k], `${wo.id}.${k}`);
    for (const e of wo.exercises) {
      const where = `${wo.id}/${e.id}`;
      assert.ok(nonEmpty(e.id), where);
      bilingual(e.name, `${where}.name`);
      bilingual(e.tech, `${where}.tech`);
      bilingual(e.alt, `${where}.alt`);
      assert.ok(Number.isInteger(e.sets) && e.sets >= 1, `${where}: serie`);
      assert.ok(Array.isArray(e.reps) && e.reps.length === 2 && e.reps[0] > 0 && e.reps[0] <= e.reps[1], `${where}: ripetizioni`);
      assert.ok(['reps', 'sec'].includes(e.unit), `${where}: unità`);
      assert.ok(Array.isArray(e.rest) && e.rest.length === 2 && e.rest[0] <= e.rest[1], `${where}: recupero`);
      assert.ok([null, 'dumbbell', 'barbell', 'stack'].includes(e.inc), `${where}: incremento`);
      if (e.variant) {
        bilingual(e.variant.name, `${where}.variant`);
        bilingual(e.variant.tech, `${where}.variant.tech`);
        assert.ok(e.variant.fromWeek > 0);
      }
    }
  }
});

test('dish_nutrition.json: rules compile as JavaScript RegExp', () => {
  const t = readJSON('piano/dish_nutrition.json');
  for (const r of t.rules) assert.doesNotThrow(() => new RegExp(r.match, 'i'), r.match);
});

test('i18n: same keys in DE and IT, every literal t(...) key exists', () => {
  const { de, it } = loadI18n();
  const a = Object.keys(de), b = Object.keys(it);
  assert.deepEqual(a.filter((k) => !(k in it)), [], 'chiavi solo in DE');
  assert.deepEqual(b.filter((k) => !(k in de)), [], 'chiavi solo in IT');
  for (const k of a) assert.ok(nonEmpty(de[k]) && nonEmpty(it[k]), `testo vuoto: ${k}`);
  // placeholders must match between languages
  const ph = (s) => (s.match(/\{\w+\}/g) || []).sort().join(',');
  for (const k of a) assert.equal(ph(de[k]), ph(it[k]), `segnaposto diversi in ${k}`);
  // keys built at run time: t('piano.level.' + level) etc. -> every member must exist
  const C = require('../../docs/piano-core.js');
  const units = UNITS.filter(Boolean).flatMap((u) => [u + '.1', u + '.n']);
  const DYNAMIC = {
    'piano.level.': [...C.LEVELS, 'auto'],
    'piano.src.': ['menu', 'entered', 'forecast', 'free', 'nomenu', 'unknown', 'locked', 'generic'],
    'piano.lunch.noMenu.': ['free', 'nomenu', 'unknown', 'locked'],
    'piano.portion.': C.PORTION_IDS,
    'piano.why.': ['kcal_high', 'fried_combo', 'creamy_fatty', 'kcal_low', 'fried', 'kcal_mid', 'unknown'],
    'piano.phase.': ['before', 'settle', 'cut', 'deload', 'check', 'after'],
    'piano.dinner.clamped.': ['min', 'max'],
    'piano.tag.': TAGS,
    'piano.unit.': units,
    'piano.act.': ['1_2', '1_3', '1_4', '1_45', '1_5', '1_55', '1_6', '1_7', '1_8'],
    'piano.set.f.': ['sex', 'age', 'heightCm', 'startWeightKg', 'startDate', 'activity', 'deficit', 'proteinG', 'breakfastKcal', 'breakfastProt'],
    'piano.check.': C.CHECKS
  };
  for (const [pre, members] of Object.entries(DYNAMIC)) {
    for (const m of members) assert.ok(pre + m in de, `chiave mancante: ${pre + m}`);
  }
  for (const k of ['piano.more.piano', 'piano.more.tipp']) assert.ok(k in de, k); // used by app.js via t(group.title)
  for (const file of ['app.js', 'piano.js']) {
    const p = path.join(DOCS, file);
    if (!fs.existsSync(p)) continue;
    const src = fs.readFileSync(p, 'utf8');
    const used = new Set([...src.matchAll(/\bt\('((?:piano|tab)\.[\w.]+)'/g)].map((m) => m[1]));
    for (const k of used) {
      if (k.endsWith('.')) assert.ok(k in DYNAMIC, `${file}: famiglia di chiavi dinamica non controllata: ${k}`);
      else assert.ok(k in de, `${file}: chiave usata ma non definita: ${k}`);
    }
  }
});
