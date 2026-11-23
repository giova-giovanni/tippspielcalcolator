/* Piano – pure logic, no DOM (routine, lunch -> dinner, training, weight).
 *
 * Browser: window.PianoCore (used by docs/piano.js). Node: module.exports (tests in tests/js).
 * Everything here works on plain values; personal data never leaves the device (localStorage
 * keys tsp.piano.*). Tests use fictitious profiles only.
 */
(function (root, factory) {
  'use strict';
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PianoCore = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var CATS = ['vorspeise', 'hauptspeise', 'beilage'];
  var LEVELS = ['red', 'yellow', 'green']; // light -> generous

  var DEFAULT_GOALS = {
    activity: 1.45, deficit: 700, proteinPerKg: 1.2, proteinG: null,
    breakfastKcal: 490, breakfastProt: 15, snackKcal: 200, snackProt: 16,
    coffeeKcal: 20, coffees: 2
  };
  var LIMITS = {
    activity: [1.2, 1.8], deficit: [300, 1000], dinner: [500, 1100],
    age: [14, 100], heightCm: [120, 230], kg: [35, 350], proteinG: [40, 300],
    breakfastKcal: [0, 1500], breakfastProt: [0, 100], waistCm: [40, 250]
  };
  var LUNCH = { red: 1450, green: 1150 };
  /** factor of the Vorspeise for "what I really had" (Hauptspeise and Beilage always 1) */
  var PORTIONS = { all: 1, noPrimo: 0, halfPrimo: 0.5, bis: 2 };
  var PORTION_IDS = ['all', 'noPrimo', 'halfPrimo', 'bis', 'elsewhere'];
  var ELSEWHERE_PROT = 30;
  var EXTRAS = { yogurt: { id: 'yogurt', kcal: 100, prot: 15 }, frutto: { id: 'frutto', kcal: 80, prot: 1 } };
  var EXTRA_MIN = 150;
  var CHECKS = ['colazione', 'passi', 'allenamento', 'cena', 'acqua', 'snack', 'letto'];
  var CHECKS_OK = 5;
  /** default week: Mon strength A, Tue cardio + core, Wed strength B, Thu strength C, Fri rest */
  var SCHEDULE = { 0: 'A', 1: 'cardio', 2: 'B', 3: 'C' };
  var STORE_KEYS = ['v', 'profile', 'goals', 'settings', 'weights', 'waist', 'days',
    'training', 'plans', 'shopping', 'reviews', 'milestones'];
  var EXPORT_APP = 'tippspiel-piano';
  var SCHEMA = 1;

  // ---------------------------------------------------------------- small helpers
  function isNum(x) { return typeof x === 'number' && isFinite(x); }
  function clamp(x, lo, hi) { return Math.min(hi, Math.max(lo, x)); }
  function roundTo(x, step) { return Math.round(x / step) * step; }
  function fold(s) {
    return String(s == null ? '' : s).replace(/ /g, ' ').replace(/\s+/g, ' ').trim().toLowerCase().replace(/ß/g, 'ss');
  }
  /** "129,4" / "129.4" / 129.4 -> 129.4; anything else -> null */
  function parseNum(s) {
    if (isNum(s)) return s;
    if (s === null || s === undefined || typeof s === 'boolean') return null;
    var t = String(s).trim().replace(/\s+/g, '').replace(',', '.');
    if (!/^[-+]?(\d+\.?\d*|\.\d+)$/.test(t)) return null;
    var v = parseFloat(t);
    return isFinite(v) ? v : null;
  }
  function inRange(x, r) { return isNum(x) && x >= r[0] && x <= r[1]; }

  // ---------------------------------------------------------------- dates (ISO strings, UTC math)
  function parseISO(s) { var p = String(s).slice(0, 10).split('-'); return Date.UTC(+p[0], +p[1] - 1, +p[2]); }
  function isISO(s) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(String(s || ''))) return false;
    var ms = parseISO(s);
    return !isNaN(ms) && isoOf(ms) === s;
  }
  function isoOf(ms) { return new Date(ms).toISOString().slice(0, 10); }
  function addDays(iso, n) { return isoOf(parseISO(iso) + n * 864e5); }
  function daysBetween(a, b) { return Math.round((parseISO(b) - parseISO(a)) / 864e5); }
  function weekdayOf(iso) { return (new Date(parseISO(iso)).getUTCDay() + 6) % 7; } // 0 = Monday
  function mondayOf(iso) { return addDays(iso, -weekdayOf(iso)); }
  function isWeekend(iso) { return weekdayOf(iso) >= 5; }

  // ---------------------------------------------------------------- targets
  /** Mifflin-St Jeor. p: {sex: 'm'|'f', kg, heightCm, age} */
  function bmr(p) {
    if (!p) return null;
    var kg = parseNum(p.kg), cm = parseNum(p.heightCm), age = parseNum(p.age);
    if (!(kg > 0 && cm > 0 && age > 0)) return null;
    return 10 * kg + 6.25 * cm - 5 * age + (p.sex === 'f' ? -161 : 5);
  }
  function goalsWithDefaults(g) {
    var o = {};
    Object.keys(DEFAULT_GOALS).forEach(function (k) {
      var v = g && g[k] !== undefined && g[k] !== null && g[k] !== '' ? parseNum(g[k]) : null;
      o[k] = isNum(v) ? v : DEFAULT_GOALS[k];
    });
    return o;
  }
  /**
   * Daily targets from the local profile. currentKg = latest weigh-in (falls back to the start weight).
   * kcal = BMR x activity - deficit, rounded to 50; protein = 1.2 g/kg rounded to 5 (or the manual value).
   */
  function targets(profile, goals, currentKg) {
    if (!profile) return null;
    var g = goalsWithDefaults(goals);
    var kg = isNum(currentKg) ? currentKg : parseNum(profile.startWeightKg);
    var b = bmr({ sex: profile.sex, kg: kg, heightCm: profile.heightCm, age: profile.age });
    if (!isNum(b)) return null;
    var act = clamp(g.activity, LIMITS.activity[0], LIMITS.activity[1]);
    var def = clamp(g.deficit, LIMITS.deficit[0], LIMITS.deficit[1]);
    var tdee = b * act;
    var manualProt = isNum(g.proteinG) && g.proteinG > 0;
    return {
      kg: kg, bmr: b, tdee: tdee, activity: act, deficit: def,
      kcal: roundTo(tdee - def, 50),
      protein: manualProt ? roundTo(g.proteinG, 5) : roundTo(g.proteinPerKg * kg, 5),
      proteinAuto: !manualProt
    };
  }
  /** Zone 2 heart rate: 60–70 % of (220 - age). */
  function zone2(age) {
    var a = parseNum(age);
    if (!(a > 0)) return null;
    return [Math.round(0.6 * (220 - a)), Math.round(0.7 * (220 - a))];
  }
  function validateProfile(p) {
    var err = {};
    p = p || {};
    if (p.sex !== 'm' && p.sex !== 'f') err.sex = 'required';
    if (!inRange(parseNum(p.age), LIMITS.age)) err.age = 'range';
    if (!inRange(parseNum(p.heightCm), LIMITS.heightCm)) err.heightCm = 'range';
    if (!inRange(parseNum(p.startWeightKg), LIMITS.kg)) err.startWeightKg = 'range';
    if (!isISO(p.startDate)) err.startDate = 'date';
    return { ok: !Object.keys(err).length, errors: err };
  }
  function validateGoals(g) {
    var err = {};
    g = g || {};
    var chk = function (k, r, optional) {
      var raw = g[k];
      if (optional && (raw === null || raw === undefined || raw === '')) return;
      if (!inRange(parseNum(raw), r)) err[k] = 'range';
    };
    chk('activity', LIMITS.activity);
    chk('deficit', LIMITS.deficit);
    chk('proteinG', LIMITS.proteinG, true);
    chk('breakfastKcal', LIMITS.breakfastKcal);
    chk('breakfastProt', LIMITS.breakfastProt);
    return { ok: !Object.keys(err).length, errors: err };
  }

  // ---------------------------------------------------------------- dishes
  /** Prepares docs/piano/dish_nutrition.json for lookups (exact name -> regex rules -> category mean). */
  function dishIndex(table) {
    var idx = { cats: {}, rules: [], means: {} };
    CATS.forEach(function (c) {
      var map = {}, sk = 0, sp = 0, n = 0;
      var src = (table && table.dishes && table.dishes[c]) || {};
      Object.keys(src).forEach(function (name) {
        var e = src[name] || {};
        if (!isNum(e.kcal) || !isNum(e.prot)) return;
        map[fold(name)] = { name: name, kcal: e.kcal, prot: e.prot, tags: (e.tags || []).slice() };
        sk += e.kcal; sp += e.prot; n++;
      });
      idx.cats[c] = map;
      idx.means[c] = n ? { kcal: roundTo(sk / n, 10), prot: Math.round(sp / n) } : { kcal: 0, prot: 0 };
    });
    ((table && table.rules) || []).forEach(function (r) {
      if (!r || !r.match) return;
      try {
        idx.rules.push({ cat: r.cat || null, re: new RegExp(r.match, 'i'), kcal: r.kcal, prot: r.prot, tags: (r.tags || []).slice() });
      } catch (e) { /* invalid pattern: ignored (the Python test reports it) */ }
    });
    return idx;
  }
  /** {name, kcal, prot, tags, source: 'table'|'rule'|'default'} or null for an empty name. */
  function dishInfo(idx, cat, name) {
    var k = fold(name);
    if (!k || !idx) return null;
    var e = idx.cats[cat] && idx.cats[cat][k];
    if (e) return { name: e.name, kcal: e.kcal, prot: e.prot, tags: e.tags, source: 'table' };
    var m = idx.means[cat] || { kcal: 0, prot: 0 };
    var label = String(name).replace(/\s+/g, ' ').trim();
    for (var i = 0; i < idx.rules.length; i++) {
      var r = idx.rules[i];
      if (r.cat && r.cat !== cat) continue;
      if (r.re.test(k)) {
        return { name: label, kcal: isNum(r.kcal) ? r.kcal : m.kcal, prot: isNum(r.prot) ? r.prot : m.prot, tags: r.tags, source: 'rule' };
      }
    }
    return { name: label, kcal: m.kcal, prot: m.prot, tags: [], source: 'default' };
  }

  // ---------------------------------------------------------------- lunch
  /**
   * Estimate of the lunch actually eaten.
   * picks: {vorspeise, hauptspeise, beilage} (dish names, null = no dish in that category);
   * portion: all | noPrimo | halfPrimo | bis (= double Vorspeise) | elsewhere (manual kcal/prot).
   * picks === null means "menu unknown": category means, level yellow by default.
   */
  function lunchEstimate(idx, picks, portion, manual) {
    portion = PORTION_IDS.indexOf(portion) >= 0 ? portion : 'all';
    if (portion === 'elsewhere') {
      var mk = parseNum(manual && manual.kcal), mp = parseNum(manual && manual.prot);
      if (isNum(mk) && mk >= 0) {
        return {
          portion: portion, items: [], manual: true, unknown: false, generic: false,
          kcal: Math.round(mk), prot: isNum(mp) && mp >= 0 ? Math.round(mp) : ELSEWHERE_PROT, protAssumed: !(isNum(mp) && mp >= 0)
        };
      }
      // no kcal entered yet: behave like an unknown menu
      var u = lunchEstimate(idx, null, 'all');
      u.portion = portion;
      return u;
    }
    var fV = PORTIONS[portion];
    var items = [], kcal = 0, prot = 0, generic = false, unknown = picks === null || picks === undefined;
    CATS.forEach(function (c) {
      var info;
      if (unknown) {
        var m = (idx && idx.means[c]) || { kcal: 0, prot: 0 };
        info = { name: null, kcal: m.kcal, prot: m.prot, tags: [], source: 'default' };
      } else {
        info = picks[c] ? dishInfo(idx, c, picks[c]) : null;
      }
      if (!info) return;
      var f = c === 'vorspeise' ? fV : 1;
      items.push({ cat: c, name: info.name, kcal: info.kcal, prot: info.prot, tags: info.tags, source: info.source, factor: f });
      kcal += info.kcal * f;
      prot += info.prot * f;
      if (info.source === 'default') generic = true;
    });
    return { portion: portion, items: items, kcal: Math.round(kcal), prot: Math.round(prot), generic: generic, unknown: unknown, manual: false };
  }
  function hasTag(it, tag) { return !!(it && it.tags && it.tags.indexOf(tag) >= 0); }
  function friedOrBreaded(it) { return hasTag(it, 'fritto') || hasTag(it, 'impanato'); }
  /**
   * Level of the lunch: red if kcal >= 1450, or fried/breaded Hauptspeise + fried Beilage, or creamy
   * Vorspeise + fatty-meat Hauptspeise; green if kcal <= 1150 and nothing fried/breaded; yellow otherwise.
   * Only dishes actually eaten count (e.g. "senza primo" ignores the Vorspeise). Unknown menu -> yellow.
   * Returns {level, reasons[]}.
   */
  function classifyLunch(est) {
    if (!est || est.unknown || !isNum(est.kcal)) return { level: 'yellow', reasons: ['unknown'] };
    var by = {};
    est.items.forEach(function (it) { if (it.factor > 0) by[it.cat] = it; });
    var eaten = CATS.map(function (c) { return by[c]; }).filter(Boolean);
    var reasons = [];
    if (est.kcal >= LUNCH.red) reasons.push('kcal_high');
    if (friedOrBreaded(by.hauptspeise) && hasTag(by.beilage, 'fritto')) reasons.push('fried_combo');
    if (hasTag(by.vorspeise, 'cremoso') && hasTag(by.hauptspeise, 'carne_grassa')) reasons.push('creamy_fatty');
    if (reasons.length) return { level: 'red', reasons: reasons };
    var fried = eaten.some(friedOrBreaded);
    if (est.kcal <= LUNCH.green && !fried) return { level: 'green', reasons: ['kcal_low'] };
    return { level: 'yellow', reasons: [fried ? 'fried' : 'kcal_mid'] };
  }
  function lunchLevel(est) { return classifyLunch(est).level; }

  // ---------------------------------------------------------------- dinner
  function shiftLevel(level, n) {
    var i = LEVELS.indexOf(level);
    if (i < 0) i = 1;
    return LEVELS[clamp(i + n, 0, LEVELS.length - 1)];
  }
  /** Dinner follows the lunch level; on training days it goes up one level (red -> yellow -> green). */
  function dinnerLevel(lunchLvl, training) {
    var l = LEVELS.indexOf(lunchLvl) >= 0 ? lunchLvl : 'yellow';
    return training ? shiftLevel(l, 1) : l;
  }
  /**
   * Dinner budget = target - breakfast - snack (training days only) - coffees - lunch, limited to 500–1100.
   * o: {targetKcal, lunchKcal, training, goals}
   */
  function dinnerBudget(o) {
    var g = goalsWithDefaults(o && o.goals);
    var snack = o.training ? g.snackKcal : 0;
    var coffee = g.coffees * g.coffeeKcal;
    var raw = o.targetKcal - g.breakfastKcal - snack - coffee - (o.lunchKcal || 0);
    var lo = LIMITS.dinner[0], hi = LIMITS.dinner[1];
    return {
      raw: Math.round(raw), kcal: Math.round(clamp(raw, lo, hi)),
      clamped: raw < lo ? 'min' : (raw > hi ? 'max' : null),
      breakfast: g.breakfastKcal, snack: snack, coffee: coffee, lunch: o.lunchKcal || 0
    };
  }
  /** Protein still missing at dinner = target - (breakfast + lunch + snack on training days). */
  function proteinGap(o) {
    var g = goalsWithDefaults(o && o.goals);
    var have = g.breakfastProt + (o.training ? g.snackProt : 0) + (o.lunchProt || 0);
    return Math.max(0, Math.round(o.targetProt - have));
  }
  /** Addition when more than 150 kcal are left: yogurt/skyr if protein is still short, otherwise fruit. */
  function extraFor(leftover, protLeft) {
    if (!(leftover > EXTRA_MIN)) return null;
    return protLeft > 10 && leftover >= EXTRAS.yogurt.kcal ? EXTRAS.yogurt : EXTRAS.frutto;
  }
  /**
   * Up to n dinners: same level, within budget, not eaten in the last days, protein close to the gap.
   * Fallbacks (flagged): lighter levels within budget, then recent ones, then the lightest recipes.
   * Prefers different main protein sources (recipe.protein) for variety.
   * o: {level, budget, proteinGap, recent: [ids], n}
   */
  function proposeDinners(recipes, o) {
    var n = o.n || 3, budget = o.budget, gap = o.proteinGap || 0, recent = o.recent || [];
    var li = LEVELS.indexOf(o.level);
    var pool = (recipes || []).filter(function (r) { return r && r.id && isNum(r.kcal) && isNum(r.prot); });
    var fresh = function (r) { return recent.indexOf(r.id) < 0; };
    var fits = function (r) { return r.kcal <= budget; };
    var tiers = [
      pool.filter(function (r) { return r.level === o.level && fits(r) && fresh(r); }),
      pool.filter(function (r) { return LEVELS.indexOf(r.level) < li && fits(r) && fresh(r); }),
      pool.filter(function (r) { return r.level === o.level && fits(r); }),
      pool.filter(fits),
      pool.slice().sort(function (a, b) { return a.kcal - b.kcal; })
    ];
    var out = [], seen = {};
    tiers.forEach(function (tier, ti) {
      var cands = tier.filter(function (r) { return !seen[r.id]; });
      if (ti < 4) {
        cands.sort(function (a, b) {
          return Math.abs(a.prot - gap) - Math.abs(b.prot - gap) ||
            Math.abs(budget - a.kcal) - Math.abs(budget - b.kcal) || (a.id < b.id ? -1 : 1);
        });
      }
      while (out.length < n && cands.length) {
        var used = out.map(function (x) { return x.recipe.protein; });
        var j = 0;
        for (var k = 0; k < cands.length; k++) { if (used.indexOf(cands[k].protein) < 0) { j = k; break; } }
        var r = cands.splice(j, 1)[0];
        seen[r.id] = true;
        out.push({
          recipe: r, leftover: budget - r.kcal, extra: extraFor(budget - r.kcal, gap - r.prot),
          otherLevel: r.level !== o.level, recent: !fresh(r), overBudget: !fits(r)
        });
      }
    });
    return out;
  }
  /** ids of the dinners chosen in the `back` days before `iso` (to avoid repeating them) */
  function recentDinners(days, iso, back) {
    var out = [];
    for (var i = 1; i <= (back || 3); i++) {
      var d = days && days[addDays(iso, -i)];
      if (d && d.dinner && d.dinner.id && out.indexOf(d.dinner.id) < 0) out.push(d.dinner.id);
    }
    return out;
  }

  // ---------------------------------------------------------------- training days, checks, streak
  function isTrainingDay(iso, schedule) {
    var s = schedule || SCHEDULE;
    var v = s[weekdayOf(iso)];
    return v !== undefined && v !== null && v !== '';
  }
  /** Training actually happening (per-day switch overrides the weekly plan). */
  function trainingToday(iso, day, schedule) {
    if (day && typeof day.training === 'boolean') return day.training;
    return isTrainingDay(iso, schedule);
  }
  /**
   * Workday score: 7 checks; a check that does not apply that day (training on a rest day) counts as done.
   * ok = at least 5 of 7.
   */
  function dayScore(day, trainingPlanned) {
    var checks = (day && day.checks) || {};
    var done = 0, applicable = 0, missing = [];
    CHECKS.forEach(function (k) {
      if (k === 'allenamento' && !trainingPlanned) { done++; return; }
      applicable++;
      if (checks[k]) done++; else missing.push(k);
    });
    return { done: done, total: CHECKS.length, applicable: applicable, missing: missing, ok: done >= CHECKS_OK };
  }
  /**
   * Consecutive workdays with >= 5/7 checks, counted back from today (today only once it is ok: a day
   * in progress never breaks the streak). Days where isOff(iso) is true (weekend, at home, pause) are
   * skipped. Nothing before `start` counts.
   * o: {today, start, isOff(iso), schedule}
   */
  function streak(days, o) {
    if (!isISO(o.start) || !isISO(o.today) || o.today < o.start) return 0;
    var isOff = o.isOff || isWeekend;
    var score = function (iso) { return dayScore(days && days[iso], isTrainingDay(iso, o.schedule)); };
    var n = 0;
    if (!isOff(o.today) && score(o.today).ok) n++;
    for (var d = addDays(o.today, -1), g = 0; d >= o.start && g < 4000; d = addDays(d, -1), g++) {
      if (isOff(d)) continue;
      if (!score(d).ok) break;
      n++;
    }
    return n;
  }
  /** Workouts of the week containing `monday`: planned (weekly plan, minus off days and days before start) and done. */
  function weekWorkouts(days, o) {
    var isOff = o.isOff || isWeekend;
    var planned = 0, done = 0;
    for (var i = 0; i < 5; i++) {
      var d = addDays(o.monday, i);
      if (isISO(o.start) && d < o.start) continue;
      if (isOff(d) || !isTrainingDay(d, o.schedule)) continue;
      planned++;
      var day = days && days[d];
      if (day && day.checks && day.checks.allenamento) done++;
    }
    return { planned: planned, done: done };
  }

  // ---------------------------------------------------------------- 12-week cycle
  /** week 1–2 settle, 3–10 cut, 11 deload, 12 check; before the start date: {started: false, daysToStart} */
  function cycleInfo(start, today) {
    if (!isISO(start) || !isISO(today)) return null;
    var d = daysBetween(start, today);
    if (d < 0) return { started: false, daysToStart: -d, week: 0, phase: 'before' };
    var w = Math.floor(d / 7) + 1;
    var phase = w <= 2 ? 'settle' : (w <= 10 ? 'cut' : (w === 11 ? 'deload' : (w === 12 ? 'check' : 'after')));
    return { started: true, daysToStart: 0, week: w, phase: phase };
  }
  /** Weeks 1–2: 2 sets instead of 3; week 11 (deload): 40 % fewer sets. */
  function setsFor(baseSets, week) {
    if (week >= 1 && week <= 2) return Math.min(baseSets, 2);
    if (week === 11) return Math.max(1, Math.round(baseSets * 0.6));
    return baseSets;
  }

  // ---------------------------------------------------------------- weight
  /** {iso: kg} -> [{date, kg}] sorted by date (invalid entries dropped) */
  function weightSeries(map) {
    return Object.keys(map || {}).filter(function (d) { return isISO(d) && isNum(map[d]) && map[d] > 0; })
      .sort().map(function (d) { return { date: d, kg: map[d] }; });
  }
  function latestOnOrBefore(series, iso) {
    var last = null;
    (series || []).forEach(function (p) { if (!iso || p.date <= iso) last = p; });
    return last;
  }
  /** Is a new weigh-in due? every = 7 or 14 days. */
  function weighDue(series, today, every) {
    var last = latestOnOrBefore(series, today);
    if (!last) return { last: null, daysSince: null, due: true };
    var ds = daysBetween(last.date, today);
    return { last: last, daysSince: ds, due: ds >= (every || 7) };
  }
  /**
   * Trend in kg/week: least squares over the weigh-ins of the last `windowDays` (default 42) days.
   * Needs >= 2 weigh-ins at least `minSpanDays` (default 7) apart, otherwise null.
   */
  function weightTrend(series, today, opt) {
    opt = opt || {};
    var win = opt.windowDays || 42, minSpan = opt.minSpanDays || 7;
    var from = addDays(today, -win);
    var pts = (series || []).filter(function (p) { return p.date >= from && p.date <= today; });
    if (pts.length < 2) return null;
    var x0 = pts[0].date;
    var xs = pts.map(function (p) { return daysBetween(x0, p.date); });
    if (xs[xs.length - 1] < minSpan) return null;
    var ys = pts.map(function (p) { return p.kg; });
    var n = xs.length;
    var mx = xs.reduce(function (a, b) { return a + b; }, 0) / n;
    var my = ys.reduce(function (a, b) { return a + b; }, 0) / n;
    var sxx = 0, sxy = 0;
    for (var i = 0; i < n; i++) { sxx += (xs[i] - mx) * (xs[i] - mx); sxy += (xs[i] - mx) * (ys[i] - my); }
    if (!(sxx > 0)) return null;
    var slope = sxy / sxx; // kg per day
    var icpt = my - slope * mx;
    return {
      kgPerWeek: slope * 7, n: n, from: x0, to: pts[n - 1].date,
      at: function (iso) { return icpt + slope * daysBetween(x0, iso); }
    };
  }

  // ---------------------------------------------------------------- export / import
  function buildExport(data, nowIso) {
    var out = {};
    Object.keys(data || {}).forEach(function (k) {
      if (STORE_KEYS.indexOf(k) >= 0 && data[k] !== null && data[k] !== undefined) out[k] = data[k];
    });
    return { app: EXPORT_APP, version: SCHEMA, exported_at: nowIso || null, data: out };
  }
  /** Validates an exported file. -> {ok, data} or {ok: false, error: code} */
  function parseImport(text) {
    if (typeof text !== 'string' || !text.trim()) return { ok: false, error: 'empty' };
    if (text.length > 5e6) return { ok: false, error: 'too_big' };
    var obj;
    try { obj = JSON.parse(text); } catch (e) { return { ok: false, error: 'json' }; }
    if (!obj || typeof obj !== 'object' || obj.app !== EXPORT_APP) return { ok: false, error: 'app' };
    if (!isNum(obj.version) || obj.version > SCHEMA) return { ok: false, error: 'version' };
    var d = obj.data;
    if (!d || typeof d !== 'object' || Array.isArray(d)) return { ok: false, error: 'data' };
    var keys = Object.keys(d);
    if (!keys.length) return { ok: false, error: 'data' };
    for (var i = 0; i < keys.length; i++) {
      if (STORE_KEYS.indexOf(keys[i]) < 0) return { ok: false, error: 'key', key: keys[i] };
    }
    return { ok: true, data: d };
  }

  return {
    CATS: CATS, LEVELS: LEVELS, DEFAULT_GOALS: DEFAULT_GOALS, LIMITS: LIMITS, LUNCH: LUNCH,
    PORTION_IDS: PORTION_IDS, ELSEWHERE_PROT: ELSEWHERE_PROT, EXTRAS: EXTRAS, CHECKS: CHECKS,
    CHECKS_OK: CHECKS_OK, SCHEDULE: SCHEDULE, STORE_KEYS: STORE_KEYS, SCHEMA: SCHEMA,
    isNum: isNum, clamp: clamp, roundTo: roundTo, fold: fold, parseNum: parseNum,
    parseISO: parseISO, isISO: isISO, isoOf: isoOf, addDays: addDays, daysBetween: daysBetween,
    weekdayOf: weekdayOf, mondayOf: mondayOf, isWeekend: isWeekend,
    bmr: bmr, goalsWithDefaults: goalsWithDefaults, targets: targets, zone2: zone2,
    validateProfile: validateProfile, validateGoals: validateGoals,
    dishIndex: dishIndex, dishInfo: dishInfo, lunchEstimate: lunchEstimate,
    classifyLunch: classifyLunch, lunchLevel: lunchLevel,
    shiftLevel: shiftLevel, dinnerLevel: dinnerLevel, dinnerBudget: dinnerBudget, proteinGap: proteinGap,
    extraFor: extraFor, proposeDinners: proposeDinners, recentDinners: recentDinners,
    isTrainingDay: isTrainingDay, trainingToday: trainingToday, dayScore: dayScore, streak: streak,
    weekWorkouts: weekWorkouts, cycleInfo: cycleInfo, setsFor: setsFor,
    weightSeries: weightSeries, latestOnOrBefore: latestOnOrBefore, weighDue: weighDue, weightTrend: weightTrend,
    buildExport: buildExport, parseImport: parseImport
  };
});
