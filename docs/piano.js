/* Piano – daily routine, lunch -> dinner, training plan and weigh-ins (no framework, no build step).
 *
 * Routes: #/piano (Oggi, optional #/piano/oggi/<yyyy-mm-dd>), #/piano/corpo, #/piano/training[/<id>],
 * #/piano/impostazioni. Registered through window.TSP (docs/app.js); logic in window.PianoCore.
 *
 * Privacy: profile, weigh-ins, checks and notes live ONLY in this browser's localStorage
 * (keys tsp.piano.*, through TSP.pstore). Nothing is ever sent anywhere: the only requests are the
 * static files docs/piano/*.json and the Tippspiel data (docs/data/*.json, same loader as the rest
 * of the site, decryption included). All data is inserted as text (TSP.h).
 */
(function () {
  'use strict';
  var T = window.TSP, C = window.PianoCore;
  if (!T || !C || !T.addRoute) return;

  var h = T.h, t = T.t, icon = T.icon, notice = T.notice, chip = T.chip;
  var ps = T.pstore;
  var CATS = T.CATS;

  T.addIcons({
    gear: '<circle cx="12" cy="12" r="3"/><path d="M12 2.8v2.4M12 18.8v2.4M2.8 12h2.4M18.8 12h2.4M5.5 5.5l1.7 1.7M16.8 16.8l1.7 1.7M5.5 18.5l1.7-1.7M16.8 7.2l1.7-1.7"/>',
    coffee: '<path d="M4 9h12v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5V9zM16 10h1.5a2.5 2.5 0 0 1 0 5H16M8 3.5v2.5M12 3.5v2.5"/>',
    lunch: '<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10M16 3c-1.7 1.5-2.5 4-2.5 7h2.5v11"/>',
    snack: '<path d="M12 7c-3.5-2-7 0-7 4.5S8 21 12 19c4 2 7-3 7-7.5S15.5 5 12 7zM12 7c0-2 1-3.5 3-4"/>',
    dinner: '<circle cx="12" cy="13" r="7"/><circle cx="12" cy="13" r="3.5"/><path d="M3 5v5M21 5v5"/>',
    moon: '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
    flame: '<path d="M12 21c-4 0-6.5-2.7-6.5-6.3 0-3.9 3.3-5.7 4-9.7 2.9 1.9 5 4.4 5 7.3.9-.6 1.4-1.6 1.5-2.6 1.8 1.5 2.5 3.4 2.5 5.2 0 3.5-2.6 6.1-6.5 6.1z"/>',
    home: '<path d="M3.5 11 12 4l8.5 7M6 9.5V20h12V9.5M10 20v-5h4v5"/>',
    check: '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>',
    chevl: '<path d="M14.5 5.5 8 12l6.5 6.5"/>',
    chevr: '<path d="M9.5 5.5 16 12l-6.5 6.5"/>'
  });

  // ------------------------------------------------------------------ static content (docs/piano/*.json)
  var contentCache = {};
  function content(name) {
    if (!contentCache[name]) {
      contentCache[name] = fetch('piano/' + name + '.json', { cache: 'no-cache' }).then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      }).catch(function (e) { delete contentCache[name]; throw e; });
    }
    return contentCache[name];
  }
  function optional(p) { return p.then(function (x) { return x; }, function () { return null; }); }
  var dishIdx = null, dishIdxSrc = null;
  function dishIndexOf(table) {
    if (!table) return C.dishIndex(null);
    if (dishIdxSrc !== table) { dishIdx = C.dishIndex(table); dishIdxSrc = table; }
    return dishIdx;
  }
  function L(obj) { return obj ? (obj[T.lang()] || obj.de || '') : ''; }

  // ------------------------------------------------------------------ local state (tsp.piano.*)
  function obj(k) { var v = ps.getJSON(k, null); return v && typeof v === 'object' && !Array.isArray(v) ? v : {}; }
  function touch() { if (!ps.get('v')) ps.setJSON('v', C.SCHEMA); }
  function profile() { var p = ps.getJSON('profile', null); return p && typeof p === 'object' ? p : null; }
  function profileOk() { var p = profile(); return !!(p && C.validateProfile(p).ok); }
  function goals() { return obj('goals'); }
  function settings() {
    var s = obj('settings');
    return {
      startPage: s.startPage === 'heute' ? 'heute' : 'piano', weighEvery: s.weighEvery === 14 ? 14 : 7,
      breakfastText: typeof s.breakfastText === 'string' ? s.breakfastText : '', lastExport: s.lastExport || null
    };
  }
  function saveSettings(patch) {
    var s = obj('settings');
    Object.keys(patch).forEach(function (k) { if (patch[k] === null || patch[k] === undefined) delete s[k]; else s[k] = patch[k]; });
    ps.setJSON('settings', s);
    touch();
  }
  function allDays() { return obj('days'); }
  function dayOf(iso) { return allDays()[iso] || {}; }
  function saveDay(iso, mutate) {
    var all = allDays();
    var d = all[iso] || {};
    mutate(d);
    if (Object.keys(d).length) all[iso] = d; else delete all[iso];
    ps.setJSON('days', all);
    touch();
  }
  function weightMap() { return obj('weights'); }
  function waistMap() { return obj('waist'); }

  // ------------------------------------------------------------------ small helpers
  function todayISO() { return T.romeTodayISO(); }
  function minutesNow() { var p = T.zonedParts(Date.now()); return p.h * 60 + p.mi; }
  function fmtKg(x) { return T.isNum(x) ? T.fmtNum(x, 1) + ' kg' : '–'; }
  function fmtInt(x) { return T.isNum(x) ? T.fmtNum(x, 0) : '–'; }
  function fmtSigned(x, d) { return T.isNum(x) ? (x > 0 ? '+' : (x < 0 ? '−' : '±')) + T.fmtNum(Math.abs(x), d) : '–'; }
  function kpi(label, value, sub, extra) {
    return h('div', { class: 'p-kpi' }, h('span', { class: 'k' }, label), h('span', { class: 'v' }, value),
      sub ? h('span', { class: 'muted tiny' }, sub) : null, extra || null);
  }
  function levelBadge(level, label) {
    return h('span', { class: 'p-level ' + level }, label || t('piano.level.' + level));
  }
  function head(iconName, title, time, extra, now) {
    return h('div', { class: 'p-card-head' }, icon(iconName),
      h('h2', { class: 'card-title' }, title),
      now ? chip(t('piano.now'), 'accent') : null,
      time ? h('span', { class: 'p-time muted small' }, time) : null,
      extra || null);
  }
  /** wrapping group of toggle buttons (aria-pressed) */
  function choices(options, current, onChange, label) {
    return h('div', { class: 'p-choices', role: 'group', 'aria-label': label || null }, options.map(function (o) {
      var on = String(o.value) === String(current);
      return h('button', { type: 'button', class: 'p-choice' + (on ? ' on' : ''), 'aria-pressed': String(on), onclick: function () { onChange(o.value); } }, o.label);
    }));
  }
  function field(label, input, hint, err) {
    return h('label', { class: 'field' + (err ? ' has-err' : '') }, h('span', null, label), input,
      err ? h('span', { class: 'p-err small' }, err) : null,
      hint ? h('span', { class: 'muted tiny' }, hint) : null);
  }
  function numInput(id, value, opts) {
    opts = opts || {};
    return h('input', {
      type: 'text', id: id, inputmode: opts.integer ? 'numeric' : 'decimal', autocomplete: 'off',
      value: value === null || value === undefined ? '' : String(value).replace('.', ','), // DE and IT: decimal comma
      placeholder: opts.placeholder || null, maxlength: '6', class: 'p-num'
    });
  }
  function readNum(input) { return C.parseNum(input.value); }

  // ------------------------------------------------------------------ plan / schedule
  function scheduleOf(workouts) { return (workouts && workouts.schedule) || C.SCHEDULE; }
  function workoutById(workouts, id) {
    return ((workouts && workouts.workouts) || []).filter(function (w) { return w.id === id; })[0] || null;
  }
  /** at home (no food tracking, streak not affected): weekend, switch of the day, or a Tippspiel free day */
  function isHome(iso, ctx) {
    if (C.isWeekend(iso)) return true;
    var d = dayOf(iso);
    if (typeof d.home === 'boolean') return d.home;
    return !!(ctx && ctx.r4 && ctx.r4.free && ctx.r4.free.has(iso));
  }
  function autoHome(iso, ctx) { return !C.isWeekend(iso) && !!(ctx && ctx.r4 && ctx.r4.free && ctx.r4.free.has(iso)); }
  function currentKg(iso) {
    var last = C.latestOnOrBefore(C.weightSeries(weightMap()), iso);
    return last ? last.kg : null;
  }
  function targetsFor(iso) {
    var p = profile();
    if (!p || !C.validateProfile(p).ok) return null;
    return C.targets(p, goals(), currentKg(iso));
  }

  // ------------------------------------------------------------------ lunch of a day
  /** most probable dish per category (not the tip, which is bound by rule 4); tips = today.json + today_alt.json */
  function forecastFor(tips, Wd, iso) {
    var opts = null;
    var Td = (tips || []).filter(function (x) { return x && x.date === iso && x.alternatives; })[0];
    if (Td) {
      opts = {};
      CATS.forEach(function (c) {
        var best = null;
        (Td.alternatives[c] || []).forEach(function (a) { if (a && a.dish && (!best || (a.p || 0) > (best.p || 0))) best = a; });
        opts[c] = best ? [best.dish] : [];
      });
    } else if (Wd && Wd.days) {
      var day = Wd.days.filter(function (x) { return x && x.date === iso; })[0];
      if (day && day.forecast) {
        opts = {};
        CATS.forEach(function (c) { var f = (day.forecast[c] || [])[0]; opts[c] = f && f.dish ? [f.dish] : []; });
      }
    }
    return opts && CATS.some(function (c) { return opts[c].length; }) ? opts : null;
  }
  /** source of the lunch menu: real menu (menus.json or just entered in Eingabe) -> forecast -> unknown */
  function lunchSource(ctx, tips, Wd, iso) {
    if (ctx.locked) return { kind: 'locked' };
    var m = T.menuOf(ctx, iso);
    if (m && m.status === 'free') return { kind: 'free' };
    if (m && m.status === 'served' && m.opts && CATS.some(function (c) { return (m.opts[c] || []).length; })) {
      return { kind: m.pending ? 'entered' : 'menu', opts: m.opts };
    }
    var fc = forecastFor(tips, Wd, iso);
    if (fc) return { kind: 'forecast', opts: fc };
    if ((tips || []).some(function (x) { return x && x.season_over; })) return { kind: 'nomenu' };
    return { kind: 'unknown' };
  }
  /**
   * Lunch of a day: menu (or forecast), the choice "solo primo" / "secondo + contorno" (never all three),
   * estimate and level. Until the choice is made the suggested one is assumed (assumed = true).
   */
  function lunchOf(iso, env) {
    var lu = dayOf(iso).lunch || {};
    var src = lunchSource(env.ctx, env.tips, env.Wd, iso);
    var picks = null;
    if (src.opts) {
      picks = {};
      CATS.forEach(function (c) {
        var o = src.opts[c] || [];
        var chosen = lu.pick && lu.pick[c];
        picks[c] = chosen && o.indexOf(chosen) >= 0 ? chosen : (o[0] || null);
      });
    }
    var choices = C.lunchChoices(env.idx, picks);
    var stored = C.normPortion(lu.portion);
    var portion = stored || choices.suggested || 'secondo';
    var est = C.lunchEstimate(env.idx, picks, portion, { kcal: lu.kcal, prot: lu.prot });
    var cls = C.classifyLunch(est);
    var overridden = C.LEVELS.indexOf(lu.level) >= 0;
    return {
      src: src, picks: picks, est: est, cls: cls, level: overridden ? lu.level : cls.level, overridden: overridden, lu: lu,
      choices: choices, portion: portion, assumed: !stored, carbs: C.carbLunch(est)
    };
  }
  /** "Solo primo (Lasagne)" / "Secondo + contorno (Hühnerbrust + Reis)" */
  function portionText(L0) {
    var p = L0.portion;
    var names = L0.est.items.filter(function (it) { return it.factor > 0 && it.name; }).map(function (it) { return it.name; });
    return t('piano.portion.' + p) + (names.length && p !== 'elsewhere' ? ' (' + names.join(' + ') + ')' : '');
  }

  // ================================================================== VIEW: Oggi
  function loadEnv() {
    return Promise.all([
      T.loadCtx(), T.load('today'), T.load('week'),
      optional(content('dish_nutrition')), optional(content('dinners')), optional(content('workouts')), T.load('today_alt')
    ]).then(function (rs) {
      var Td = T.okData(rs[1]), Ta = T.okData(rs[6]);
      return {
        ctx: rs[0], T: rs[1], Td: Td, Ta: Ta, tips: [Td, Ta].filter(Boolean), Wd: T.okData(rs[2]),
        table: rs[3], idx: dishIndexOf(rs[3]), dinners: rs[4], workouts: rs[5]
      };
    });
  }

  function viewOggi(rest) {
    var today = todayISO();
    var iso = T.isISO(rest[0]) && rest[0] <= today ? rest[0] : today;
    var isToday = iso === today;
    return loadEnv().then(function (env) {
      var out = h('div', { class: 'stack p-oggi' });
      var p = profile();
      var okProfile = profileOk();
      var sched = scheduleOf(env.workouts);
      var tg = targetsFor(iso);
      var home = isHome(iso, env.ctx);

      // ---- head with day navigation
      var prev = T.addDays(iso, -1), next = T.addDays(iso, 1);
      out.appendChild(h('div', { class: 'p-head' },
        h('div', { class: 'p-head-text' },
          h('h1', null, isToday ? t('piano.tab.oggi') : (iso === T.addDays(today, -1) ? t('piano.day.yesterday') : T.fmtWdDM(iso))),
          h('p', { class: 'muted' }, T.fmtLong(iso))),
        h('div', { class: 'p-head-actions' },
          h('a', { class: 'icon-btn', href: '#/piano/oggi/' + prev, 'aria-label': t('piano.day.prev'), title: t('piano.day.prev') }, icon('chevl')),
          isToday ? null : h('a', { class: 'icon-btn', href: next >= today ? '#/piano' : '#/piano/oggi/' + next, 'aria-label': t('piano.day.next'), title: t('piano.day.next') }, icon('chevr')),
          h('a', { class: 'icon-btn', href: '#/piano/impostazioni', 'aria-label': t('piano.set.title'), title: t('piano.set.title') }, icon('gear')))));

      // ---- notices
      var notes = h('div', { class: 'stack-sm' });
      if (!ps.available()) notes.appendChild(notice('danger', t('piano.storageOff')));
      if (!okProfile) {
        notes.appendChild(h('section', { class: 'card p-onboard' },
          h('h2', { class: 'card-title' }, t('piano.onboard.title')),
          h('p', null, t('piano.onboard.text')),
          h('a', { class: 'btn primary', href: '#/piano/impostazioni' }, icon('gear'), t('piano.onboard.btn'))));
      }
      var cyc = okProfile ? C.cycleInfo(p.startDate, iso) : null;
      if (isToday && cyc && !cyc.started) notes.appendChild(notice('info', t('piano.trial', { date: T.fmtWdDM(p.startDate), n: cyc.daysToStart })));
      if (env.ctx.locked) {
        notes.appendChild(notice('info', t('piano.locked'),
          h('button', { type: 'button', class: 'btn small', onclick: function () { T.reloadData(); } }, t('pass.enter'))));
      }
      if (!env.table || !env.dinners) notes.appendChild(notice('warn', t('piano.contentMissing')));
      if (notes.childNodes.length) out.appendChild(notes);

      if (okProfile) out.appendChild(summaryCard(env, iso, today, tg, sched));

      if (home) {
        out.appendChild(homeCard(env, iso));
        return out;
      }

      var lunch = lunchOf(iso, env);
      var training = C.trainingToday(iso, dayOf(iso), sched);
      var nowBlock = isToday ? currentBlock(training) : null;
      var g = C.goalsWithDefaults(goals());

      out.appendChild(breakfastCard(iso, g, nowBlock === 'colazione'));
      if (isToday) {
        var tc = tippCard(env, nowBlock === 'tipp');
        if (tc) out.appendChild(tc);
      }
      out.appendChild(lunchCard(iso, env, lunch, nowBlock === 'pranzo'));
      if (training) out.appendChild(snackCard(g, nowBlock === 'merenda'));
      out.appendChild(trainingCard(env, iso, training, sched, cyc, nowBlock === 'allenamento'));
      out.appendChild(dinnerCard(env, iso, lunch, training, tg, g, nowBlock === 'cena'));
      out.appendChild(eveningCard(iso, C.isTrainingDay(iso, sched), nowBlock === 'sera'));
      out.appendChild(h('div', { class: 'center' },
        h('button', { type: 'button', class: 'link-btn', onclick: function () { saveDay(iso, function (d) { d.home = true; }); T.rerender(); } },
          icon('home'), ' ', t('piano.home.set'))));
      return out;
    });
  }

  /** card highlighted at this time of the day */
  function currentBlock(training) {
    var m = minutesNow();
    if (m < 9 * 60) return 'colazione';
    if (m < 12 * 60) return 'tipp';
    if (m < 15 * 60) return 'pranzo';
    if (m < 17 * 60 + 30) return training ? 'merenda' : 'pranzo';
    if (m < 19 * 60) return training ? 'allenamento' : 'cena';
    if (m < 21 * 60) return 'cena';
    return 'sera';
  }

  function summaryCard(env, iso, today, tg, sched) {
    var p = profile();
    var all = allDays();
    var isOff = function (d) { return isHome(d, env.ctx); };
    var cyc = C.cycleInfo(p.startDate, iso);
    var started = cyc && cyc.started;
    var st = started ? C.streak(all, { today: iso, start: p.startDate, isOff: isOff, schedule: sched }) : 0;
    var ww = C.weekWorkouts(all, { monday: T.mondayOf(iso), start: p.startDate, isOff: isOff, schedule: sched });
    var series = C.weightSeries(weightMap());
    var due = C.weighDue(series, today, settings().weighEvery);
    var weightSub = due.last ? (due.daysSince === 0 ? t('piano.sum.todayW') : t('piano.sum.ago', { n: due.daysSince })) : t('piano.sum.noWeight');
    var dueChip = due.due ? h('a', { class: 'chip warn-chip', href: '#/piano/corpo' }, t('piano.sum.weighDue')) : null;
    var kpis = h('div', { class: 'p-kpis' },
      kpi(t('piano.sum.streak'), started ? t('piano.sum.days', { n: st }) : '–', started ? null : t('piano.sum.fromStart'), null),
      kpi(t('piano.sum.workouts'), started ? ww.done + '/' + ww.planned : '–', t('piano.sum.thisWeek')),
      kpi(t('piano.sum.weight'), due.last ? fmtKg(due.last.kg) : '–', weightSub, dueChip));
    var mon = T.mondayOf(iso);
    var dots = h('div', { class: 'p-week', role: 'list', 'aria-label': t('piano.sum.week') }, [0, 1, 2, 3, 4].map(function (i) {
      var d = T.addDays(mon, i);
      var off = isOff(d);
      var sc = C.dayScore(all[d], C.isTrainingDay(d, sched));
      var state = off ? 'off' : (d > today ? 'future' : (sc.ok ? 'ok' : (d === today ? 'open' : 'miss')));
      var title = T.wdLong(i) + ': ' + (off ? t('piano.dot.off') : (d > today ? '–' : t('piano.dot.score', { n: sc.done })));
      return h('a', { class: 'p-dot ' + state + (d === iso ? ' sel' : ''), role: 'listitem', href: d === today ? '#/piano' : (d < today ? '#/piano/oggi/' + d : null), title: title, 'aria-label': title },
        h('span', { class: 'p-dot-d' }, T.wdShort(i)), h('span', { class: 'p-dot-m', 'aria-hidden': 'true' }));
    }));
    return h('section', { class: 'card p-summary' }, kpis, dots,
      tg ? h('p', { class: 'muted small p-target' }, t('piano.sum.target', { kcal: fmtInt(tg.kcal), prot: tg.protein })) : null,
      started ? h('p', { class: 'muted tiny' }, t('piano.cycle.week', { n: cyc.week, phase: t('piano.phase.' + cyc.phase) })) : null);
  }

  function checkRow(iso, key, label, opts) {
    opts = opts || {};
    var d = dayOf(iso);
    var id = 'chk-' + key;
    var input = h('input', { type: 'checkbox', id: id, checked: !!(d.checks && d.checks[key]), disabled: opts.disabled ? true : null });
    input.addEventListener('change', function () {
      saveDay(iso, function (x) {
        x.checks = x.checks || {};
        if (input.checked) x.checks[key] = true; else delete x.checks[key];
        if (!Object.keys(x.checks).length) delete x.checks;
      });
      T.rerender();
    });
    return h('label', { class: 'check p-check' + (opts.na ? ' na' : '') }, input, h('span', null, label, opts.na ? h('span', { class: 'muted small' }, ' · ' + t('piano.check.na')) : null));
  }

  function breakfastCard(iso, g, now) {
    var txt = settings().breakfastText;
    return h('section', { class: 'card p-meal' + (now ? ' p-now' : '') },
      head('coffee', t('piano.bf.title'), '07:10', null, now),
      h('p', null, txt ? txt : t('piano.bf.text')),
      h('p', { class: 'muted small' }, t('piano.bf.values', { kcal: fmtInt(g.breakfastKcal), prot: fmtInt(g.breakfastProt) }) + ' ' + t('piano.bf.alt')),
      h('p', { class: 'muted small' }, t('piano.bf.coffee')),
      checkRow(iso, 'colazione', t('piano.check.colazione')));
  }

  function tippCard(env, now) {
    if (!env.T || env.T.status !== 'ok') return null;
    // today's tip until 17:00, then the next game day's (switch: TSP.tipDays / tipSwitch, as on the Tipp page)
    var TD = T.tipDays(env.Td || {}, env.Ta);
    var d = TD.d || {};
    if (!d.recommendation || !d.recommendation.vorspeise) return null;
    var S = T.tipSummary(d, env.ctx);
    var cd = T.countdown(S);
    var R = S.isToday ? T.tipResult(env.ctx, S.target) : null;
    var resLine = null;
    if (R) {
      resLine = h('p', { class: 'small p-tipp-res' }, R.tip
        ? t('piano.tipp.result', { n: T.fmtPts(R.points), hits: CATS.filter(function (c) { return R.hits[c]; }).map(T.catShort).join(' ') || '–' })
        : t('piano.tipp.noTip'));
    }
    var el = h('section', { class: 'card p-tipp' + (S.isToday ? '' : ' ahead') + (now ? ' p-now' : '') },
      head('heute', S.isToday ? t('piano.tipp.today') : t('piano.tipp.next', { day: T.fmtWdDM(S.target) }), null, null, now),
      T.tipSwitch(TD),
      h('div', { class: 'p-tipp-body' },
        h('ul', { class: 'p-tipp-dishes' }, CATS.map(function (c) {
          return h('li', null, T.catBadge(c), h('span', { class: 'p-tipp-dish', lang: 'de' }, (S.rec[c] || {}).dish || '–'));
        })),
        h('div', { class: 'cd p-cd' }, cd.val, cd.label)),
      d.provisional ? h('p', { class: 'muted small' }, t('tipd.provisionalShort')) : null,
      resLine,
      S.issues.length ? notice('danger', t('today.recBlocked')) : null,
      h('div', { class: 'btn-row' }, T.copyButton(S.copy, t('today.copy'), 'primary'),
        h('a', { class: 'btn', href: '#/heute' }, t('piano.tipp.details'))));
    cd.start(el);
    return el;
  }

  var SRC_CHIP = { menu: 'ok', entered: 'info', forecast: 'warn-chip', free: 'muted-chip', nomenu: 'muted-chip', unknown: 'muted-chip', locked: 'muted-chip' };

  function lunchCard(iso, env, L0, now) {
    var est = L0.est, lu = L0.lu;
    var srcKind = L0.src.kind;
    var setLunch = function (mut) {
      saveDay(iso, function (d) { d.lunch = d.lunch || {}; mut(d.lunch); if (!Object.keys(d.lunch).length) delete d.lunch; });
      T.rerender();
    };
    var nodes = [];
    nodes.push(head('lunch', t('piano.lunch.title'), '12:00', levelBadge(L0.level), now));
    var srcRow = h('div', { class: 'p-src' }, chip(t('piano.src.' + srcKind), SRC_CHIP[srcKind] || ''),
      est.generic && L0.picks ? chip(t('piano.src.generic'), 'muted-chip') : null);
    nodes.push(srcRow);
    if (L0.picks) {
      var hasPick = false;
      nodes.push(h('ul', { class: 'p-dishes' }, CATS.map(function (c) {
        var it = est.items.filter(function (x) { return x.cat === c; })[0];
        var opts = (L0.src.opts && L0.src.opts[c]) || [];
        var label = opts.length > 1 ? T.selectEl(opts.map(function (o) { return { value: o, label: o }; }), L0.picks[c], function (v) {
          setLunch(function (l) { l.pick = l.pick || {}; l.pick[c] = v; });
        }, T.catName(c)) : h('span', { class: 'p-dish', lang: 'de' }, L0.picks[c] || '–');
        if (opts.length > 1) hasPick = true;
        // kcal of the dish itself; struck through once the choice is made and the dish was not eaten
        var off = !!it && !L0.assumed && !(it.factor > 0);
        var kc = it ? Math.round(it.kcal * (it.factor > 0 ? it.factor : 1)) : null;
        return h('li', { class: 'p-dish-row' + (off ? ' off' : '') }, T.catBadge(c), label,
          h('span', { class: 'p-kcal' }, it ? fmtInt(kc) + ' kcal' : '–'));
      })));
      if (hasPick) nodes.push(h('p', { class: 'muted tiny' }, t('piano.lunch.pickHint')));
    } else {
      nodes.push(h('p', { class: 'muted small' }, t('piano.lunch.noMenu.' + srcKind)));
      if (srcKind === 'unknown') nodes.push(h('a', { class: 'small', href: '#/eingabe' }, t('piano.lunch.enterMenu')));
    }
    // what I take: the first course alone or main course + side – never all three (or elsewhere)
    var ch = L0.choices;
    var chosen = L0.assumed ? null : L0.portion;
    var optBtn = function (p) {
      var c = ch[p];
      var on = chosen === p;
      var names = L0.picks ? c.est.items.filter(function (it) { return it.factor > 0 && it.name; }).map(function (it) { return it.name; }).join(' + ') : '';
      return h('button', {
        type: 'button', class: 'p-opt' + (on ? ' on' : '') + (L0.assumed && L0.portion === p ? ' assumed' : ''),
        'aria-pressed': String(on), disabled: c.available ? null : true,
        onclick: function () { setLunch(function (l) { l.portion = p; }); }
      },
        h('span', { class: 'p-opt-title' }, t('piano.portion.' + p)),
        names ? h('span', { class: 'p-opt-dish', lang: 'de' }, names) : null,
        h('span', { class: 'p-opt-meta' }, fmtInt(c.est.kcal) + ' kcal · ' + fmtInt(c.est.prot) + ' g ' + t('piano.prot')),
        h('span', { class: 'p-opt-chips' }, levelBadge(c.cls.level),
          L0.picks && ch.suggested === p ? chip(t('piano.lunch.suggested'), 'ok') : null));
    };
    var elsewhereOn = chosen === 'elsewhere';
    nodes.push(h('div', { class: 'p-sub' }, h('div', { class: 'p-label' }, t('piano.lunch.choose')),
      h('div', { class: 'p-opts', role: 'group', 'aria-label': t('piano.lunch.choose') }, optBtn('primo'), optBtn('secondo')),
      h('div', { class: 'p-choices' }, h('button', {
        type: 'button', class: 'p-choice' + (elsewhereOn ? ' on' : ''), 'aria-pressed': String(elsewhereOn),
        onclick: function () { setLunch(function (l) { if (elsewhereOn) delete l.portion; else l.portion = 'elsewhere'; }); }
      }, t('piano.portion.elsewhere'))),
      L0.assumed ? h('p', { class: 'muted small' }, t('piano.lunch.assumed', { what: t('piano.portion.' + L0.portion) })) : null,
      C.isLegacyPortion(lu.portion) ? h('p', { class: 'muted small' }, t('piano.lunch.legacy', { what: t('piano.portion.' + lu.portion) })) : null));
    if (chosen === 'elsewhere') {
      var kIn = numInput('lunch-kcal', lu.kcal, { integer: true, placeholder: 'kcal' });
      var pIn = numInput('lunch-prot', lu.prot, { integer: true, placeholder: String(C.ELSEWHERE_PROT) });
      var save = function () {
        var k = readNum(kIn), pr = readNum(pIn);
        setLunch(function (l) {
          if (T.isNum(k) && k >= 0 && k <= 4000) l.kcal = Math.round(k); else delete l.kcal;
          if (T.isNum(pr) && pr >= 0 && pr <= 300) l.prot = Math.round(pr); else delete l.prot;
        });
      };
      kIn.addEventListener('change', save);
      pIn.addEventListener('change', save);
      nodes.push(h('div', { class: 'form-grid two p-elsewhere' },
        field(t('piano.lunch.kcal'), kIn), field(t('piano.lunch.prot'), pIn, t('piano.lunch.protHint', { n: C.ELSEWHERE_PROT }))));
    }
    // totals and level
    var totals = T.isNum(est.kcal) ? t('piano.lunch.total', { kcal: fmtInt(est.kcal), prot: fmtInt(est.prot) }) : t('piano.lunch.totalUnknown');
    nodes.push(h('div', { class: 'p-total' }, h('strong', null, totals),
      est.protAssumed ? h('span', { class: 'muted small' }, ' ' + t('piano.lunch.protAssumed')) : null));
    var lim = L0.cls.limits || C.LUNCH_PART;
    nodes.push(h('p', { class: 'small' }, levelBadge(L0.level), ' ',
      L0.overridden ? t('piano.lunch.manualLevel') : L0.cls.reasons.map(function (r) { return t('piano.why.' + r, { red: lim.red, green: lim.green }); }).join(' · ')));
    nodes.push(h('details', { class: 'p-more' }, h('summary', null, t('piano.lunch.changeLevel')),
      choices([{ value: '', label: t('piano.level.auto') }].concat(C.LEVELS.map(function (l) { return { value: l, label: t('piano.level.' + l) }; })),
        L0.overridden ? lu.level : '', function (v) { setLunch(function (l) { if (v) l.level = v; else delete l.level; }); }, t('piano.lunch.changeLevel')),
      h('p', { class: 'muted tiny' }, t('piano.lunch.rules'))));
    nodes.push(h('p', { class: 'muted small' }, t('piano.lunch.walk')));
    return h('section', { class: 'card p-lunch' + (now ? ' p-now' : '') }, nodes);
  }

  function snackCard(g, now) {
    return h('section', { class: 'card p-meal' + (now ? ' p-now' : '') },
      head('snack', t('piano.snack.title'), '15:20', null, now),
      h('p', null, t('piano.snack.text', { kcal: fmtInt(g.snackKcal), prot: fmtInt(g.snackProt) })));
  }

  function trainingCard(env, iso, training, sched, cyc, now) {
    var planned = C.isTrainingDay(iso, sched);
    var wid = sched[C.weekdayOf(iso)];
    var w = planned ? workoutById(env.workouts, wid) : null;
    var nodes = [head('training', t('piano.train.title'), planned ? '17:45–18:45' : null, null, now)];
    if (planned) {
      nodes.push(h('p', null, w ? h('a', { href: '#/piano/training/' + encodeURIComponent(w.id) }, L(w.name)) : t('piano.train.planned'),
        w ? h('span', { class: 'muted small' }, ' · ~' + w.minutes + ' min') : null));
      if (cyc && !cyc.started) nodes.push(h('p', { class: 'muted small' }, t('piano.train.trialNote')));
      else if (cyc && cyc.week >= 1 && cyc.week <= 2) nodes.push(h('p', { class: 'muted small' }, t('piano.train.settleNote')));
    } else {
      nodes.push(h('p', null, t('piano.train.rest')));
    }
    var d = dayOf(iso);
    var overridden = typeof d.training === 'boolean';
    nodes.push(h('div', { class: 'p-sub' }, h('div', { class: 'p-label' }, t('piano.train.today')),
      choices([{ value: 'yes', label: t('piano.yes') }, { value: 'no', label: t('piano.no') }], training ? 'yes' : 'no', function (v) {
        var want = v === 'yes';
        saveDay(iso, function (x) { if (want === C.isTrainingDay(iso, sched)) delete x.training; else x.training = want; });
        T.rerender();
      }, t('piano.train.today')),
      h('p', { class: 'muted tiny' }, overridden ? t('piano.train.overridden') : t('piano.train.effect'))));
    return h('section', { class: 'card p-train' + (now ? ' p-now' : '') }, nodes);
  }

  function recipeDetails(r) {
    var lang = T.lang();
    return h('details', { class: 'p-recipe-more' }, h('summary', null, t('piano.dinner.howto')),
      h('ul', { class: 'plain p-ingr' }, r.ingredients.map(function (i) {
        var q = i.qty === null ? '' : T.fmtNum(i.qty, i.qty % 1 ? 1 : 0) + ' ' + t('piano.unit.' + i.unit + (i.qty > 1 ? '.n' : '.1')) + ' ';
        return h('li', null, q + (i[lang] || i.de));
      })),
      h('ol', { class: 'plain-ol p-steps' }, (r.steps[lang] || r.steps.de).map(function (s) { return h('li', null, s); })));
  }

  function dinnerCard(env, iso, L0, training, tg, g, now) {
    var lunchLvl = L0.level;
    var lvl = C.dinnerLevel(lunchLvl, training, L0.carbs);
    var capped = lvl !== C.dinnerLevel(lunchLvl, training);
    var nodes = [head('dinner', t('piano.dinner.title'), '19:15', levelBadge(lvl), now)];
    var data = env.dinners;
    // what the dinner is based on: the lunch really chosen (or the suggested one until the choice is made)
    if (T.isNum(L0.est.kcal) && !L0.est.unknown) {
      nodes.push(h('p', { class: 'small p-lunchline' }, t('piano.dinner.lunchLine', { what: portionText(L0), kcal: fmtInt(L0.est.kcal), prot: fmtInt(L0.est.prot) }),
        L0.assumed ? h('span', { class: 'muted' }, ' ' + t('piano.dinner.lunchAssumed')) : null));
    }
    var why = capped ? t('piano.dinner.carbCap', { dinner: t('piano.level.' + lvl) })
      : t(training && lvl !== lunchLvl ? 'piano.dinner.levelUp' : 'piano.dinner.levelSame', { lunch: t('piano.level.' + lunchLvl), dinner: t('piano.level.' + lvl) });
    nodes.push(h('p', { class: 'small' }, why + (data && data.levels && data.levels[lvl] ? ' ' + L(data.levels[lvl]) : '')));
    var budget = null, gap = null;
    var lunchKcal = T.isNum(L0.est.kcal) ? L0.est.kcal : null;
    if (tg && lunchKcal !== null) {
      budget = C.dinnerBudget({ targetKcal: tg.kcal, lunchKcal: lunchKcal, training: training, goals: goals() });
      gap = C.proteinGap({ targetProt: tg.protein, lunchProt: L0.est.prot, training: training, goals: goals() });
      nodes.push(h('div', { class: 'p-budget' },
        kpi(t('piano.dinner.budget'), fmtInt(budget.kcal) + ' kcal', budget.clamped ? t('piano.dinner.clamped.' + budget.clamped) : null),
        kpi(t('piano.dinner.protein'), '~' + gap + ' g')));
      nodes.push(h('p', { class: 'muted tiny' }, t('piano.dinner.formula', {
        target: fmtInt(tg.kcal), bf: fmtInt(budget.breakfast), snack: fmtInt(budget.snack), coffee: fmtInt(budget.coffee), lunch: fmtInt(lunchKcal)
      })));
    } else if (!tg) {
      nodes.push(h('p', { class: 'muted small' }, t('piano.dinner.noProfile')));
    }
    if (!data || !data.recipes) return h('section', { class: 'card p-dinner' + (now ? ' p-now' : '') }, nodes);

    var chosenId = (dayOf(iso).dinner || {}).id || null;
    var recent = C.recentDinners(allDays(), iso, 3);
    var props = C.proposeDinners(data.recipes, {
      level: lvl, budget: budget ? budget.kcal : 1e9, proteinGap: gap === null ? 50 : gap, recent: recent, n: 3
    });
    if (chosenId && !props.some(function (x) { return x.recipe.id === chosenId; })) {
      var ch = data.recipes.filter(function (r) { return r.id === chosenId; })[0];
      if (ch) props.unshift({ recipe: ch, leftover: budget ? budget.kcal - ch.kcal : 0, extra: budget ? C.extraFor(budget.kcal - ch.kcal, (gap || 0) - ch.prot) : null, otherLevel: ch.level !== lvl, recent: false, overBudget: budget ? ch.kcal > budget.kcal : false });
    }
    nodes.push(h('h3', { class: 'sub-title' }, t('piano.dinner.proposals')));
    if (budget && props.length && props.every(function (x) { return x.overBudget; })) nodes.push(notice('warn', t('piano.dinner.noneFits')));
    else if (props.length && props.every(function (x) { return x.otherLevel; })) nodes.push(notice('info', t('piano.dinner.fallback')));
    nodes.push(h('ul', { class: 'p-recipes' }, props.map(function (x) {
      var r = x.recipe;
      var chosen = r.id === chosenId;
      var flags = [];
      if (x.otherLevel) flags.push(chip(t('piano.level.' + r.level), 'p-lv-' + r.level));
      if (x.recent) flags.push(chip(t('piano.dinner.recent'), 'muted-chip'));
      if (x.overBudget) flags.push(chip(t('piano.dinner.over'), 'danger'));
      (r.tags || []).forEach(function (tag) { flags.push(chip(t('piano.tag.' + tag), 'muted-chip')); });
      var extra = budget && x.extra && !x.overBudget && data.extras && data.extras[x.extra.id]
        ? h('p', { class: 'small p-extra' }, t('piano.dinner.extra', { n: fmtInt(x.leftover), what: L(data.extras[x.extra.id]) }))
        : null;
      return h('li', { class: 'p-recipe' + (chosen ? ' chosen' : '') },
        h('div', { class: 'p-recipe-top' },
          h('div', { class: 'p-recipe-name' }, L(r.name)),
          h('button', {
            type: 'button', class: 'btn small' + (chosen ? ' done' : ''), 'aria-pressed': String(chosen),
            onclick: function () { saveDay(iso, function (d) { if (chosen) delete d.dinner; else d.dinner = { id: r.id }; }); T.rerender(); }
          }, chosen ? t('piano.dinner.chosen') : t('piano.dinner.choose'))),
        h('div', { class: 'p-recipe-meta muted small' }, fmtInt(r.kcal) + ' kcal · ' + r.prot + ' g ' + t('piano.prot') + ' · ' + r.minutes + ' min' +
          (r.servings > 1 ? ' · ' + t('piano.dinner.servings', { n: r.servings }) : '')),
        flags.length ? h('div', { class: 'chips wrap' }, flags) : null,
        extra, recipeDetails(r));
    })));
    return h('section', { class: 'card p-dinner' + (now ? ' p-now' : '') }, nodes);
  }

  function eveningCard(iso, trainingPlanned, now) {
    var sc = C.dayScore(dayOf(iso), trainingPlanned);
    return h('section', { class: 'card p-evening' + (now ? ' p-now' : '') },
      head('moon', t('piano.evening.title'), null, h('span', { class: 'p-score' + (sc.ok ? ' ok' : '') }, t('piano.evening.score', { n: sc.done, total: sc.total })), now),
      h('p', { class: 'muted small' }, t('piano.evening.hint')),
      h('div', { class: 'p-checks' },
        checkRow(iso, 'passi', t('piano.check.passi')),
        trainingPlanned ? checkRow(iso, 'allenamento', t('piano.check.allenamento')) : checkRow(iso, 'allenamento', t('piano.check.allenamento'), { na: true, disabled: true }),
        checkRow(iso, 'cena', t('piano.check.cena')),
        checkRow(iso, 'acqua', t('piano.check.acqua')),
        checkRow(iso, 'snack', t('piano.check.snack')),
        checkRow(iso, 'letto', t('piano.check.letto'))),
      h('p', { class: 'muted tiny' }, t('piano.evening.rule')));
  }

  function homeCard(env, iso) {
    var d = dayOf(iso);
    var weekend = C.isWeekend(iso);
    var auto = autoHome(iso, env.ctx) && typeof d.home !== 'boolean';
    var out = h('section', { class: 'card p-home' },
      head('home', t('piano.home.title')),
      h('p', null, t('piano.home.text')),
      h('ul', { class: 'plain' }, h('li', null, t('piano.home.rule1')), h('li', null, t('piano.home.rule2'))),
      h('p', { class: 'muted small' }, t('piano.home.drinks')),
      checkRow(iso, 'uscita', t('piano.home.walkDone')));
    if (!weekend) {
      out.appendChild(h('p', { class: 'muted small' }, auto ? t('piano.home.autoFree') : t('piano.home.manual')));
      out.appendChild(h('button', {
        type: 'button', class: 'btn small', onclick: function () {
          saveDay(iso, function (x) { if (auto) x.home = false; else delete x.home; });
          T.rerender();
        }
      }, t('piano.home.unset')));
    }
    var due = C.weighDue(C.weightSeries(weightMap()), todayISO(), settings().weighEvery);
    if (profileOk() && due.due) {
      out.appendChild(notice('info', due.last ? t('piano.home.weigh', { n: due.daysSince }) : t('piano.home.weighFirst'),
        h('a', { href: '#/piano/corpo' }, t('piano.body.add'))));
    }
    return out;
  }

  // ================================================================== VIEW: Corpo (weigh-ins)
  function viewCorpo() {
    var today = todayISO();
    var p = profile();
    var series = C.weightSeries(weightMap());
    var wmap = waistMap();
    var st = settings();
    var out = h('div', { class: 'stack p-corpo' });
    out.appendChild(h('div', { class: 'page-head' }, h('h1', null, t('piano.tab.corpo')), h('p', { class: 'muted' }, t('piano.body.sub'))));
    if (!ps.available()) out.appendChild(notice('danger', t('piano.storageOff')));

    // ---- new weigh-in
    var dIn = h('input', { type: 'date', id: 'w-date', value: today, max: today, required: true });
    var kgIn = numInput('w-kg', null, { placeholder: 'kg' });
    var cmIn = numInput('w-cm', null, { placeholder: 'cm' });
    var status = h('div', { class: 'form-status', 'aria-live': 'polite' });
    var fillFor = function () {
      var d = dIn.value;
      var m = weightMap();
      kgIn.value = T.isNum(m[d]) ? T.fmtNum(m[d], 1) : '';
      cmIn.value = T.isNum(wmap[d]) ? T.fmtNum(wmap[d], 1) : '';
    };
    dIn.addEventListener('change', fillFor);
    var form = h('form', {
      class: 'card form', novalidate: true, onsubmit: function (e) {
        e.preventDefault();
        var d = dIn.value, kg = readNum(kgIn), cm = readNum(cmIn);
        if (!T.isISO(d) || d > today) { status.replaceChildren(notice('danger', t('piano.body.badDate'))); return; }
        var okKg = T.isNum(kg) && kg >= C.LIMITS.kg[0] && kg <= C.LIMITS.kg[1];
        var okCm = T.isNum(cm) && cm >= C.LIMITS.waistCm[0] && cm <= C.LIMITS.waistCm[1];
        if (kgIn.value.trim() && !okKg) { status.replaceChildren(notice('danger', t('piano.body.badKg'))); return; }
        if (cmIn.value.trim() && !okCm) { status.replaceChildren(notice('danger', t('piano.body.badCm'))); return; }
        if (!okKg && !okCm) { status.replaceChildren(notice('danger', t('piano.body.needOne'))); return; }
        if (okKg) { var m = weightMap(); m[d] = Math.round(kg * 10) / 10; ps.setJSON('weights', m); }
        if (okCm) { var w = waistMap(); w[d] = Math.round(cm * 10) / 10; ps.setJSON('waist', w); }
        touch();
        T.toast(t('piano.saved'), 'ok');
        T.rerender();
      }
    },
      h('h2', { class: 'card-title' }, icon('corpo'), t('piano.body.add')),
      h('div', { class: 'form-grid three' }, field(t('col.date'), dIn), field(t('piano.body.kg'), kgIn), field(t('piano.body.waist'), cmIn, t('piano.body.waistHint'))),
      h('p', { class: 'muted tiny' }, t('piano.body.howto', { n: st.weighEvery })),
      h('button', { type: 'submit', class: 'btn primary big' }, t('piano.save')), status);
    fillFor();
    out.appendChild(form);

    // ---- summary
    var last = C.latestOnOrBefore(series, today);
    var startKg = p && C.isNum(C.parseNum(p.startWeightKg)) ? C.parseNum(p.startWeightKg) : (series[0] ? series[0].kg : null);
    var trend = C.weightTrend(series, today);
    var due = C.weighDue(series, today, st.weighEvery);
    var diff = last && T.isNum(startKg) ? last.kg - startKg : null;
    out.appendChild(h('section', { class: 'card' },
      h('h2', { class: 'card-title' }, t('piano.body.summary')),
      h('div', { class: 'p-kpis' },
        kpi(t('piano.body.start'), fmtKg(startKg), p && p.startDate ? T.fmtDM(p.startDate) : null),
        kpi(t('piano.body.last'), last ? fmtKg(last.kg) : '–', last ? T.fmtDM(last.date) : null),
        kpi(t('piano.body.change'), diff === null ? '–' : fmtSigned(diff, 1) + ' kg', diff !== null && startKg ? fmtSigned(diff / startKg * 100, 1) + ' %' : null)),
      h('p', { class: 'small' }, trend
        ? t('piano.body.trend', { v: fmtSigned(trend.kgPerWeek, 2), n: trend.n, from: T.fmtDM(trend.from) })
        : t('piano.body.noTrend')),
      h('p', { class: 'muted small' }, due.last ? (due.due ? t('piano.body.dueNow') : t('piano.body.dueIn', { n: st.weighEvery - due.daysSince })) : t('piano.body.first')),
      h('p', { class: 'muted tiny' }, t('piano.estimates'))));

    // ---- chart
    if (series.length >= 2) {
      var lastDate = series[series.length - 1].date;
      out.appendChild(h('section', { class: 'card' }, h('h2', { class: 'card-title' }, t('piano.body.chart')),
        T.chartBox(240, t('piano.body.chart'), function (col) {
          var ds = [{
            label: t('piano.body.kg'), data: series.map(function (pt) { return { x: C.parseISO(pt.date), y: pt.kg }; }),
            borderColor: col.series[0], backgroundColor: col.series[0], pointRadius: 4, pointHoverRadius: 6, borderWidth: 2, showLine: true
          }];
          if (trend) {
            ds.push({
              label: t('piano.body.trendLine'), data: [{ x: C.parseISO(trend.from), y: trend.at(trend.from) }, { x: C.parseISO(lastDate), y: trend.at(lastDate) }],
              borderColor: col.muted, backgroundColor: col.muted, borderDash: [6, 4], borderWidth: 1.5, pointRadius: 0, pointHoverRadius: 0, showLine: true
            });
          }
          return {
            type: 'scatter', data: { datasets: ds },
            options: {
              responsive: true, maintainAspectRatio: false, animation: false,
              plugins: {
                legend: { labels: { color: col.text2, boxWidth: 14, usePointStyle: true } },
                tooltip: Object.assign(T.tooltipOpts(col), { callbacks: { label: function (c) { return ' ' + T.fmtDM(C.isoOf(c.raw.x)) + ': ' + T.fmtNum(c.raw.y, 1) + ' kg'; } } })
              },
              scales: {
                x: T.axisOpts(col, { type: 'linear', ticks: { color: col.muted, maxTicksLimit: 6, callback: function (v) { return T.fmtDM(C.isoOf(v)); } } }),
                y: T.axisOpts(col, { ticks: { color: col.muted, maxTicksLimit: 6, callback: function (v) { return T.fmtNum(v, 1); } } })
              }
            }
          };
        })));
    }

    // ---- list
    var dates = Object.keys(weightMap()).concat(Object.keys(wmap)).filter(T.isISO)
      .filter(function (d, i, a) { return a.indexOf(d) === i; }).sort().reverse();
    if (dates.length) {
      var wm = weightMap();
      var rows = dates.map(function (d) {
        var prevW = series.filter(function (pt) { return pt.date < d; }).pop();
        var dlt = T.isNum(wm[d]) && prevW ? wm[d] - prevW.kg : null;
        return [T.fmtDMY(d), T.isNum(wm[d]) ? T.fmtNum(wm[d], 1) : '–', dlt === null ? '–' : fmtSigned(dlt, 1), T.isNum(wmap[d]) ? T.fmtNum(wmap[d], 1) : '–',
          h('button', {
            type: 'button', class: 'btn small danger-btn', 'aria-label': t('piano.delete') + ' ' + T.fmtDMY(d), onclick: function () {
              if (!window.confirm(t('piano.body.delConfirm', { date: T.fmtDMY(d) }))) return;
              var a = weightMap(); delete a[d]; ps.setJSON('weights', a);
              var b = waistMap(); delete b[d]; ps.setJSON('waist', b);
              T.rerender();
            }
          }, '×')];
      });
      out.appendChild(h('section', { class: 'card' }, h('h2', { class: 'card-title' }, t('piano.body.list')),
        T.table([{ label: t('col.date') }, { label: 'kg', num: true }, { label: 'Δ', num: true }, { label: t('piano.body.waistShort'), num: true }, { label: '' }], rows, { cls: 'compact' })));
    }
    return out;
  }

  // ================================================================== VIEW: Training (plan, read only)
  function viewTraining(rest) {
    return content('workouts').then(function (W) {
      var today = todayISO();
      var p = profile();
      var cyc = p && C.isISO(p.startDate) ? C.cycleInfo(p.startDate, today) : null;
      var week = cyc ? Math.max(1, cyc.week) : 0; // before the start: already show week 1 (settling in)
      var sched = scheduleOf(W);
      var todayId = sched[C.weekdayOf(today)];
      var openId = rest[0] || todayId || null;
      var out = h('div', { class: 'stack p-training' });
      out.appendChild(h('div', { class: 'page-head' }, h('h1', null, t('piano.tab.training')),
        h('p', { class: 'muted' }, cyc ? (cyc.started ? t('piano.cycle.week', { n: cyc.week, phase: t('piano.phase.' + cyc.phase) }) : t('piano.train.startsOn', { date: T.fmtWdDM(p.startDate), n: cyc.daysToStart })) : t('piano.train.noStart')),
        cyc && !cyc.started ? h('p', { class: 'muted small' }, t('piano.train.week1Preview')) : null));

      // ---- week plan
      var mon = T.mondayOf(today);
      out.appendChild(h('section', { class: 'card' }, h('h2', { class: 'card-title' }, t('piano.train.week')),
        h('ul', { class: 'p-plan' }, [0, 1, 2, 3, 4, 5].map(function (i) {
          var d = T.addDays(mon, i);
          var id = sched[i];
          var w = id ? workoutById(W, id) : null;
          var label = i === 5 ? t('piano.train.weekend') : (w ? L(w.name) : t('piano.train.restShort'));
          return h('li', { class: 'p-plan-row' + (d === today || (i === 5 && C.weekdayOf(today) >= 5) ? ' today' : '') },
            h('span', { class: 'p-plan-day' }, i === 5 ? T.wdShort(5) + '–' + T.wdShort(6) : T.wdShort(i)),
            h('span', { class: 'p-plan-what' }, w ? h('a', { href: '#/piano/training/' + encodeURIComponent(w.id) }, label) : label,
              w ? h('span', { class: 'muted small' }, ' · ~' + w.minutes + ' min') : null));
        }))));

      // ---- rules
      var z = p ? C.zone2(p.age) : null;
      out.appendChild(h('details', { class: 'card p-rules' }, h('summary', { class: 'card-title' }, t('piano.train.rules')),
        h('ul', { class: 'plain' }, (W.rules || []).map(function (r) { return h('li', null, L(r)); })),
        h('p', { class: 'small' }, z ? L(W.zone2).replace('{lo}', z[0]).replace('{hi}', z[1]) : L(W.zone2NoAge)),
        h('p', { class: 'small muted' }, L(W.note))));

      // ---- workouts
      (W.workouts || []).forEach(function (w) {
        var isToday = w.id === todayId;
        var det = h('details', { class: 'card p-workout' + (isToday ? ' today' : ''), id: 'w-' + w.id, open: w.id === openId ? true : null },
          h('summary', { class: 'card-title' },
            h('span', { class: 'p-wname' }, L(w.name), h('span', { class: 'muted small p-wmin' }, ' · ~' + w.minutes + ' min')),
            isToday ? chip(t('week.today'), 'accent') : null),
          w.intro ? h('p', { class: 'small' }, L(w.intro)) : null,
          w.rounds ? h('p', { class: 'small strong' }, t('piano.train.rounds', { n: w.rounds })) : null,
          h('ol', { class: 'p-exlist' }, w.exercises.map(function (e) { return exerciseItem(e, week); })),
          w.finisher ? h('p', { class: 'small' }, L(w.finisher)) : null,
          w.optional ? h('p', { class: 'small muted' }, L(w.optional)) : null);
        out.appendChild(det);
      });
      if (openId) T.mount(function () { var el = document.getElementById('w-' + openId); if (el && rest[0]) el.scrollIntoView({ block: 'start' }); });
      return out;
    }, function () {
      return T.emptyState(t('piano.contentMissing'), null);
    });
  }

  function exerciseItem(e, week) {
    var variantOn = e.variant && week >= e.variant.fromWeek;
    var name = variantOn ? L(e.variant.name) : L(e.name);
    var tech = variantOn ? L(e.variant.tech) : L(e.tech);
    var sets = week ? C.setsFor(e.sets, week) : e.sets;
    var reps = e.reps[0] === e.reps[1] ? String(e.reps[0]) : e.reps[0] + '–' + e.reps[1];
    var dose = (sets > 1 ? sets + ' × ' : '') + reps + (e.unit === 'sec' ? ' s' : '') + (e.perSide ? ' ' + t('piano.train.perSide') : '');
    var rest = e.rest && e.rest[1] ? t('piano.train.rest2', { a: e.rest[0], b: e.rest[1] }) : '';
    var notYet = e.fromWeek && week < e.fromWeek;
    return h('li', { class: 'p-ex' + (notYet ? ' later' : '') },
      h('div', { class: 'p-ex-top' }, h('span', { class: 'p-ex-name' }, name), h('span', { class: 'p-ex-dose' }, dose)),
      h('div', { class: 'muted small' }, rest, notYet ? chip(t('piano.train.fromWeek', { n: e.fromWeek }), 'info') : null,
        e.variant && !variantOn ? h('span', null, ' · ' + t('piano.train.variantFrom', { n: e.variant.fromWeek, name: L(e.variant.name) })) : null),
      h('p', { class: 'small' }, tech),
      h('details', { class: 'p-alt small' }, h('summary', null, t('piano.train.alt')), h('p', null, L(e.alt))));
  }

  // ================================================================== VIEW: Impostazioni
  var ACTIVITY = [1.2, 1.3, 1.4, 1.45, 1.5, 1.55, 1.6, 1.7, 1.8];
  var DEFICITS = [300, 400, 500, 600, 700, 800, 900, 1000];
  function viewImpostazioni() {
    var p = profile() || {};
    var g = goals();
    var gd = C.goalsWithDefaults(g);
    var st = settings();
    var out = h('div', { class: 'stack p-settings' });
    out.appendChild(h('div', { class: 'page-head' }, h('h1', null, t('piano.set.title')), h('p', { class: 'muted' }, t('piano.set.sub'))));
    if (!ps.available()) out.appendChild(notice('danger', t('piano.storageOff')));

    // ---- profile + goals
    var sex = p.sex === 'f' ? 'f' : (p.sex === 'm' ? 'm' : '');
    var sexWrap = h('div');
    var renderSex = function () {
      sexWrap.replaceChildren(choices([{ value: 'm', label: t('piano.set.male') }, { value: 'f', label: t('piano.set.female') }], sex, function (v) { sex = v; renderSex(); }, t('piano.set.sex')));
    };
    renderSex();
    var ageIn = numInput('p-age', p.age, { integer: true });
    var hIn = numInput('p-height', p.heightCm, { integer: true, placeholder: 'cm' });
    var kgIn = numInput('p-kg', p.startWeightKg, { placeholder: 'kg' });
    var dIn = h('input', { type: 'date', id: 'p-start', value: C.isISO(p.startDate) ? p.startDate : '' });
    var actSel = T.selectEl(ACTIVITY.map(function (a) { return { value: a, label: T.fmtNum(a, 2) + ' – ' + t('piano.act.' + String(a).replace('.', '_')) }; }),
      ACTIVITY.indexOf(gd.activity) >= 0 ? gd.activity : 1.45, function () {}, t('piano.set.activity'), 'p-activity');
    var defSel = T.selectEl(DEFICITS.map(function (d) { return { value: d, label: d + ' kcal' }; }), DEFICITS.indexOf(gd.deficit) >= 0 ? gd.deficit : 700, function () {}, t('piano.set.deficit'), 'p-deficit');
    var protIn = numInput('p-prot', g.proteinG, { integer: true, placeholder: t('piano.set.auto') });
    var bfK = numInput('p-bfk', gd.breakfastKcal, { integer: true });
    var bfP = numInput('p-bfp', gd.breakfastProt, { integer: true });
    var bfText = h('input', { type: 'text', id: 'p-bftext', value: st.breakfastText, maxlength: '140', autocomplete: 'off', placeholder: t('piano.bf.text') });
    var everyWrap = h('div');
    var every = st.weighEvery;
    var renderEvery = function () {
      everyWrap.replaceChildren(choices([{ value: 7, label: t('piano.set.every7') }, { value: 14, label: t('piano.set.every14') }], every, function (v) { every = +v; renderEvery(); }, t('piano.set.weighEvery')));
    };
    renderEvery();
    var status = h('div', { class: 'form-status', 'aria-live': 'polite' });
    var preview = h('div', { class: 'p-preview' });
    var collect = function () {
      return {
        profile: { sex: sex, age: readNum(ageIn), heightCm: readNum(hIn), startWeightKg: readNum(kgIn), startDate: dIn.value },
        goals: { activity: +actSel.value, deficit: +defSel.value, proteinG: protIn.value.trim() ? readNum(protIn) : null, breakfastKcal: readNum(bfK), breakfastProt: readNum(bfP) }
      };
    };
    var updPreview = function () {
      var v = collect();
      var tg = C.validateProfile(v.profile).ok ? C.targets(v.profile, v.goals, currentKg(todayISO())) : null;
      preview.replaceChildren(tg
        ? h('div', null,
          h('div', { class: 'p-kpis' }, kpi(t('piano.set.bmr'), fmtInt(tg.bmr) + ' kcal'), kpi(t('piano.set.tdee'), fmtInt(tg.tdee) + ' kcal'),
            kpi(t('piano.set.target'), fmtInt(tg.kcal) + ' kcal', t('piano.set.protTarget', { n: tg.protein }))),
          h('p', { class: 'muted tiny' }, t('piano.set.weightUsed', { kg: T.fmtNum(tg.kg, 1) }) + ' ' + t('piano.estimates')))
        : h('p', { class: 'muted small' }, t('piano.set.previewMissing')));
    };
    [ageIn, hIn, kgIn, dIn, protIn, bfK, bfP].forEach(function (el) { el.addEventListener('input', updPreview); el.addEventListener('change', updPreview); });
    actSel.addEventListener('change', updPreview);
    defSel.addEventListener('change', updPreview);
    var save = function (e) {
      e.preventDefault();
      var v = collect();
      var vp = C.validateProfile(v.profile), vg = C.validateGoals(v.goals);
      if (!vp.ok || !vg.ok) {
        var errs = Object.assign({}, vp.errors, vg.errors);
        status.replaceChildren(notice('danger', t('piano.set.invalid', { fields: Object.keys(errs).map(function (k) { return t('piano.set.f.' + k); }).join(', ') })));
        return;
      }
      var first = !profileOk();
      ps.setJSON('profile', {
        sex: v.profile.sex, age: Math.round(v.profile.age), heightCm: Math.round(v.profile.heightCm),
        startWeightKg: Math.round(v.profile.startWeightKg * 10) / 10, startDate: v.profile.startDate
      });
      var ng = { activity: v.goals.activity, deficit: v.goals.deficit, breakfastKcal: Math.round(v.goals.breakfastKcal), breakfastProt: Math.round(v.goals.breakfastProt) };
      if (T.isNum(v.goals.proteinG)) ng.proteinG = Math.round(v.goals.proteinG);
      ps.setJSON('goals', ng);
      saveSettings({ weighEvery: every, breakfastText: bfText.value.trim() || null });
      if (first && navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(function () { /* ignore */ });
      T.toast(t('piano.saved'), 'ok');
      T.rerender();
    };
    out.appendChild(h('form', { class: 'card form p-form', novalidate: true, onsubmit: save },
      h('h2', { class: 'card-title' }, t('piano.set.profile')),
      h('p', { class: 'muted small' }, t('piano.set.privacy')),
      h('div', { class: 'field' }, h('span', null, t('piano.set.sex')), sexWrap),
      h('div', { class: 'form-grid three' }, field(t('piano.set.f.age'), ageIn), field(t('piano.set.f.heightCm'), hIn), field(t('piano.set.f.startWeightKg'), kgIn)),
      field(t('piano.set.f.startDate'), dIn, t('piano.set.startHint')),
      h('h3', { class: 'sub-title' }, t('piano.set.goals')),
      h('div', { class: 'form-grid two' }, field(t('piano.set.activity'), actSel, t('piano.set.activityHint')), field(t('piano.set.deficit'), defSel)),
      field(t('piano.set.f.proteinG'), protIn, t('piano.set.protHint')),
      h('div', { class: 'form-grid two' }, field(t('piano.set.f.breakfastKcal'), bfK), field(t('piano.set.f.breakfastProt'), bfP)),
      field(t('piano.set.bfText'), bfText, t('piano.set.bfTextHint')),
      h('div', { class: 'field' }, h('span', null, t('piano.set.weighEvery')), everyWrap),
      preview,
      h('button', { type: 'submit', class: 'btn primary big' }, t('piano.save')),
      status));
    updPreview();

    // ---- start page
    out.appendChild(h('section', { class: 'card' },
      h('h2', { class: 'card-title' }, t('piano.set.start')),
      choices([{ value: 'piano', label: t('piano.tab.oggi') }, { value: 'heute', label: t('tab.heute') }], st.startPage, function (v) {
        saveSettings({ startPage: v });
        T.rerender();
      }, t('piano.set.start')),
      h('p', { class: 'muted tiny' }, t('piano.set.startPageHint'))));

    // ---- data: export / import / delete
    var dataStatus = h('div', { class: 'form-status', 'aria-live': 'polite' });
    var persistInfo = h('span', { class: 'muted tiny' });
    if (navigator.storage && navigator.storage.persisted) {
      navigator.storage.persisted().then(function (yes) { persistInfo.textContent = yes ? t('piano.data.persistent') : t('piano.data.notPersistent'); }, function () { /* ignore */ });
    }
    var file = h('input', { type: 'file', id: 'p-import', accept: 'application/json,.json', class: 'p-file' });
    file.addEventListener('change', function () {
      var f = file.files && file.files[0];
      if (!f) return;
      var rd = new FileReader();
      rd.onload = function () {
        var res = C.parseImport(String(rd.result || ''));
        file.value = '';
        if (!res.ok) { dataStatus.replaceChildren(notice('danger', t('piano.data.importErr') + ' (' + res.error + ')')); return; }
        if (!window.confirm(t('piano.data.importConfirm'))) return;
        ps.clear();
        Object.keys(res.data).forEach(function (k) { ps.setJSON(k, res.data[k]); });
        touch();
        T.toast(t('piano.data.imported'), 'ok');
        T.rerender();
      };
      rd.onerror = function () { dataStatus.replaceChildren(notice('danger', t('piano.data.importErr'))); };
      rd.readAsText(f);
    });
    out.appendChild(h('section', { class: 'card p-data' },
      h('h2', { class: 'card-title' }, t('piano.data.title')),
      h('p', { class: 'small' }, t('piano.data.local')),
      h('p', { class: 'muted small' }, st.lastExport ? t('piano.data.lastExport', { date: T.fmtDMY(st.lastExport) }) : t('piano.data.neverExported'), ' ', persistInfo),
      h('div', { class: 'btn-row' },
        h('button', { type: 'button', class: 'btn primary', onclick: function () { exportData(false, dataStatus); } }, t('piano.data.export')),
        h('button', { type: 'button', class: 'btn', onclick: function () { exportData(true, dataStatus); } }, t('piano.data.copy'))),
      h('label', { class: 'field' }, h('span', null, t('piano.data.import')), file, h('span', { class: 'muted tiny' }, t('piano.data.importHint'))),
      h('button', {
        type: 'button', class: 'btn danger-btn', onclick: function () {
          if (!window.confirm(t('piano.data.deleteConfirm'))) return;
          ps.clear();
          T.toast(t('piano.data.deleted'), 'ok');
          T.rerender();
        }
      }, t('piano.data.delete')),
      dataStatus));
    return out;
  }

  function exportJSON() {
    var data = {};
    ps.keys().forEach(function (k) { if (C.STORE_KEYS.indexOf(k) >= 0) data[k] = ps.getJSON(k, null); });
    return JSON.stringify(C.buildExport(data, new Date().toISOString()), null, 1);
  }
  function exportData(copyOnly, statusEl) {
    var json = exportJSON();
    var done = function () { saveSettings({ lastExport: todayISO() }); };
    if (copyOnly) {
      T.copyText(json).then(function (ok) {
        if (ok) { done(); T.toast(t('piano.data.copied'), 'ok'); } else statusEl.replaceChildren(notice('danger', t('piano.data.exportFail')));
      });
      return;
    }
    try {
      var url = URL.createObjectURL(new Blob([json], { type: 'application/json' }));
      var a = h('a', { href: url, download: 'piano-' + todayISO() + '.json', class: 'offscreen' });
      document.body.appendChild(a);
      a.click();
      setTimeout(function () { URL.revokeObjectURL(url); a.remove(); }, 2000);
      done();
      T.toast(t('piano.data.exported'), 'ok');
    } catch (e) {
      statusEl.replaceChildren(notice('danger', t('piano.data.exportFail')));
    }
  }

  // ------------------------------------------------------------------ registration
  var SUB = { '': viewOggi, oggi: viewOggi, corpo: viewCorpo, training: viewTraining, impostazioni: viewImpostazioni };
  var TITLES = { '': 'piano.tab.oggi', oggi: 'piano.tab.oggi', corpo: 'piano.tab.corpo', training: 'piano.tab.training', impostazioni: 'piano.set.title' };
  T.addRoute({
    id: 'piano',
    view: function () {
      var p = T.hashParts();
      var key = SUB[p[1] || ''] ? (p[1] || '') : '';
      return SUB[key](p.slice(2));
    },
    title: function () { var p = T.hashParts(); return t(TITLES[p[1] || ''] || 'piano.tab.oggi'); }
  });
  T.addMoreLink({ group: 'piano', href: '#/piano/impostazioni', icon: 'gear', label: 'piano.set.title' });
})();
