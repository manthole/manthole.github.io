/* Page Actus : ouverture des fiches détaillées dans un panneau.
   Sans JavaScript, les fiches s'ouvrent quand même grâce à :target (lien #f-…).
   Avec JavaScript : historique propre (le bouton Retour ferme la fiche), touche Échap,
   focus clavier, défilement de la page bloqué derrière le panneau. */
(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.add("news-js");
  var current = null;
  var opener = null;
  var ID = /^[fk]-[a-z0-9-]{1,40}$/;

  function show(id, push) {
    if (!ID.test(id)) return false;
    var fiche = document.getElementById(id);
    if (!fiche || !fiche.classList.contains("fiche")) return false;
    if (current && current !== fiche) current.classList.remove("is-open");
    fiche.classList.add("is-open");
    current = fiche;
    root.classList.add("fiche-lock");
    var panel = fiche.querySelector(".fiche__panel");
    panel.scrollTop = 0;
    panel.focus({ preventScroll: true });
    if (push) history.pushState({ fiche: id }, "", "#" + id);
    return true;
  }

  function hide() {
    if (!current) return;
    current.classList.remove("is-open");
    current = null;
    root.classList.remove("fiche-lock");
    if (opener) {
      opener.focus({ preventScroll: true });
      opener = null;
    }
  }

  function close() {
    if (history.state && history.state.fiche) {
      history.back(); // l'événement popstate ferme la fiche
    } else {
      history.replaceState(null, "", location.pathname + location.search);
      hide();
    }
  }

  document.addEventListener("click", function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    var closer = e.target.closest("[data-fiche-close]");
    if (closer) {
      e.preventDefault();
      close();
      return;
    }
    var a = e.target.closest("a.news-open");
    if (!a) return;
    var id = (a.getAttribute("href") || "").slice(1);
    if (show(id, true)) {
      e.preventDefault();
      opener = a;
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && current) close();
  });

  window.addEventListener("popstate", function () {
    var id = location.hash.slice(1);
    if (!show(id, false)) hide();
  });

  function init() {
    var id = location.hash.slice(1);
    if (ID.test(id)) show(id, false);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();

/* Bouton « copier » du résumé : copie le texte dans la langue affichée. */
document.addEventListener("click", function (e) {
  var btn = e.target.closest(".fiche__copy");
  if (!btn || !navigator.clipboard) return;
  var lang = ["fr", "en", "es", "pt", "de"].indexOf(document.documentElement.lang) >= 0 ? document.documentElement.lang : "en";
  var span = btn.closest(".fiche__term").querySelector('.fiche__pitch [lang="' + lang + '"]');
  if (!span) return;
  navigator.clipboard.writeText(span.textContent.trim()).then(function () {
    btn.classList.add("is-done");
    setTimeout(function () { btn.classList.remove("is-done"); }, 1600);
  });
});

/* Recherche dans les actus : filtre les sujets dans le navigateur (titres de tous les articles du sujet,
   sources, CVE, type d'attaque dans les 5 langues, groupes cités), sans accents ni majuscules.
   Plusieurs mots = tous doivent être présents. Un même sujet présent dans plusieurs sections n'est
   affiché qu'une fois. La requête est gardée dans l'adresse (?q=…) pour pouvoir la partager. */
(function () {
  "use strict";
  var input = document.getElementById("news-q");
  if (!input) return;
  var root = document.documentElement;
  var status = document.getElementById("news-q-status");
  var clearBtn = document.getElementById("news-q-clear");
  var LANGS = ["fr", "en", "es", "pt", "de"];
  function norm(s) { return String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  var rows = Array.prototype.slice.call(document.querySelectorAll(".news-section .news-row"));
  rows.forEach(function (r) {
    var t = r.querySelector(".news-title");
    var a = r.querySelector("a.news-open");
    r._q = norm(r.getAttribute("data-q") || r.textContent);
    r._t = t;
    r._orig = t ? t.textContent : "";
    r._key = a ? a.getAttribute("href") : r._orig;
  });
  var lists = Array.prototype.slice.call(document.querySelectorAll(".news-section .news-list"));
  var sections = Array.prototype.slice.call(document.querySelectorAll(".news-section"));

  /* surligne les termes dans le titre, sans tenir compte des accents */
  function mark(text, terms) {
    var n = "", map = [], i, k;
    for (i = 0; i < text.length; i++) {
      var c = norm(text[i]);
      for (k = 0; k < c.length; k++) { n += c[k]; map.push(i); }
    }
    var hit = [];
    terms.forEach(function (t) {
      var p = 0;
      while ((p = n.indexOf(t, p)) >= 0) { for (k = p; k < p + t.length; k++) hit[map[k]] = true; p += t.length; }
    });
    var out = "", open = false;
    for (i = 0; i < text.length; i++) {
      if (hit[i] && !open) { out += "<mark>"; open = true; }
      if (!hit[i] && open) { out += "</mark>"; open = false; }
      out += esc(text[i]);
    }
    return out + (open ? "</mark>" : "");
  }
  function msg(n, q) {
    var t = n === 0
      ? { fr: "Aucun sujet ne correspond à « {q} ». Essaie un nom d'entreprise, un groupe, une CVE ou un type d'attaque.",
          en: "No story matches “{q}”. Try a company name, a group, a CVE or an attack type.",
          es: "Ningún tema coincide con «{q}». Prueba con una empresa, un grupo, una CVE o un tipo de ataque.",
          pt: "Nenhum tema corresponde a «{q}». Experimenta uma empresa, um grupo, uma CVE ou um tipo de ataque.",
          de: "Keine Meldung passt zu „{q}“. Versuch es mit einer Firma, einer Gruppe, einer CVE oder einer Angriffsart." }
      : n === 1
        ? { fr: "1 sujet trouvé", en: "1 story found", es: "1 tema encontrado", pt: "1 tema encontrado", de: "1 Meldung gefunden" }
        : { fr: "{n} sujets trouvés", en: "{n} stories found", es: "{n} temas encontrados", pt: "{n} temas encontrados", de: "{n} Meldungen gefunden" };
    return LANGS.map(function (l) {
      return '<span lang="' + l + '">' + t[l].replace("{n}", n).replace("{q}", "<strong>" + esc(q) + "</strong>") + "</span>";
    }).join("");
  }

  var urlTimer = null;
  function apply(q) {
    var terms = norm(q).split(/\s+/).filter(Boolean);
    var active = terms.length > 0;
    root.classList.toggle("news-searching", active);
    clearBtn.hidden = !q;
    var seen = {}, found = 0;
    rows.forEach(function (r) {
      var ok = !active || terms.every(function (t) { return r._q.indexOf(t) >= 0; });
      if (ok && active) { if (seen[r._key]) ok = false; else { seen[r._key] = true; found++; } }
      r.hidden = !ok;
      if (r._t) {
        if (ok && active) r._t.innerHTML = mark(r._orig, terms);
        else if (r._t.firstElementChild) r._t.textContent = r._orig;
      }
    });
    lists.forEach(function (l) {
      var any = Array.prototype.some.call(l.children, function (c) { return !c.hidden; });
      l.hidden = active && !any;
      var prev = l.previousElementSibling;
      if (prev && prev.classList.contains("news-subtitle")) prev.hidden = active && !any;
    });
    sections.forEach(function (s) {
      var any = Array.prototype.some.call(s.querySelectorAll(".news-row"), function (r) { return !r.hidden; });
      s.hidden = active && !any;
    });
    status.innerHTML = active ? msg(found, q.trim()) : "";
    Array.prototype.forEach.call(document.querySelectorAll("[data-chip]"), function (c) {
      c.setAttribute("aria-pressed", active && norm(chipText(c)) === norm(q.trim()) ? "true" : "false");
    });
    clearTimeout(urlTimer);
    urlTimer = setTimeout(function () {
      var url = location.pathname + (q.trim() ? "?q=" + encodeURIComponent(q.trim()) : "") + location.hash;
      history.replaceState(history.state, "", url);
    }, 400);
  }
  function chipText(c) {
    var span = c.querySelector('[lang="' + root.lang + '"]');
    return (span || c).textContent.trim();
  }

  var timer = null;
  input.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(function () { apply(input.value); }, 120); });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && input.value) { e.stopPropagation(); input.value = ""; apply(""); }
    if (e.key === "Enter") { e.preventDefault(); input.blur(); }
  });
  clearBtn.addEventListener("click", function () { input.value = ""; apply(""); input.focus(); });
  document.addEventListener("click", function (e) {
    var c = e.target.closest("[data-chip]");
    if (!c) return;
    var t = chipText(c);
    input.value = norm(input.value.trim()) === norm(t) ? "" : t;
    apply(input.value);
  });
  /* « / » place le curseur dans la recherche (hors champ de saisie et fiche fermée) */
  document.addEventListener("keydown", function (e) {
    if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.target.closest("input, textarea, select, [contenteditable]") || root.classList.contains("fiche-lock")) return;
    e.preventDefault();
    input.focus();
    input.select();
  });
  var q0 = new URLSearchParams(location.search).get("q");
  if (q0) { input.value = q0.slice(0, 100); apply(input.value); }
})();
