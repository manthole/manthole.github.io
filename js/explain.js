/* Explications interactives : schéma de séquence pas à pas, simulateur d'injection SQL,
   calculateur de cassage Kerberos. Sans JavaScript, toutes les étapes restent visibles.
   Textes affichés en 5 langues : un <span lang> par langue, masqués par css/cyber.css. */
(function () {
  "use strict";

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  var LANGS = ["fr", "en", "es", "pt", "de"];
  /* t : { fr: "…", en: "…", … } ; vars : remplacées dans {nom} (valeurs échappées) */
  function T(t, vars) {
    return LANGS.map(function (l) {
      var s = t[l] || t.en;
      Object.keys(vars || {}).forEach(function (k) { s = s.split("{" + k + "}").join(vars[k]); });
      return '<span lang="' + l + '">' + s + "</span>";
    }).join("");
  }

  /* ------------------------------------------------------------ pas à pas */
  function stepper(root) {
    root.classList.add("ex-js");
    var panels = Array.prototype.slice.call(root.querySelectorAll(".ex-panel"));
    var msgs = Array.prototype.slice.call(root.querySelectorAll(".seq__msg"));
    var total = panels.length;
    var cur = 1, timer = null;
    var dots = root.querySelector(".ex-dots");
    var btnPrev = root.querySelector('[data-ex="prev"]');
    var btnNext = root.querySelector('[data-ex="next"]');
    var btnPlay = root.querySelector('[data-ex="play"]');
    for (var i = 1; i <= total; i++) {
      var d = document.createElement("button");
      d.type = "button";
      d.className = "ex-dot";
      d.setAttribute("data-go", String(i));
      d.setAttribute("aria-label", String(i) + " / " + total);
      dots.appendChild(d);
    }
    function show(n) {
      cur = Math.max(1, Math.min(total, n));
      msgs.forEach(function (m) {
        var s = +m.getAttribute("data-step");
        m.classList.toggle("is-past", s < cur);
        m.classList.toggle("is-current", s === cur);
        m.classList.toggle("is-future", s > cur);
      });
      panels.forEach(function (p) { p.classList.toggle("is-current", +p.getAttribute("data-step") === cur); });
      Array.prototype.forEach.call(dots.children, function (d, k) {
        d.classList.toggle("is-current", k + 1 === cur);
        d.setAttribute("aria-current", k + 1 === cur ? "step" : "false");
      });
      btnPrev.disabled = cur === 1;
      btnNext.disabled = cur === total;
    }
    function stop() {
      if (timer) { clearInterval(timer); timer = null; }
      root.classList.remove("is-playing");
      btnPlay.setAttribute("aria-pressed", "false");
    }
    function play() {
      if (timer) { stop(); return; }
      if (cur === total) show(1);
      root.classList.add("is-playing");
      btnPlay.setAttribute("aria-pressed", "true");
      timer = setInterval(function () {
        if (cur >= total) { stop(); return; }
        show(cur + 1);
      }, 3200);
    }
    root.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b || !root.contains(b)) return;
      if (b === btnPrev) { stop(); show(cur - 1); }
      else if (b === btnNext) { stop(); show(cur + 1); }
      else if (b === btnPlay) { play(); }
      else if (b.hasAttribute("data-go")) { stop(); show(+b.getAttribute("data-go")); }
    });
    root.addEventListener("keydown", function (e) {
      if (e.target.closest("input, textarea, select")) return;
      if (e.key === "ArrowRight") { stop(); show(cur + 1); e.preventDefault(); }
      if (e.key === "ArrowLeft") { stop(); show(cur - 1); e.preventDefault(); }
    });
    show(1);
  }

  /* ------------------------------------------------------------ simulateur SQL */
  var USERS = [
    { username: "admin", password: "Adm!n-2026" },
    { username: "alice", password: "s3cret!" },
    { username: "bob", password: "hunter2" }
  ];
  var KW = { SELECT: 1, FROM: 1, WHERE: 1, AND: 1, OR: 1, NOT: 1, UNION: 1, DROP: 1, INSERT: 1, UPDATE: 1, DELETE: 1 };
  var MSG = {
    unterminated: { fr: "chaîne de caractères non terminée", en: "unterminated string", es: "cadena sin terminar", pt: "cadeia de caracteres não terminada", de: "nicht abgeschlossene Zeichenkette" },
    near: { fr: "syntaxe invalide près de « {t} »", en: "syntax error near “{t}”", es: "error de sintaxis cerca de «{t}»", pt: "erro de sintaxe perto de «{t}»", de: "Syntaxfehler bei „{t}“" },
    column: { fr: "colonne inconnue « {t} »", en: "unknown column “{t}”", es: "columna desconocida «{t}»", pt: "coluna desconhecida «{t}»", de: "unbekannte Spalte „{t}“" },
    unsupported: { fr: "« {t} » n'est pas simulé dans cette démonstration", en: "“{t}” is not simulated in this demo", es: "«{t}» no se simula en esta demostración", pt: "«{t}» não é simulado nesta demonstração", de: "„{t}“ wird in dieser Demo nicht simuliert" },
    one: { fr: "Connecté en tant que <strong>{u}</strong>.", en: "Logged in as <strong>{u}</strong>.", es: "Sesión iniciada como <strong>{u}</strong>.", pt: "Sessão iniciada como <strong>{u}</strong>.", de: "Angemeldet als <strong>{u}</strong>." },
    many: { fr: "{n} lignes renvoyées : l'application connecte le premier compte, <strong>{u}</strong>, sans connaître son mot de passe.", en: "{n} rows returned: the application logs in the first account, <strong>{u}</strong>, without knowing its password.", es: "{n} filas devueltas: la aplicación inicia sesión con la primera cuenta, <strong>{u}</strong>, sin conocer su contraseña.", pt: "{n} linhas devolvidas: a aplicação inicia sessão com a primeira conta, <strong>{u}</strong>, sem conhecer a palavra-passe.", de: "{n} Zeilen zurückgegeben: Die Anwendung meldet das erste Konto an, <strong>{u}</strong>, ohne dessen Passwort zu kennen." },
    bypass: { fr: "Connecté en tant que <strong>{u}</strong> sans le bon mot de passe : la vérification a été court-circuitée.", en: "Logged in as <strong>{u}</strong> without the right password: the check was bypassed.", es: "Sesión iniciada como <strong>{u}</strong> sin la contraseña correcta: la comprobación se ha saltado.", pt: "Sessão iniciada como <strong>{u}</strong> sem a palavra-passe certa: a verificação foi contornada.", de: "Angemeldet als <strong>{u}</strong> ohne das richtige Passwort: Die Prüfung wurde umgangen." },
    none: { fr: "Aucune ligne renvoyée : connexion refusée.", en: "No row returned: login refused.", es: "Ninguna fila devuelta: acceso denegado.", pt: "Nenhuma linha devolvida: acesso recusado.", de: "Keine Zeile zurückgegeben: Anmeldung abgelehnt." },
    error: { fr: "Erreur SQL : {m}. Afficher ce message aide l'attaquant à ajuster sa saisie ; en production, on renvoie un message générique.", en: "SQL error: {m}. Showing this message helps the attacker tune the input; in production, return a generic message.", es: "Error SQL: {m}. Mostrar este mensaje ayuda al atacante a ajustar su entrada; en producción, se devuelve un mensaje genérico.", pt: "Erro SQL: {m}. Mostrar esta mensagem ajuda o atacante a ajustar a entrada; em produção, devolve-se uma mensagem genérica.", de: "SQL-Fehler: {m}. Diese Meldung hilft dem Angreifer, seine Eingabe anzupassen; in Produktion gibt man eine allgemeine Meldung zurück." },
    injected: { fr: "Ta saisie a changé la structure de la requête : {n} élément(s) en rouge sont interprétés comme du code SQL, plus comme des données.", en: "Your input changed the query's structure: {n} red element(s) are now interpreted as SQL code, no longer as data.", es: "Tu entrada ha cambiado la estructura de la consulta: {n} elemento(s) en rojo se interpretan como código SQL, ya no como datos.", pt: "A tua entrada mudou a estrutura da consulta: {n} elemento(s) a vermelho são interpretados como código SQL, já não como dados.", de: "Deine Eingabe hat die Struktur der Abfrage verändert: {n} rot markierte(s) Element(e) werden als SQL-Code interpretiert, nicht mehr als Daten." },
    safe: { fr: "La saisie reste une donnée : elle est envoyée à part et ne peut pas modifier la requête.", en: "The input stays data: it is sent separately and cannot change the query.", es: "La entrada sigue siendo un dato: se envía aparte y no puede modificar la consulta.", pt: "A entrada continua a ser um dado: é enviada à parte e não pode modificar a consulta.", de: "Die Eingabe bleibt ein Datum: Sie wird separat gesendet und kann die Abfrage nicht verändern." },
    params: { fr: "paramètres envoyés séparément", en: "parameters sent separately", es: "parámetros enviados por separado", pt: "parâmetros enviados à parte", de: "separat gesendete Parameter" }
  };

  function tokenize(sql, mask) {
    var toks = [], i = 0, n = sql.length;
    while (i < n) {
      var c = sql[i];
      if (/\s/.test(c)) { i++; continue; }
      var start = i, type;
      if (c === "-" && sql[i + 1] === "-") { i = n; type = "com"; }
      else if (c === "'") {
        i++;
        while (true) {
          if (i >= n) throw { key: "unterminated" };
          if (sql[i] === "'" && sql[i + 1] === "'") { i += 2; continue; }
          if (sql[i] === "'") { i++; break; }
          i++;
        }
        type = "str";
      } else if (/[0-9]/.test(c)) { while (i < n && /[0-9.]/.test(sql[i])) i++; type = "num"; }
      else if (/[A-Za-z_]/.test(c)) {
        while (i < n && /[A-Za-z0-9_]/.test(sql[i])) i++;
        type = KW[sql.slice(start, i).toUpperCase()] ? "kw" : "id";
      } else if (c === "<" && sql[i + 1] === ">" || c === "!" && sql[i + 1] === "=") { i += 2; type = "op"; }
      else if ("=(),*;?".indexOf(c) >= 0) { i++; type = "op"; }
      else throw { key: "near", t: c };
      var text = sql.slice(start, i), user = false, inj = false;
      for (var k = start; k < i; k++) if (mask[k]) user = true;
      if (type === "str") inj = mask[start] || mask[i - 1];
      else inj = user;
      toks.push({ type: type, text: text, start: start, end: i, user: user, inj: inj });
    }
    return toks;
  }

  function evaluate(toks) {
    var t = toks.filter(function (x) { return x.type !== "com"; }), p = 0;
    function peek() { return t[p]; }
    function up(x) { return x && x.text.toUpperCase(); }
    function expect(word) {
      var x = t[p];
      if (!x || up(x) !== word) throw { key: "near", t: x ? x.text : "∅" };
      p++;
    }
    ["SELECT", "*", "FROM", "USERS", "WHERE"].forEach(expect);
    function primary() {
      var x = t[p];
      if (!x) throw { key: "near", t: "∅" };
      if (x.type === "str") { p++; var v = x.text.slice(1, -1).replace(/''/g, "'"); return function () { return v; }; }
      if (x.type === "num") { p++; return function () { return x.text; }; }
      if (x.type === "id") {
        p++;
        var col = x.text.toLowerCase();
        if (col !== "username" && col !== "password") throw { key: "column", t: x.text };
        return function (row) { return row[col]; };
      }
      if (x.text === "(") { p++; var e = orExpr(); if (!t[p] || t[p].text !== ")") throw { key: "near", t: t[p] ? t[p].text : "∅" }; p++; return e; }
      if (x.type === "kw" && !{ AND: 1, OR: 1, NOT: 1 }[up(x)]) throw { key: "unsupported", t: x.text };
      throw { key: "near", t: x.text };
    }
    function cmp() {
      var a = primary(), x = peek();
      if (x && (x.text === "=" || x.text === "<>" || x.text === "!=")) {
        p++;
        var b = primary(), op = x.text;
        return function (row) { var eq = String(a(row)) === String(b(row)); return op === "=" ? eq : !eq; };
      }
      return function (row) { var v = a(row); return v !== "" && v !== "0" && v !== false; };
    }
    function notExpr() { if (up(peek()) === "NOT") { p++; var e = notExpr(); return function (r) { return !e(r); }; } return cmp(); }
    function andExpr() { var e = notExpr(); while (up(peek()) === "AND") { p++; var a = e, b = notExpr(); e = (function (a, b) { return function (r) { return a(r) && b(r); }; })(a, b); } return e; }
    function orExpr() { var e = andExpr(); while (up(peek()) === "OR") { p++; var a = e, b = andExpr(); e = (function (a, b) { return function (r) { return a(r) || b(r); }; })(a, b); } return e; }
    var where = orExpr();
    if (p < t.length) {
      var x = t[p];
      if (x.type === "kw" || x.text === ";") throw { key: "unsupported", t: x.text };
      throw { key: "near", t: x.text };
    }
    return USERS.filter(function (r) { return !!where(r); });
  }

  function sqlsim(root) {
    root.classList.add("ex-js");
    var form = root.querySelector(".sqlsim__form");
    var u = root.querySelector('[name="sim-user"]');
    var pw = root.querySelector('[name="sim-pass"]');
    var out = root.querySelector(".sqlsim__query");
    var params = root.querySelector(".sqlsim__params");
    var res = root.querySelector(".sqlsim__result");
    var note = root.querySelector(".sqlsim__note");
    var mode = "vuln";
    function render() {
      var parts = mode === "vuln"
        ? [["SELECT * FROM users WHERE username = '", 0], [u.value, 1], ["' AND password = '", 0], [pw.value, 1], ["'", 0]]
        : [["SELECT * FROM users WHERE username = ? AND password = ?", 0]];
      var sql = "", mask = [];
      parts.forEach(function (pt) { sql += pt[0]; for (var k = 0; k < pt[0].length; k++) mask.push(pt[1]); });
      var html = "", rows = null, err = null, toks = [];
      try {
        toks = tokenize(sql, mask);
        if (mode === "vuln") rows = evaluate(toks);
        else rows = USERS.filter(function (r) { return r.username === u.value && r.password === pw.value; });
      } catch (e) { err = e; }
      if (toks.length) {
        var pos = 0;
        toks.forEach(function (tk) {
          html += esc(sql.slice(pos, tk.start));
          var cls = "t-" + tk.type + (tk.inj ? " t-inj" : tk.user ? " t-user" : "");
          html += '<span class="' + cls + '">' + esc(tk.text) + "</span>";
          pos = tk.end;
        });
        html += esc(sql.slice(pos));
      } else {
        html = esc(sql);
      }
      out.innerHTML = html;
      params.hidden = mode !== "params";
      if (mode === "params") {
        params.innerHTML = T(MSG.params) + ' : <span class="t-user">' + esc(JSON.stringify([u.value, pw.value])) + "</span>";
      }
      var injected = toks.filter(function (x) { return x.inj; }).length;
      var cls, msg;
      if (err) {
        var m = MSG[err.key] || MSG.near;
        cls = "warn";
        msg = LANGS.map(function (l) {
          var inner = (m[l] || m.en).split("{t}").join(esc(err.t || ""));
          return '<span lang="' + l + '">' + (MSG.error[l] || MSG.error.en).split("{m}").join(inner) + "</span>";
        }).join("");
      } else if (!rows.length) {
        cls = "ok"; msg = T(MSG.none);
      } else if (rows.length > 1) {
        cls = "bad"; msg = T(MSG.many, { n: rows.length, u: esc(rows[0].username) });
      } else {
        var legit = rows[0].username === u.value && rows[0].password === pw.value;
        cls = legit ? "ok" : "bad";
        msg = T(legit ? MSG.one : MSG.bypass, { u: esc(rows[0].username) });
      }
      res.className = "sqlsim__result sqlsim__result--" + cls;
      res.innerHTML = msg;
      note.innerHTML = mode === "params" ? T(MSG.safe) : injected ? T(MSG.injected, { n: injected }) : "";
      note.hidden = !note.innerHTML;
    }
    root.addEventListener("click", function (e) {
      var b = e.target.closest("[data-mode], [data-example]");
      if (!b) return;
      if (b.hasAttribute("data-mode")) {
        mode = b.getAttribute("data-mode");
        root.querySelectorAll("[data-mode]").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        root.classList.toggle("is-safe", mode === "params");
      } else {
        u.value = b.getAttribute("data-example");
        pw.value = b.getAttribute("data-pass") || "";
      }
      render();
    });
    form.addEventListener("input", render);
    form.addEventListener("submit", function (e) { e.preventDefault(); });
    render();
  }

  /* ------------------------------------------------------------ calculateur Kerberos */
  var UNITS = {
    fr: [["seconde", "secondes"], ["minute", "minutes"], ["heure", "heures"], ["jour", "jours"], ["an", "ans"]],
    en: [["second", "seconds"], ["minute", "minutes"], ["hour", "hours"], ["day", "days"], ["year", "years"]],
    es: [["segundo", "segundos"], ["minuto", "minutos"], ["hora", "horas"], ["día", "días"], ["año", "años"]],
    pt: [["segundo", "segundos"], ["minuto", "minutos"], ["hora", "horas"], ["dia", "dias"], ["ano", "anos"]],
    de: [["Sekunde", "Sekunden"], ["Minute", "Minuten"], ["Stunde", "Stunden"], ["Tag", "Tage"], ["Jahr", "Jahre"]]
  };
  var LOCALES = { fr: "fr-FR", en: "en-US", es: "es-ES", pt: "pt-PT", de: "de-DE" };
  var INSTANT = { fr: "moins d'une seconde", en: "under a second", es: "menos de un segundo", pt: "menos de um segundo", de: "unter einer Sekunde" };
  var NEVER = { fr: "hors de portée (renouvelé tous les 30 jours)", en: "out of reach (rotated every 30 days)", es: "fuera de alcance (renovada cada 30 días)", pt: "fora de alcance (renovada a cada 30 dias)", de: "außer Reichweite (alle 30 Tage erneuert)" };
  var VERDICT = {
    bad: { fr: "Cassé : le compte de service tombe.", en: "Cracked: the service account falls.", es: "Roto: la cuenta de servicio cae.", pt: "Quebrado: a conta de serviço cai.", de: "Geknackt: Das Dienstkonto fällt." },
    warn: { fr: "Faisable avec du temps ou plusieurs cartes graphiques.", en: "Feasible with time or several GPUs.", es: "Factible con tiempo o varias tarjetas gráficas.", pt: "Viável com tempo ou várias placas gráficas.", de: "Machbar mit Zeit oder mehreren Grafikkarten." },
    ok: { fr: "Hors de portée en pratique.", en: "Out of reach in practice.", es: "Fuera de alcance en la práctica.", pt: "Fora de alcance na prática.", de: "Praktisch außer Reichweite." }
  };
  function duration(sec) {
    var steps = [[1, 0], [60, 1], [3600, 2], [86400, 3], [31557600, 4]];
    var u = 0;
    for (var i = 0; i < steps.length; i++) if (sec >= steps[i][0]) u = i;
    var v = sec / steps[u][0];
    return LANGS.map(function (l) {
      var txt;
      if (sec < 1) txt = INSTANT[l];
      else if (v >= 1e6) txt = "≈ 10<sup>" + Math.floor(Math.log10(v)) + "</sup> " + UNITS[l][u][1];
      else { var r = Math.round(v); txt = "≈ " + r.toLocaleString(LOCALES[l]) + " " + UNITS[l][u][r > 1 ? 1 : 0]; }
      return '<span lang="' + l + '">' + txt + "</span>";
    }).join("");
  }
  function kcalc(root) {
    root.classList.add("ex-js");
    var scenario = "dict", enc = "rc4";
    var RATE = { rc4: 1e9, aes: 1e6 };
    var time = root.querySelector(".kcalc__time");
    var bar = root.querySelector(".kcalc__bar span");
    var verdict = root.querySelector(".kcalc__verdict");
    function render() {
      /* dictionnaire + règles : ≈ 10^12 candidats ; rN : N caractères aléatoires parmi 95 */
      var space = scenario === "dict" ? 1e12 : Math.pow(95, +scenario.slice(1));
      var sec = scenario === "gmsa" ? Infinity : space / 2 / RATE[enc];
      time.innerHTML = sec === Infinity ? T(NEVER) : duration(sec);
      var year = 31557600;
      var level = sec < 86400 ? "bad" : sec < 100 * year ? "warn" : "ok";
      var frac = sec === Infinity ? 1 : Math.max(0.03, Math.min(1, (Math.log10(Math.max(sec, 1)) + 1) / 22));
      bar.style.width = (frac * 100).toFixed(1) + "%";
      root.setAttribute("data-level", level);
      verdict.innerHTML = T(VERDICT[level]);
    }
    root.addEventListener("click", function (e) {
      var b = e.target.closest("[data-scenario], [data-enc]");
      if (!b) return;
      var attr = b.hasAttribute("data-scenario") ? "data-scenario" : "data-enc";
      root.querySelectorAll("[" + attr + "]").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      if (attr === "data-scenario") scenario = b.getAttribute(attr); else enc = b.getAttribute(attr);
      render();
    });
    render();
  }

  function init() {
    document.querySelectorAll("[data-stepper]").forEach(stepper);
    document.querySelectorAll("[data-sqlsim]").forEach(sqlsim);
    document.querySelectorAll("[data-kcalc]").forEach(kcalc);
  }
  if (typeof document === "undefined") { /* Node : tests */ }
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();

  /* tests (Node) : module.exports si disponible */
  if (typeof module !== "undefined") module.exports = { tokenize: tokenize, evaluate: evaluate, USERS: USERS };
})();
