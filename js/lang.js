/* Sélecteur de langue FR / EN.
   Chargé dans le <head> pour fixer <html lang> avant l'affichage de la page (pas de clignotement) ;
   css/cyber.css masque ensuite les éléments [lang="fr"] ou [lang="en"] de l'autre langue.
   Langue par défaut : le dernier choix du visiteur, sinon celle de son navigateur. */
(function () {
  var root = document.documentElement;
  var title = document.querySelector("title");
  var titleEn = document.title;

  function apply(lang) {
    root.lang = lang;
    if (title && title.dataset.fr) {
      document.title = lang === "fr" ? title.dataset.fr : titleEn;
    }
  }

  var lang = null;
  try { lang = localStorage.getItem("lang"); } catch (e) {}
  if (lang !== "fr" && lang !== "en") {
    lang = /^fr\b/i.test(navigator.language || "") ? "fr" : "en";
  }
  apply(lang);

  document.addEventListener("click", function (e) {
    if (!e.target.closest(".lang-switch")) return;
    var next = root.lang === "fr" ? "en" : "fr";
    apply(next);
    try { localStorage.setItem("lang", next); } catch (err) {}
  });
})();
