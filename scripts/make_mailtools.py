"""Génère les pages des outils e-mail : /tools/email-headers/ et /tools/dns-check/ (5 langues).
Gabarit : tools/deobfuscator/index.html. Logique dans js/mail.js, styles dans css/tools.css.
Usage : python3 scripts/make_mailtools.py <racine du site>"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from make_explain import L, set_head  # noqa: E402

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
SITE = "https://manthole.github.io"


def chips(a, b):
    return (f'<p class="x-kicker k-orange"><span class="x-chip "><span class="x-dot" aria-hidden="true"></span>{L(*a)}</span> '
            f'<span class="x-chip x-chip--muted x-chip--plain">{L(*b)}</span></p>')


def label(*t):
    return f'<span class="tool-label">{L(*t)}</span>'


def ph(attr_id, fr, en, es, pt, de):
    return f'data-ph-fr="{fr}" data-ph-en="{en}" data-ph-es="{es}" data-ph-pt="{pt}" data-ph-de="{de}"'


def steps(items):
    lis = "".join(f'<li data-reveal><span class="x-step__node" aria-hidden="true">{i}</span><div class="x-step__body"><h4>{L(*h)}</h4><p>{L(*p)}</p></div></li>'
                  for i, (h, p) in enumerate(items, 1))
    return (f'<section class="tool-flow k-orange"><h3 class="x-h">{L("Sous le capot", "Under the hood", "Bajo el capó", "Por dentro", "Unter der Haube")}</h3>'
            f'<ol class="x-steps " data-reveal>{lis}</ol></section>')


BACK = (f'<p class="tool-back k-orange"><a class="x-btn" href="{SITE}/tools/">← '
        + L("Tous les outils", "All tools", "Todas las herramientas", "Todas as ferramentas", "Alle Tools") + "</a></p>")
RUN_SAMPLE = L("Charger un exemple", "Load an example", "Cargar un ejemplo", "Carregar um exemplo", "Beispiel laden")

# ---------------------------------------------------------------- en-têtes

HEADERS_TITLE = ("Analyseur d'en-têtes d'e-mail", "Email header analyzer", "Analizador de encabezados de correo", "Analisador de cabeçalhos de e-mail", "E-Mail-Header-Analyse")

HEADERS_TOOL = f"""{chips(("Analyse SOC", "SOC analysis", "Análisis SOC", "Análise SOC", "SOC-Analyse"), ("100 % navigateur", "100% in-browser", "100 % navegador", "100 % navegador", "100 % im Browser"))}
<p class="tool-privacy">{L("Les en-têtes sont analysées <strong>dans ton navigateur</strong> : rien n'est envoyé. Elles contiennent des adresses e-mail et IP, évite de les coller sur des sites tiers.",
 "Headers are analysed <strong>in your browser</strong>: nothing is sent. They contain email and IP addresses, so avoid pasting them into third-party sites.",
 "Los encabezados se analizan <strong>en tu navegador</strong>: no se envía nada. Contienen direcciones de correo e IP, evita pegarlos en sitios de terceros.",
 "Os cabeçalhos são analisados <strong>no teu navegador</strong>: nada é enviado. Contêm endereços de e-mail e IP, evita colá-los em sites de terceiros.",
 "Die Header werden <strong>in deinem Browser</strong> analysiert: Nichts wird gesendet. Sie enthalten E-Mail- und IP-Adressen, füge sie daher nicht auf fremden Websites ein.")}</p>
<div class="tool">
  <label for="eh-input">{L("en-têtes brutes du message", "raw message headers", "encabezados en bruto del mensaje", "cabeçalhos brutos da mensagem", "rohe Header der Nachricht")}</label>
  <div class="tool-field">
    <textarea id="eh-input" class="textarea-tall" spellcheck="false" autocomplete="off" {ph("eh", "Colle ici les en-têtes (ou la source complète) du message suspect", "Paste the headers (or full source) of the suspicious message here", "Pega aquí los encabezados (o el código fuente completo) del mensaje sospechoso", "Cola aqui os cabeçalhos (ou o código-fonte completo) da mensagem suspeita", "Füge hier die Header (oder den vollständigen Quelltext) der verdächtigen Nachricht ein")}></textarea>
  </div>
  <div class="tool-row">
    <button class="btn" type="button" id="eh-run">{L("Analyser", "Analyse", "Analizar", "Analisar", "Analysieren")}</button>
    <button class="btn btn--ghost" type="button" id="eh-sample">{RUN_SAMPLE}</button>
  </div>
  <div class="tool-msg" id="eh-status" aria-live="polite"></div>
  <div id="eh-results" hidden>
    {label("verdict", "verdict", "veredicto", "veredicto", "Ergebnis")}
    <ul class="mail-findings" id="eh-findings"></ul>
    {label("authentification (serveur de réception)", "authentication (receiving server)", "autenticación (servidor de recepción)", "autenticação (servidor de receção)", "Authentifizierung (empfangender Server)")}
    <div class="mail-auth" id="eh-auth"></div>
    {label("expéditeur et message", "sender and message", "remitente y mensaje", "remetente e mensagem", "Absender und Nachricht")}
    <dl class="mail-kv" id="eh-ident"></dl>
    <div id="eh-hops-wrap">
      {label("chemin des serveurs, du premier au dernier", "server path, first to last", "ruta de servidores, del primero al último", "caminho dos servidores, do primeiro ao último", "Serverpfad, vom ersten zum letzten")}
      <ol class="mail-hops" id="eh-hops"></ol>
    </div>
  </div>
</div>
{steps([
    (("Lecture", "Parsing", "Lectura", "Leitura", "Einlesen"),
     ("Les en-têtes repliées sont reconstituées et les objets encodés (<code>=?UTF-8?B?…?=</code>) décodés.", "Folded headers are rebuilt and encoded subjects (<code>=?UTF-8?B?…?=</code>) decoded.", "Los encabezados plegados se reconstruyen y los asuntos codificados (<code>=?UTF-8?B?…?=</code>) se decodifican.", "Os cabeçalhos dobrados são reconstruídos e os assuntos codificados (<code>=?UTF-8?B?…?=</code>) descodificados.", "Gefaltete Header werden zusammengesetzt und kodierte Betreffzeilen (<code>=?UTF-8?B?…?=</code>) dekodiert.")),
    (("Chemin", "Path", "Ruta", "Caminho", "Pfad"),
     ("Les lignes <code>Received</code> se lisent de bas en haut : chaque serveur ajoute la sienne au-dessus. On en tire les étapes, les délais et l'IP d'origine.", "<code>Received</code> lines read bottom to top: each server adds its own on top. They give the hops, delays and origin IP.", "Las líneas <code>Received</code> se leen de abajo arriba: cada servidor añade la suya encima. De ellas salen los saltos, los retrasos y la IP de origen.", "As linhas <code>Received</code> leem-se de baixo para cima: cada servidor acrescenta a sua por cima. Daí saem os saltos, os atrasos e o IP de origem.", "<code>Received</code>-Zeilen liest man von unten nach oben: Jeder Server fügt seine oben an. Daraus ergeben sich Hops, Verzögerungen und Ursprungs-IP.")),
    (("Authentification", "Authentication", "Autenticación", "Autenticação", "Authentifizierung"),
     ("Les résultats SPF, DKIM et DMARC sont lus dans l'en-tête <code>Authentication-Results</code> écrite par ton serveur de réception, la seule fiable.", "SPF, DKIM and DMARC results are read from the <code>Authentication-Results</code> header written by your receiving server, the only trustworthy one.", "Los resultados SPF, DKIM y DMARC se leen en el encabezado <code>Authentication-Results</code> escrito por tu servidor de recepción, el único fiable.", "Os resultados SPF, DKIM e DMARC são lidos no cabeçalho <code>Authentication-Results</code> escrito pelo teu servidor de receção, o único fiável.", "SPF-, DKIM- und DMARC-Ergebnisse stammen aus dem <code>Authentication-Results</code>-Header deines empfangenden Servers, dem einzig vertrauenswürdigen.")),
    (("Incohérences", "Inconsistencies", "Incoherencias", "Incoerências", "Ungereimtheiten"),
     ("Réponse détournée (<code>Reply-To</code>), adresse cachée dans le nom affiché, adresse de retour différente, domaine en punycode.", "Hijacked replies (<code>Reply-To</code>), address hidden in the display name, different return path, punycode domain.", "Respuesta desviada (<code>Reply-To</code>), dirección escondida en el nombre visible, dirección de retorno distinta, dominio en punycode.", "Resposta desviada (<code>Reply-To</code>), endereço escondido no nome apresentado, endereço de retorno diferente, domínio em punycode.", "Umgeleitete Antworten (<code>Reply-To</code>), im Anzeigenamen versteckte Adresse, abweichende Rücklaufadresse, Punycode-Domain.")),
])}
<div lang="fr">
<h3>Où trouver les en-têtes ?</h3>
<ul>
<li><strong>Gmail</strong> : menu ⋮ du message, puis « Afficher l'original ».</li>
<li><strong>Outlook (web)</strong> : menu … du message, « Afficher », puis « Afficher les détails du message ».</li>
<li><strong>Outlook (Windows)</strong> : ouvrir le message, « Fichier », « Propriétés », zone « En-têtes Internet ».</li>
<li><strong>Thunderbird</strong> : <code>Ctrl+U</code> (source du message). <strong>Apple Mail</strong> : « Présentation », « Message », « Source brute ».</li>
</ul>
<h3>Lire le résultat</h3>
<p><strong>SPF</strong> vérifie que le serveur qui a envoyé le message est autorisé par le domaine de l'adresse de retour. <strong>DKIM</strong> vérifie une signature posée par le domaine expéditeur : le message n'a pas été modifié. <strong>DMARC</strong> relie les deux au domaine affiché dans « De », celui que voit la victime : c'est le contrôle qui compte contre l'usurpation.</p>
<h3>Limites</h3>
<p>Un message transféré ou passé par une liste de diffusion peut échouer en SPF ou DKIM sans être malveillant. Un DMARC réussi prouve seulement que le domaine est bien celui affiché, pas qu'il est honnête : un attaquant peut très bien authentifier son propre domaine sosie. Les liens et pièces jointes doivent être analysés à part.</p>
</div>
<div lang="en">
<h3>Where do I find the headers?</h3>
<ul>
<li><strong>Gmail</strong>: the message's ⋮ menu, then “Show original”.</li>
<li><strong>Outlook (web)</strong>: the message's … menu, “View”, then “View message details”.</li>
<li><strong>Outlook (Windows)</strong>: open the message, “File”, “Properties”, “Internet headers” box.</li>
<li><strong>Thunderbird</strong>: <code>Ctrl+U</code> (message source). <strong>Apple Mail</strong>: “View”, “Message”, “Raw Source”.</li>
</ul>
<h3>Reading the result</h3>
<p><strong>SPF</strong> checks that the server that sent the message is authorised by the return-path domain. <strong>DKIM</strong> checks a signature applied by the sending domain: the message was not altered. <strong>DMARC</strong> ties both to the domain shown in “From”, the one the victim sees: it is the check that matters against spoofing.</p>
<h3>Limits</h3>
<p>A forwarded message or one sent through a mailing list can fail SPF or DKIM without being malicious. A DMARC pass only proves the domain is the one displayed, not that it is honest: an attacker can authenticate their own look-alike domain. Links and attachments must be analysed separately.</p>
</div>
<div lang="es">
<h3>¿Dónde encuentro los encabezados?</h3>
<ul>
<li><strong>Gmail</strong>: menú ⋮ del mensaje y luego «Mostrar original».</li>
<li><strong>Outlook (web)</strong>: menú … del mensaje, «Ver» y luego «Ver detalles del mensaje».</li>
<li><strong>Outlook (Windows)</strong>: abre el mensaje, «Archivo», «Propiedades», cuadro «Encabezados de Internet».</li>
<li><strong>Thunderbird</strong>: <code>Ctrl+U</code> (código fuente del mensaje). <strong>Apple Mail</strong>: «Visualización», «Mensaje», «Fuente sin procesar».</li>
</ul>
<h3>Leer el resultado</h3>
<p><strong>SPF</strong> comprueba que el servidor que envió el mensaje está autorizado por el dominio de la dirección de retorno. <strong>DKIM</strong> comprueba una firma puesta por el dominio remitente: el mensaje no se ha modificado. <strong>DMARC</strong> vincula ambos al dominio mostrado en «De», el que ve la víctima: es el control que cuenta contra la suplantación.</p>
<h3>Límites</h3>
<p>Un mensaje reenviado o que pasa por una lista de distribución puede fallar en SPF o DKIM sin ser malicioso. Un DMARC correcto solo demuestra que el dominio es el que se muestra, no que sea honesto: un atacante puede autenticar perfectamente su propio dominio parecido. Los enlaces y adjuntos deben analizarse aparte.</p>
</div>
<div lang="pt">
<h3>Onde encontro os cabeçalhos?</h3>
<ul>
<li><strong>Gmail</strong>: menu ⋮ da mensagem e depois «Mostrar original».</li>
<li><strong>Outlook (web)</strong>: menu … da mensagem, «Ver» e depois «Ver detalhes da mensagem».</li>
<li><strong>Outlook (Windows)</strong>: abre a mensagem, «Ficheiro», «Propriedades», caixa «Cabeçalhos da Internet».</li>
<li><strong>Thunderbird</strong>: <code>Ctrl+U</code> (código-fonte da mensagem). <strong>Apple Mail</strong>: «Visualização», «Mensagem», «Fonte em bruto».</li>
</ul>
<h3>Ler o resultado</h3>
<p>O <strong>SPF</strong> verifica que o servidor que enviou a mensagem está autorizado pelo domínio do endereço de retorno. O <strong>DKIM</strong> verifica uma assinatura colocada pelo domínio remetente: a mensagem não foi alterada. O <strong>DMARC</strong> liga ambos ao domínio mostrado em «De», o que a vítima vê: é o controlo que conta contra a usurpação.</p>
<h3>Limites</h3>
<p>Uma mensagem reencaminhada ou que passa por uma lista de distribuição pode falhar no SPF ou DKIM sem ser maliciosa. Um DMARC aprovado só prova que o domínio é o que aparece, não que seja honesto: um atacante pode perfeitamente autenticar o seu próprio domínio parecido. As ligações e anexos devem ser analisados à parte.</p>
</div>
<div lang="de">
<h3>Wo finde ich die Header?</h3>
<ul>
<li><strong>Gmail</strong>: ⋮-Menü der Nachricht, dann „Original anzeigen“.</li>
<li><strong>Outlook (Web)</strong>: …-Menü der Nachricht, „Anzeigen“, dann „Nachrichtendetails anzeigen“.</li>
<li><strong>Outlook (Windows)</strong>: Nachricht öffnen, „Datei“, „Eigenschaften“, Feld „Internetkopfzeilen“.</li>
<li><strong>Thunderbird</strong>: <code>Strg+U</code> (Quelltext der Nachricht). <strong>Apple Mail</strong>: „Darstellung“, „E-Mail“, „Rohdaten“.</li>
</ul>
<h3>Das Ergebnis lesen</h3>
<p><strong>SPF</strong> prüft, ob der sendende Server von der Domain der Rücklaufadresse autorisiert ist. <strong>DKIM</strong> prüft eine Signatur der sendenden Domain: Die Nachricht wurde nicht verändert. <strong>DMARC</strong> verknüpft beides mit der in „Von“ angezeigten Domain, die das Opfer sieht: Das ist die entscheidende Prüfung gegen Spoofing.</p>
<h3>Grenzen</h3>
<p>Eine weitergeleitete Nachricht oder eine über eine Mailingliste kann bei SPF oder DKIM scheitern, ohne bösartig zu sein. Ein bestandenes DMARC beweist nur, dass die Domain die angezeigte ist, nicht dass sie ehrlich ist: Ein Angreifer kann seine eigene Doppelgänger-Domain problemlos authentifizieren. Links und Anhänge müssen separat analysiert werden.</p>
</div>
{BACK}"""

# ---------------------------------------------------------------- DNS

DNS_TITLE = ("Vérificateur DNS e-mail", "Email DNS checker", "Verificador DNS de correo", "Verificador DNS de e-mail", "E-Mail-DNS-Prüfung")

DNS_TOOL = f"""{chips(("Sécurité e-mail", "Email security", "Seguridad del correo", "Segurança do e-mail", "E-Mail-Sicherheit"), ("DNS public via 1.1.1.1", "public DNS via 1.1.1.1", "DNS público vía 1.1.1.1", "DNS público via 1.1.1.1", "öffentliches DNS über 1.1.1.1"))}
<p class="tool-privacy">{L("Seul le <strong>nom de domaine</strong> saisi est envoyé, en HTTPS, au résolveur DNS public de Cloudflare (1.1.1.1) : ce sont des informations publiques. Ce site ne conserve rien.",
 "Only the <strong>domain name</strong> you enter is sent, over HTTPS, to Cloudflare's public DNS resolver (1.1.1.1): this is public information. This site keeps nothing.",
 "Solo se envía el <strong>nombre de dominio</strong> introducido, por HTTPS, al resolutor DNS público de Cloudflare (1.1.1.1): es información pública. Este sitio no guarda nada.",
 "Só é enviado o <strong>nome de domínio</strong> introduzido, por HTTPS, ao resolvedor DNS público da Cloudflare (1.1.1.1): é informação pública. Este site não guarda nada.",
 "Nur der eingegebene <strong>Domainname</strong> wird per HTTPS an den öffentlichen DNS-Resolver von Cloudflare (1.1.1.1) gesendet: Das sind öffentliche Informationen. Diese Website speichert nichts.")}</p>
<form class="tool" id="dn-form" autocomplete="off" novalidate>
  <div class="mail-form">
    <label for="dn-domain">{L("domaine", "domain", "dominio", "domínio", "Domain")}<input type="text" id="dn-domain" spellcheck="false" autocapitalize="off" inputmode="url" {ph("dn", "exemple.fr", "example.com", "ejemplo.es", "exemplo.pt", "beispiel.de")}></label>
    <label for="dn-selector">{L("sélecteur DKIM (facultatif)", "DKIM selector (optional)", "selector DKIM (opcional)", "seletor DKIM (opcional)", "DKIM-Selektor (optional)")}<input type="text" id="dn-selector" spellcheck="false" autocapitalize="off" {ph("dn", "ex. selector1", "e.g. selector1", "p. ej. selector1", "ex. selector1", "z. B. selector1")}></label>
  </div>
  <div class="tool-row">
    <button class="btn" type="submit" id="dn-run">{L("Vérifier", "Check", "Verificar", "Verificar", "Prüfen")}</button>
    <span class="tool-hint">{L("Exemples :", "Examples:", "Ejemplos:", "Exemplos:", "Beispiele:")}</span>
    <button class="btn btn--ghost" type="button" data-dn-example="example.com">example.com</button>
    <button class="btn btn--ghost" type="button" data-dn-example="gmail.com">gmail.com</button>
    <button class="btn btn--ghost" type="button" data-dn-example="wikipedia.org">wikipedia.org</button>
  </div>
  <div class="tool-msg" id="dn-status" aria-live="polite"></div>
  <div id="dn-results" hidden>
    {label("bilan", "summary", "balance", "balanço", "Übersicht")}
    <ul class="mail-findings" id="dn-findings"></ul>
    {label("enregistrements", "records", "registros", "registos", "Einträge")}
    <div class="mail-cards" id="dn-cards"></div>
  </div>
</form>
{steps([
    (("Requêtes", "Queries", "Consultas", "Consultas", "Abfragen"),
     ("Le navigateur interroge le DNS en HTTPS (DNS-over-HTTPS) : MX, TXT du domaine, <code>_dmarc</code>, <code>_mta-sts</code>, <code>_smtp._tls</code> et les sélecteurs DKIM.", "The browser queries DNS over HTTPS: MX, the domain's TXT, <code>_dmarc</code>, <code>_mta-sts</code>, <code>_smtp._tls</code> and DKIM selectors.", "El navegador consulta el DNS por HTTPS (DNS-over-HTTPS): MX, TXT del dominio, <code>_dmarc</code>, <code>_mta-sts</code>, <code>_smtp._tls</code> y los selectores DKIM.", "O navegador consulta o DNS por HTTPS (DNS-over-HTTPS): MX, TXT do domínio, <code>_dmarc</code>, <code>_mta-sts</code>, <code>_smtp._tls</code> e os seletores DKIM.", "Der Browser fragt das DNS per HTTPS ab (DNS-over-HTTPS): MX, TXT der Domain, <code>_dmarc</code>, <code>_mta-sts</code>, <code>_smtp._tls</code> und DKIM-Selektoren.")),
    (("SPF", "SPF", "SPF", "SPF", "SPF"),
     ("Un seul enregistrement, un <code>all</code> final strict, et moins de 10 recherches DNS en suivant chaque <code>include</code>.", "A single record, a strict final <code>all</code>, and fewer than 10 DNS lookups when following every <code>include</code>.", "Un único registro, un <code>all</code> final estricto y menos de 10 consultas DNS siguiendo cada <code>include</code>.", "Um único registo, um <code>all</code> final estrito e menos de 10 consultas DNS seguindo cada <code>include</code>.", "Ein einziger Eintrag, ein striktes abschließendes <code>all</code> und weniger als 10 DNS-Abfragen beim Verfolgen jedes <code>include</code>.")),
    (("DMARC", "DMARC", "DMARC", "DMARC", "DMARC"),
     ("Politique (<code>none</code>, <code>quarantine</code>, <code>reject</code>), pourcentage appliqué, rapports, sous-domaines, héritage du domaine parent.", "Policy (<code>none</code>, <code>quarantine</code>, <code>reject</code>), applied percentage, reports, subdomains, inheritance from the parent domain.", "Política (<code>none</code>, <code>quarantine</code>, <code>reject</code>), porcentaje aplicado, informes, subdominios, herencia del dominio padre.", "Política (<code>none</code>, <code>quarantine</code>, <code>reject</code>), percentagem aplicada, relatórios, subdomínios, herança do domínio pai.", "Richtlinie (<code>none</code>, <code>quarantine</code>, <code>reject</code>), angewandter Prozentsatz, Berichte, Subdomains, Vererbung von der übergeordneten Domain.")),
    (("DKIM et transport", "DKIM and transport", "DKIM y transporte", "DKIM e transporte", "DKIM und Transport"),
     ("Taille estimée de la clé DKIM, MTA-STS et TLS-RPT pour le chiffrement entre serveurs, et DNSSEC.", "Estimated DKIM key size, MTA-STS and TLS-RPT for server-to-server encryption, and DNSSEC.", "Tamaño estimado de la clave DKIM, MTA-STS y TLS-RPT para el cifrado entre servidores, y DNSSEC.", "Tamanho estimado da chave DKIM, MTA-STS e TLS-RPT para a cifra entre servidores, e DNSSEC.", "Geschätzte DKIM-Schlüssellänge, MTA-STS und TLS-RPT für die Verschlüsselung zwischen Servern sowie DNSSEC.")),
])}
<div lang="fr">
<h3>À quoi ça sert ?</h3>
<p>Ces enregistrements DNS décident si n'importe qui peut envoyer un e-mail en se faisant passer pour ton domaine. Un domaine sans DMARC en <code>reject</code> ou <code>quarantine</code> est une cible facile pour le phishing et la fraude au président. C'est aussi utile pour vérifier le domaine d'un fournisseur avant de faire confiance à ses e-mails.</p>
<h3>Limites</h3>
<p>Les sélecteurs DKIM ne peuvent pas être listés : sans le bon nom (visible dans l'en-tête <code>DKIM-Signature</code> d'un message reçu), seuls les plus courants sont essayés. Le domaine parent est déterminé de façon approximative pour les suffixes rares. Les résultats reflètent le DNS au moment de la requête.</p>
</div>
<div lang="en">
<h3>What is it for?</h3>
<p>These DNS records decide whether anyone can send email pretending to be your domain. A domain without DMARC set to <code>reject</code> or <code>quarantine</code> is an easy target for phishing and CEO fraud. It is also handy to check a supplier's domain before trusting its emails.</p>
<h3>Limits</h3>
<p>DKIM selectors cannot be listed: without the right name (visible in the <code>DKIM-Signature</code> header of a received message), only the most common ones are tried. The parent domain is approximated for rare suffixes. Results reflect DNS at query time.</p>
</div>
<div lang="es">
<h3>¿Para qué sirve?</h3>
<p>Estos registros DNS deciden si cualquiera puede enviar un correo haciéndose pasar por tu dominio. Un dominio sin DMARC en <code>reject</code> o <code>quarantine</code> es un blanco fácil para el phishing y el fraude del CEO. También sirve para comprobar el dominio de un proveedor antes de fiarse de sus correos.</p>
<h3>Límites</h3>
<p>Los selectores DKIM no se pueden listar: sin el nombre correcto (visible en el encabezado <code>DKIM-Signature</code> de un mensaje recibido), solo se prueban los más habituales. El dominio padre se determina de forma aproximada para los sufijos poco comunes. Los resultados reflejan el DNS en el momento de la consulta.</p>
</div>
<div lang="pt">
<h3>Para que serve?</h3>
<p>Estes registos DNS decidem se qualquer pessoa pode enviar um e-mail fazendo-se passar pelo teu domínio. Um domínio sem DMARC em <code>reject</code> ou <code>quarantine</code> é um alvo fácil para o phishing e a fraude do CEO. Também serve para verificar o domínio de um fornecedor antes de confiar nos seus e-mails.</p>
<h3>Limites</h3>
<p>Os seletores DKIM não podem ser listados: sem o nome certo (visível no cabeçalho <code>DKIM-Signature</code> de uma mensagem recebida), só se experimentam os mais comuns. O domínio pai é determinado de forma aproximada para sufixos raros. Os resultados refletem o DNS no momento da consulta.</p>
</div>
<div lang="de">
<h3>Wofür ist das gut?</h3>
<p>Diese DNS-Einträge entscheiden, ob jeder beliebige E-Mails im Namen deiner Domain senden kann. Eine Domain ohne DMARC auf <code>reject</code> oder <code>quarantine</code> ist ein leichtes Ziel für Phishing und CEO-Fraud. Praktisch auch, um die Domain eines Lieferanten zu prüfen, bevor man seinen E-Mails vertraut.</p>
<h3>Grenzen</h3>
<p>DKIM-Selektoren lassen sich nicht auflisten: Ohne den richtigen Namen (sichtbar im Header <code>DKIM-Signature</code> einer empfangenen Nachricht) werden nur die gängigsten probiert. Die übergeordnete Domain wird bei seltenen Endungen näherungsweise bestimmt. Die Ergebnisse geben den DNS-Stand zum Zeitpunkt der Abfrage wieder.</p>
</div>
{BACK}"""


def build(tpl, slug, tool, title5, desc, body, csp_extra=""):
    url = f"{SITE}/tools/{slug}/"
    s = set_head(tpl, title5, desc, url, title5[1])
    main_html = (f'<main class="post" data-tool="{tool}">\n        <article>\n'
                 f'            <h2 class="post-title"><a href="{url}">{L(*title5)}</a></h2>\n'
                 f'            <div class="post-content">\n{body}\n            </div>\n'
                 f'        </article>\n    </main>')
    s = re.sub(r'<main class="post" data-tool="[^"]*">.*?</main>', lambda m: main_html, s, count=1, flags=re.S)
    if "/js/mail.js" not in s:
        s = s.replace('<script src="/js/tools.js" defer></script>', '<script src="/js/tools.js" defer></script>\n<script src="/js/mail.js" defer></script>', 1)
    if csp_extra:
        s = s.replace("connect-src 'self' https://api.pwnedpasswords.com;", f"connect-src 'self' {csp_extra};", 1)
    else:
        s = s.replace("connect-src 'self' https://api.pwnedpasswords.com;", "connect-src 'self';", 1)
    d = ROOT / "tools" / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(s, encoding="utf-8")
    print(f"tools/{slug}/index.html écrit")


def main():
    tpl = (ROOT / "tools" / "deobfuscator" / "index.html").read_text(encoding="utf-8")
    build(tpl, "email-headers", "headers", HEADERS_TITLE,
          "Free email header analyzer: SPF, DKIM and DMARC results, server path with delays and origin IP, Reply-To and display-name spoofing. Runs in your browser.",
          HEADERS_TOOL)
    build(tpl, "dns-check", "dns", DNS_TITLE,
          "Free email DNS checker: SPF (with lookup count), DMARC policy, MX, DKIM key size, MTA-STS, TLS-RPT and DNSSEC for any domain, from your browser.",
          DNS_TOOL, "https://cloudflare-dns.com")


if __name__ == "__main__":
    main()
