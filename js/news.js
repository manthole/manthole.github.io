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
