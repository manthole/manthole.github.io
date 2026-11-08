"""Génère l'onglet « Exercices » : le hub /posts/ et les explications interactives
/explain/tls/, /explain/kerberoasting/, /explain/sql-injection/ (5 langues).
Composants animés par js/explain.js, styles dans css/cyber.css (section « Explications interactives »).
Usage : python3 scripts/make_explain.py <racine du site>"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
SITE = "https://manthole.github.io"


def L(fr, en, es, pt, de):
    return (f'<span lang="fr">{fr}</span><span lang="en">{en}</span><span lang="es">{es}</span>'
            f'<span lang="pt">{pt}</span><span lang="de">{de}</span>')


def t(x):
    return L(*x) if isinstance(x, tuple) else x


def chip_dot(inner):
    return f'<span class="x-chip"><span class="x-dot" aria-hidden="true"></span>{inner}</span>'


def chip_plain(inner):
    return f'<span class="x-chip x-chip--muted x-chip--plain">{inner}</span>'


def h3(k, x):
    return f'<h3 class="x-h {k}">{t(x)}</h3>'


# ---------------------------------------------------------------- composants

def stepper(k, n, actors, steps):
    """actors : [(nom, sous-titre)] ; steps : [(classes, label, sub, titre, texte)]"""
    acts = "".join(f'<div class="seq__actor">{t(a)}<small>{t(s)}</small></div>' for a, s in actors)
    msgs, panels = [], []
    for i, (cls, label, sub, title, body) in enumerate(steps, 1):
        note = "seq__note" in cls
        arrow = "" if note else '<span class="seq__arrow" aria-hidden="true"></span>'
        sub_html = f'<span class="seq__sub">{t(sub)}</span>' if sub else ""
        msgs.append(f'<li class="seq__msg {cls}" data-step="{i}"><span class="seq__label">{t(label)}</span>{arrow}{sub_html}</li>')
        title = tuple(re.sub(r"^\d+\.\s*", "", x) for x in title)  # le numéro est affiché par la pastille
        panels.append(f'<article class="ex-panel" data-step="{i}"><h4>{t(title)}</h4>{t(body)}</article>')
    prev = L("‹ Précédent", "‹ Previous", "‹ Anterior", "‹ Anterior", "‹ Zurück")
    nxt = L("Suivant ›", "Next ›", "Siguiente ›", "Seguinte ›", "Weiter ›")
    play = (f'<span class="ex-play__go">▶ {L("Lecture", "Play", "Reproducir", "Reproduzir", "Abspielen")}</span>'
            f'<span class="ex-play__pause">❚❚ {L("Pause", "Pause", "Pausa", "Pausa", "Pause")}</span>')
    hint = L("Avance avec « Suivant », les flèches ← → du clavier, ou lance l'animation.",
             "Step through with “Next”, the ← → arrow keys, or play the animation.",
             "Avanza con «Siguiente», las flechas ← → del teclado o reproduce la animación.",
             "Avança com «Seguinte», as setas ← → do teclado ou reproduz a animação.",
             "Schalte mit „Weiter“ oder den Pfeiltasten ← → weiter oder spiele die Animation ab.")
    return (f'<section class="ex {k}" data-stepper tabindex="0" data-reveal>'
            f'<div class="seq seq--{n}"><div class="seq__actors">{acts}</div>'
            f'<ol class="seq__msgs">{"".join(msgs)}</ol></div>'
            f'<p class="ex-hint ex-needs-js">{hint}</p>'
            f'<div class="ex-controls"><button type="button" data-ex="prev">{prev}</button>'
            f'<div class="ex-dots"></div>'
            f'<button type="button" data-ex="play" aria-pressed="false">{play}</button>'
            f'<button type="button" data-ex="next">{nxt}</button></div>'
            f'<div class="ex-panels">{"".join(panels)}</div></section>')


def keys(k, items):
    lis = "".join(f'<li data-reveal><strong>{t(a)}</strong>{t(b)}</li>' for a, b in items)
    return f'<ul class="ex-keys {k}">{lis}</ul>'


def pitch(k, text):
    return (f'<div class="x-term {k}" data-reveal><div class="x-term__bar"><span>~/pitch $ cat 30s.txt</span></div>'
            f'<p class="x-term__body">{t(text)}<span class="x-caret" aria-hidden="true"></span></p></div>')


def refs(k, items):
    rows = "".join(f'<li data-reveal><a class="x-row" href="{u}" rel="noopener" target="_blank">'
                   f'<span class="x-row__title">{name}</span> <span class="rt-res__desc">{t(d)}</span></a></li>'
                   for u, name, d in items)
    return f'<ul class="x-rows rt-res {k}">{rows}</ul>'


BACK = (f'<p class="x-links"><a class="x-btn" href="{SITE}/posts/">'
        + L("‹ Tous les exercices", "‹ All exercises", "‹ Todos los ejercicios", "‹ Todos os exercícios", "‹ Alle Übungen")
        + "</a></p>")

H_STEPS = ("Le déroulé, étape par étape", "Step by step", "Paso a paso", "Passo a passo", "Schritt für Schritt")
H_KEYS = ("À retenir", "Key takeaways", "Para recordar", "A reter", "Das Wichtigste")
H_PITCH = ("En 30 secondes", "In 30 seconds", "En 30 segundos", "Em 30 segundos", "In 30 Sekunden")
H_REFS = ("Pour aller plus loin", "Further reading", "Para saber más", "Para saber mais", "Weiterführend")

# ---------------------------------------------------------------- TLS 1.3

TLS = dict(
    slug="tls", k="k-teal",
    title=("Le handshake TLS 1.3", "The TLS 1.3 handshake", "El handshake de TLS 1.3", "O handshake TLS 1.3", "Der TLS-1.3-Handshake"),
    meta="TLS 1.3 handshake explained step by step: key exchange, certificate, CertificateVerify, Finished, and why a man-in-the-middle fails.",
    chips=[("Cryptographie", "Cryptography", "Criptografía", "Criptografia", "Kryptografie"), "RFC 8446", "1-RTT"],
    lead=("Ce qui se passe dans les ~50 ms entre le moment où tu tapes une adresse en <code>https://</code> et l'affichage de la page : comment deux machines qui ne se connaissent pas se mettent d'accord sur une clé secrète, sur un réseau où tout le monde peut écouter, et comment le navigateur sait qu'il parle au bon serveur.",
          "What happens in the ~50 ms between typing an <code>https://</code> address and the page showing up: how two machines that have never met agree on a secret key over a network anyone can listen to, and how the browser knows it is talking to the right server.",
          "Lo que pasa en los ~50 ms entre escribir una dirección <code>https://</code> y ver la página: cómo dos máquinas que no se conocen acuerdan una clave secreta en una red donde todos pueden escuchar, y cómo el navegador sabe que habla con el servidor correcto.",
          "O que acontece nos ~50 ms entre escrever um endereço <code>https://</code> e ver a página: como duas máquinas que não se conhecem acordam uma chave secreta numa rede onde todos podem escutar, e como o navegador sabe que fala com o servidor certo.",
          "Was in den ~50 ms zwischen der Eingabe einer <code>https://</code>-Adresse und der Anzeige der Seite passiert: wie sich zwei Rechner, die sich nicht kennen, über ein Netz, das jeder abhören kann, auf einen geheimen Schlüssel einigen – und woher der Browser weiß, dass er mit dem richtigen Server spricht."),
    n=2,
    actors=[(("Client", "Client", "Cliente", "Cliente", "Client"), ("navigateur", "browser", "navegador", "navegador", "Browser")),
            (("Serveur", "Server", "Servidor", "Servidor", "Server"), ("site web", "website", "sitio web", "site web", "Website"))],
    steps=[
        ("m-1-2", "ClientHello", "versions · suites · key_share · SNI",
         ("1. ClientHello : la proposition", "1. ClientHello: the offer", "1. ClientHello: la propuesta", "1. ClientHello: a proposta", "1. ClientHello: das Angebot"),
         L("<p>Le client envoie, <strong>en clair</strong> : les versions qu'il accepte (TLS 1.3), ses suites de chiffrement (par exemple <code>TLS_AES_128_GCM_SHA256</code>), un nombre aléatoire et le nom du site visé (SNI).</p><p>Surtout, il envoie déjà sa <strong>part de l'échange Diffie-Hellman</strong> (<code>key_share</code>, souvent X25519) : une clé publique éphémère, créée pour cette seule connexion. Il parie sur le groupe que le serveur acceptera, ce qui économise un aller-retour par rapport à TLS 1.2.</p>",
           "<p>The client sends, <strong>in the clear</strong>: the versions it accepts (TLS 1.3), its cipher suites (for example <code>TLS_AES_128_GCM_SHA256</code>), a random number and the name of the site (SNI).</p><p>Above all, it already sends its <strong>share of the Diffie-Hellman exchange</strong> (<code>key_share</code>, often X25519): an ephemeral public key, created for this connection only. It bets on the group the server will accept, which saves a round trip compared with TLS 1.2.</p>",
           "<p>El cliente envía, <strong>en claro</strong>: las versiones que acepta (TLS 1.3), sus suites de cifrado (por ejemplo <code>TLS_AES_128_GCM_SHA256</code>), un número aleatorio y el nombre del sitio (SNI).</p><p>Sobre todo, ya envía su <strong>parte del intercambio Diffie-Hellman</strong> (<code>key_share</code>, a menudo X25519): una clave pública efímera, creada solo para esta conexión. Apuesta por el grupo que aceptará el servidor, lo que ahorra un viaje de ida y vuelta respecto a TLS 1.2.</p>",
           "<p>O cliente envia, <strong>em claro</strong>: as versões que aceita (TLS 1.3), as suas suites de cifra (por exemplo <code>TLS_AES_128_GCM_SHA256</code>), um número aleatório e o nome do site (SNI).</p><p>Sobretudo, já envia a sua <strong>parte da troca Diffie-Hellman</strong> (<code>key_share</code>, muitas vezes X25519): uma chave pública efémera, criada só para esta ligação. Aposta no grupo que o servidor vai aceitar, o que poupa uma ida e volta em relação ao TLS 1.2.</p>",
           "<p>Der Client sendet <strong>im Klartext</strong>: die akzeptierten Versionen (TLS 1.3), seine Cipher Suites (zum Beispiel <code>TLS_AES_128_GCM_SHA256</code>), eine Zufallszahl und den Namen der Website (SNI).</p><p>Vor allem sendet er bereits seinen <strong>Anteil am Diffie-Hellman-Austausch</strong> (<code>key_share</code>, oft X25519): einen ephemeren öffentlichen Schlüssel, nur für diese Verbindung erzeugt. Er setzt auf die Gruppe, die der Server akzeptieren wird – das spart gegenüber TLS 1.2 einen Roundtrip.</p>")),
        ("m-2-1", "ServerHello", ("suite choisie · key_share", "chosen suite · key_share", "suite elegida · key_share", "suite escolhida · key_share", "gewählte Suite · key_share"),
         ("2. ServerHello : l'accord", "2. ServerHello: the agreement", "2. ServerHello: el acuerdo", "2. ServerHello: o acordo", "2. ServerHello: die Einigung"),
         L("<p>Le serveur choisit une suite et renvoie <strong>sa</strong> clé publique éphémère. C'est le dernier message en clair.</p><p>Chacun combine sa clé privée éphémère avec la clé publique de l'autre (ECDHE) et obtient <strong>le même secret partagé</strong>, sans qu'il ait jamais circulé sur le réseau. Un espion qui a tout enregistré ne peut pas le recalculer.</p>",
           "<p>The server picks a suite and sends back <strong>its</strong> ephemeral public key. This is the last message in the clear.</p><p>Each side combines its ephemeral private key with the other's public key (ECDHE) and gets <strong>the same shared secret</strong>, without it ever crossing the network. An eavesdropper who recorded everything cannot recompute it.</p>",
           "<p>El servidor elige una suite y devuelve <strong>su</strong> clave pública efímera. Es el último mensaje en claro.</p><p>Cada uno combina su clave privada efímera con la clave pública del otro (ECDHE) y obtiene <strong>el mismo secreto compartido</strong>, sin que haya circulado nunca por la red. Un espía que lo haya grabado todo no puede recalcularlo.</p>",
           "<p>O servidor escolhe uma suite e devolve <strong>a sua</strong> chave pública efémera. É a última mensagem em claro.</p><p>Cada um combina a sua chave privada efémera com a chave pública do outro (ECDHE) e obtém <strong>o mesmo segredo partilhado</strong>, sem que ele tenha alguma vez circulado na rede. Um espião que tenha gravado tudo não o consegue recalcular.</p>",
           "<p>Der Server wählt eine Suite und schickt <strong>seinen</strong> ephemeren öffentlichen Schlüssel zurück. Das ist die letzte Klartext-Nachricht.</p><p>Beide Seiten kombinieren ihren ephemeren privaten Schlüssel mit dem öffentlichen Schlüssel der anderen (ECDHE) und erhalten <strong>dasselbe gemeinsame Geheimnis</strong>, ohne dass es je über das Netz ging. Ein Lauscher, der alles aufgezeichnet hat, kann es nicht berechnen.</p>")),
        ("seq__note n-1-2", "🔑 ECDHE → HKDF", ("clés de handshake dérivées", "handshake keys derived", "claves de handshake derivadas", "chaves de handshake derivadas", "Handshake-Schlüssel abgeleitet"),
         ("3. Les clés sont dérivées", "3. The keys are derived", "3. Se derivan las claves", "3. As chaves são derivadas", "3. Die Schlüssel werden abgeleitet"),
         L("<p>Le secret partagé passe dans <strong>HKDF</strong>, une fonction de dérivation, avec l'empreinte des messages déjà échangés. On en tire des clés distinctes pour chaque sens et chaque phase.</p><p>À partir d'ici, <strong>tout est chiffré</strong> : un observateur ne voit plus que des données opaques, y compris le certificat (en TLS 1.2, il passait en clair).</p>",
           "<p>The shared secret goes through <strong>HKDF</strong>, a key derivation function, together with the hash of the messages exchanged so far. Separate keys come out for each direction and each phase.</p><p>From here on, <strong>everything is encrypted</strong>: an observer only sees opaque data, including the certificate (in TLS 1.2 it was sent in the clear).</p>",
           "<p>El secreto compartido pasa por <strong>HKDF</strong>, una función de derivación, junto con la huella de los mensajes ya intercambiados. Se obtienen claves distintas para cada sentido y cada fase.</p><p>A partir de aquí, <strong>todo va cifrado</strong>: un observador solo ve datos opacos, incluido el certificado (en TLS 1.2 viajaba en claro).</p>",
           "<p>O segredo partilhado passa pela <strong>HKDF</strong>, uma função de derivação, juntamente com a impressão das mensagens já trocadas. Obtêm-se chaves distintas para cada sentido e cada fase.</p><p>A partir daqui, <strong>tudo é cifrado</strong>: um observador só vê dados opacos, incluindo o certificado (no TLS 1.2 seguia em claro).</p>",
           "<p>Das gemeinsame Geheimnis durchläuft <strong>HKDF</strong>, eine Schlüsselableitungsfunktion, zusammen mit dem Hash der bisher ausgetauschten Nachrichten. Daraus entstehen getrennte Schlüssel für jede Richtung und jede Phase.</p><p>Ab hier ist <strong>alles verschlüsselt</strong>: Ein Beobachter sieht nur noch undurchsichtige Daten, auch das Zertifikat (bei TLS 1.2 ging es im Klartext).</p>")),
        ("m-2-1", '<span class="seq__lock">🔒</span> EncryptedExtensions', ("ALPN (h2) …", "ALPN (h2) …", "ALPN (h2) …", "ALPN (h2) …", "ALPN (h2) …"),
         ("4. EncryptedExtensions", "4. EncryptedExtensions", "4. EncryptedExtensions", "4. EncryptedExtensions", "4. EncryptedExtensions"),
         L("<p>Premier message chiffré : les paramètres qui n'ont pas besoin d'être visibles, par exemple le protocole applicatif choisi (ALPN : <code>h2</code> pour HTTP/2).</p>",
           "<p>First encrypted message: the parameters that don't need to be visible, for example the chosen application protocol (ALPN: <code>h2</code> for HTTP/2).</p>",
           "<p>Primer mensaje cifrado: los parámetros que no necesitan ser visibles, por ejemplo el protocolo de aplicación elegido (ALPN: <code>h2</code> para HTTP/2).</p>",
           "<p>Primeira mensagem cifrada: os parâmetros que não precisam de ser visíveis, por exemplo o protocolo aplicacional escolhido (ALPN: <code>h2</code> para HTTP/2).</p>",
           "<p>Erste verschlüsselte Nachricht: die Parameter, die nicht sichtbar sein müssen, zum Beispiel das gewählte Anwendungsprotokoll (ALPN: <code>h2</code> für HTTP/2).</p>")),
        ("m-2-1", '<span class="seq__lock">🔒</span> Certificate', ("chaîne X.509", "X.509 chain", "cadena X.509", "cadeia X.509", "X.509-Kette"),
         ("5. Certificate : qui je suis", "5. Certificate: who I am", "5. Certificate: quién soy", "5. Certificate: quem sou", "5. Certificate: wer ich bin"),
         L("<p>Le serveur envoie sa chaîne de certificats : sa clé publique <strong>longue durée</strong>, signée par une autorité de certification (AC).</p><p>Le client vérifie que la chaîne remonte à une AC de son magasin de confiance, que le certificat est valide aujourd'hui et que le nom (SAN) correspond bien au site demandé.</p>",
           "<p>The server sends its certificate chain: its <strong>long-term</strong> public key, signed by a certificate authority (CA).</p><p>The client checks that the chain leads to a CA in its trust store, that the certificate is valid today and that the name (SAN) matches the requested site.</p>",
           "<p>El servidor envía su cadena de certificados: su clave pública <strong>de larga duración</strong>, firmada por una autoridad de certificación (AC).</p><p>El cliente comprueba que la cadena llega a una AC de su almacén de confianza, que el certificado es válido hoy y que el nombre (SAN) coincide con el sitio pedido.</p>",
           "<p>O servidor envia a sua cadeia de certificados: a sua chave pública <strong>de longa duração</strong>, assinada por uma autoridade de certificação (AC).</p><p>O cliente verifica que a cadeia chega a uma AC do seu repositório de confiança, que o certificado é válido hoje e que o nome (SAN) corresponde ao site pedido.</p>",
           "<p>Der Server sendet seine Zertifikatskette: seinen <strong>langlebigen</strong> öffentlichen Schlüssel, signiert von einer Zertifizierungsstelle (CA).</p><p>Der Client prüft, dass die Kette zu einer CA in seinem Vertrauensspeicher führt, dass das Zertifikat heute gültig ist und dass der Name (SAN) zur angefragten Website passt.</p>")),
        ("m-2-1", '<span class="seq__lock">🔒</span> CertificateVerify', ("signature de la transcription", "signature over the transcript", "firma de la transcripción", "assinatura da transcrição", "Signatur über das Transkript"),
         ("6. CertificateVerify : la preuve", "6. CertificateVerify: the proof", "6. CertificateVerify: la prueba", "6. CertificateVerify: a prova", "6. CertificateVerify: der Beweis"),
         L("<p>Un certificat est public : n'importe qui peut le recopier. Le serveur doit donc prouver qu'il détient la <strong>clé privée</strong> correspondante.</p><p>Il signe avec elle l'empreinte de <strong>toute la conversation</strong> jusqu'ici, y compris les deux <code>key_share</code>. Cette signature lie l'échange de clés à l'identité du serveur : c'est elle qui empêche un intermédiaire de glisser sa propre clé.</p>",
           "<p>A certificate is public: anyone can copy it. So the server must prove it holds the matching <strong>private key</strong>.</p><p>It signs with it the hash of <strong>the whole conversation</strong> so far, including both <code>key_share</code> values. This signature binds the key exchange to the server's identity: it is what stops someone in the middle from slipping in their own key.</p>",
           "<p>Un certificado es público: cualquiera puede copiarlo. El servidor debe demostrar que posee la <strong>clave privada</strong> correspondiente.</p><p>Firma con ella la huella de <strong>toda la conversación</strong> hasta ahora, incluidos los dos <code>key_share</code>. Esta firma vincula el intercambio de claves con la identidad del servidor: es lo que impide que un intermediario cuele su propia clave.</p>",
           "<p>Um certificado é público: qualquer pessoa o pode copiar. O servidor tem, por isso, de provar que detém a <strong>chave privada</strong> correspondente.</p><p>Assina com ela a impressão de <strong>toda a conversa</strong> até aqui, incluindo os dois <code>key_share</code>. Esta assinatura liga a troca de chaves à identidade do servidor: é ela que impede um intermediário de introduzir a sua própria chave.</p>",
           "<p>Ein Zertifikat ist öffentlich: Jeder kann es kopieren. Der Server muss also beweisen, dass er den passenden <strong>privaten Schlüssel</strong> besitzt.</p><p>Damit signiert er den Hash <strong>des gesamten bisherigen Gesprächs</strong>, einschließlich beider <code>key_share</code>-Werte. Diese Signatur bindet den Schlüsselaustausch an die Identität des Servers: Genau sie verhindert, dass ein Mittelsmann seinen eigenen Schlüssel einschmuggelt.</p>")),
        ("m-2-1", '<span class="seq__lock">🔒</span> Finished', ("MAC de la transcription", "MAC over the transcript", "MAC de la transcripción", "MAC da transcrição", "MAC über das Transkript"),
         ("7. Finished (serveur)", "7. Finished (server)", "7. Finished (servidor)", "7. Finished (servidor)", "7. Finished (Server)"),
         L("<p>Un code d'authentification (HMAC) calculé sur toute la transcription avec une clé issue du secret partagé. Si un seul octet des messages précédents avait été modifié, par exemple pour forcer une suite plus faible, les deux côtés n'obtiendraient pas la même valeur.</p>",
           "<p>An authentication code (HMAC) over the whole transcript, using a key derived from the shared secret. If a single byte of the previous messages had been altered, for example to force a weaker suite, the two sides would not get the same value.</p>",
           "<p>Un código de autenticación (HMAC) calculado sobre toda la transcripción con una clave derivada del secreto compartido. Si se hubiera modificado un solo byte de los mensajes anteriores, por ejemplo para forzar una suite más débil, ambos lados no obtendrían el mismo valor.</p>",
           "<p>Um código de autenticação (HMAC) calculado sobre toda a transcrição com uma chave derivada do segredo partilhado. Se um único byte das mensagens anteriores tivesse sido alterado, por exemplo para forçar uma suite mais fraca, os dois lados não obteriam o mesmo valor.</p>",
           "<p>Ein Authentifizierungscode (HMAC) über das gesamte Transkript, mit einem aus dem gemeinsamen Geheimnis abgeleiteten Schlüssel. Wäre auch nur ein Byte der vorherigen Nachrichten verändert worden, etwa um eine schwächere Suite zu erzwingen, kämen beide Seiten nicht auf denselben Wert.</p>")),
        ("m-1-2", '<span class="seq__lock">🔒</span> Finished', ("le client confirme", "the client confirms", "el cliente confirma", "o cliente confirma", "der Client bestätigt"),
         ("8. Finished (client)", "8. Finished (client)", "8. Finished (cliente)", "8. Finished (cliente)", "8. Finished (Client)"),
         L("<p>Le client a tout vérifié (chaîne, signature, Finished du serveur) et envoie son propre Finished. Le handshake est terminé en <strong>un seul aller-retour</strong> (1-RTT). Les clés de session applicatives sont dérivées à leur tour.</p>",
           "<p>The client has checked everything (chain, signature, server Finished) and sends its own Finished. The handshake is done in <strong>a single round trip</strong> (1-RTT). The application session keys are derived in turn.</p>",
           "<p>El cliente lo ha comprobado todo (cadena, firma, Finished del servidor) y envía su propio Finished. El handshake termina en <strong>un solo viaje de ida y vuelta</strong> (1-RTT). Se derivan a su vez las claves de sesión de la aplicación.</p>",
           "<p>O cliente verificou tudo (cadeia, assinatura, Finished do servidor) e envia o seu próprio Finished. O handshake termina numa <strong>única ida e volta</strong> (1-RTT). As chaves de sessão aplicacionais são derivadas por sua vez.</p>",
           "<p>Der Client hat alles geprüft (Kette, Signatur, Finished des Servers) und sendet sein eigenes Finished. Der Handshake ist nach <strong>einem einzigen Roundtrip</strong> fertig (1-RTT). Danach werden die Sitzungsschlüssel für die Anwendung abgeleitet.</p>")),
        ("m-1-2", '<span class="seq__lock">🔒</span> GET / ⇄ 200 OK', ("données applicatives (AEAD)", "application data (AEAD)", "datos de aplicación (AEAD)", "dados aplicacionais (AEAD)", "Anwendungsdaten (AEAD)"),
         ("9. Les données circulent", "9. Data flows", "9. Circulan los datos", "9. Os dados circulam", "9. Die Daten fließen"),
         L("<p>Les requêtes HTTP passent maintenant dans des enregistrements chiffrés et authentifiés par un algorithme <strong>AEAD</strong> (AES-GCM ou ChaCha20-Poly1305). Chaque enregistrement porte un numéro de séquence implicite : un paquet modifié, rejoué ou réordonné est rejeté.</p>",
           "<p>HTTP requests now travel in records encrypted and authenticated by an <strong>AEAD</strong> algorithm (AES-GCM or ChaCha20-Poly1305). Each record has an implicit sequence number: a modified, replayed or reordered packet is rejected.</p>",
           "<p>Las peticiones HTTP viajan ahora en registros cifrados y autenticados por un algoritmo <strong>AEAD</strong> (AES-GCM o ChaCha20-Poly1305). Cada registro lleva un número de secuencia implícito: un paquete modificado, repetido o reordenado se rechaza.</p>",
           "<p>Os pedidos HTTP seguem agora em registos cifrados e autenticados por um algoritmo <strong>AEAD</strong> (AES-GCM ou ChaCha20-Poly1305). Cada registo tem um número de sequência implícito: um pacote modificado, repetido ou reordenado é rejeitado.</p>",
           "<p>HTTP-Anfragen laufen jetzt in Records, die mit einem <strong>AEAD</strong>-Verfahren (AES-GCM oder ChaCha20-Poly1305) verschlüsselt und authentifiziert sind. Jeder Record hat eine implizite Sequenznummer: Ein verändertes, wiederholtes oder umsortiertes Paket wird verworfen.</p>")),
        ("seq__note seq__note--alert n-1-2", ("⚠ Et un attaquant au milieu ?", "⚠ What about a man in the middle?", "⚠ ¿Y un atacante en medio?", "⚠ E um atacante no meio?", "⚠ Und ein Mittelsmann?"),
         ("il lui manque la clé privée", "it lacks the private key", "le falta la clave privada", "falta-lhe a chave privada", "ihm fehlt der private Schlüssel"),
         ("10. Pourquoi l'interception échoue", "10. Why interception fails", "10. Por qué falla la interceptación", "10. Porque é que a interceção falha", "10. Warum das Abfangen scheitert"),
         L("<p>Un attaquant placé entre les deux peut faire son propre échange ECDHE avec le client. Mais ensuite :</p><ul><li>s'il renvoie le <strong>vrai certificat</strong>, il ne peut pas produire de CertificateVerify valide : il n'a pas la clé privée ;</li><li>s'il présente <strong>son propre certificat</strong>, il n'est pas signé par une AC de confiance pour ce nom, et le navigateur affiche une alerte.</li></ul><p>D'où la règle : ne jamais « continuer quand même » sur une alerte de certificat. Et comme les clés ECDHE sont jetées après usage (<em>forward secrecy</em>), voler plus tard la clé privée du serveur ne permet pas de déchiffrer le trafic enregistré.</p>",
           "<p>An attacker sitting between them can run their own ECDHE exchange with the client. But then:</p><ul><li>if they forward the <strong>real certificate</strong>, they cannot produce a valid CertificateVerify: they don't have the private key;</li><li>if they present <strong>their own certificate</strong>, it isn't signed by a trusted CA for that name, and the browser shows a warning.</li></ul><p>Hence the rule: never “proceed anyway” past a certificate warning. And since the ECDHE keys are thrown away after use (<em>forward secrecy</em>), stealing the server's private key later doesn't decrypt recorded traffic.</p>",
           "<p>Un atacante situado entre ambos puede hacer su propio intercambio ECDHE con el cliente. Pero luego:</p><ul><li>si reenvía el <strong>certificado auténtico</strong>, no puede producir un CertificateVerify válido: no tiene la clave privada;</li><li>si presenta <strong>su propio certificado</strong>, no está firmado por una AC de confianza para ese nombre y el navegador muestra una alerta.</li></ul><p>De ahí la regla: nunca «continuar de todos modos» ante una alerta de certificado. Y como las claves ECDHE se desechan tras usarlas (<em>forward secrecy</em>), robar más tarde la clave privada del servidor no permite descifrar el tráfico grabado.</p>",
           "<p>Um atacante colocado entre os dois pode fazer a sua própria troca ECDHE com o cliente. Mas depois:</p><ul><li>se reenviar o <strong>certificado verdadeiro</strong>, não consegue produzir um CertificateVerify válido: não tem a chave privada;</li><li>se apresentar <strong>o seu próprio certificado</strong>, este não está assinado por uma AC de confiança para esse nome e o navegador mostra um alerta.</li></ul><p>Daí a regra: nunca «continuar mesmo assim» perante um alerta de certificado. E como as chaves ECDHE são descartadas após o uso (<em>forward secrecy</em>), roubar mais tarde a chave privada do servidor não permite decifrar o tráfego gravado.</p>",
           "<p>Ein Angreifer zwischen beiden kann seinen eigenen ECDHE-Austausch mit dem Client durchführen. Aber dann:</p><ul><li>leitet er das <strong>echte Zertifikat</strong> weiter, kann er kein gültiges CertificateVerify erzeugen: Ihm fehlt der private Schlüssel;</li><li>legt er <strong>sein eigenes Zertifikat</strong> vor, ist es für diesen Namen nicht von einer vertrauenswürdigen CA signiert, und der Browser zeigt eine Warnung.</li></ul><p>Daher die Regel: Bei einer Zertifikatswarnung niemals „trotzdem fortfahren“. Und weil die ECDHE-Schlüssel nach Gebrauch verworfen werden (<em>Forward Secrecy</em>), entschlüsselt ein späterer Diebstahl des privaten Server-Schlüssels keinen aufgezeichneten Verkehr.</p>")),
    ],
    keys=[(("Confidentialité", "Confidentiality", "Confidencialidad", "Confidencialidade", "Vertraulichkeit"),
           ("ECDHE éphémère + chiffrement AEAD. Les clés jetables apportent la <em>forward secrecy</em>.", "Ephemeral ECDHE + AEAD encryption. Throwaway keys give <em>forward secrecy</em>.", "ECDHE efímero + cifrado AEAD. Las claves desechables aportan <em>forward secrecy</em>.", "ECDHE efémero + cifra AEAD. As chaves descartáveis dão <em>forward secrecy</em>.", "Ephemeres ECDHE + AEAD-Verschlüsselung. Wegwerfschlüssel bringen <em>Forward Secrecy</em>.")),
          (("Authentification", "Authentication", "Autenticación", "Autenticação", "Authentifizierung"),
           ("Certificate dit qui est le serveur, CertificateVerify prouve qu'il détient la clé privée.", "Certificate says who the server is, CertificateVerify proves it holds the private key.", "Certificate dice quién es el servidor, CertificateVerify demuestra que tiene la clave privada.", "Certificate diz quem é o servidor, CertificateVerify prova que detém a chave privada.", "Certificate sagt, wer der Server ist, CertificateVerify beweist, dass er den privaten Schlüssel hat.")),
          (("Intégrité", "Integrity", "Integridad", "Integridade", "Integrität"),
           ("Finished protège le handshake contre toute modification, l'AEAD protège chaque enregistrement.", "Finished protects the handshake against tampering, AEAD protects every record.", "Finished protege el handshake contra cualquier modificación, el AEAD protege cada registro.", "Finished protege o handshake contra qualquer alteração, o AEAD protege cada registo.", "Finished schützt den Handshake vor Manipulation, AEAD schützt jeden Record."))],
    pitch=("Le client et le serveur font un échange Diffie-Hellman éphémère dès le premier aller-retour : ils obtiennent un secret commun qui n'a jamais circulé. Le serveur prouve son identité avec son certificat et une signature de toute la conversation, ce qui bloque l'homme du milieu. Les messages Finished garantissent que rien n'a été modifié, puis tout le trafic est chiffré et authentifié en AEAD.",
           "Client and server run an ephemeral Diffie-Hellman exchange in the very first round trip: they get a shared secret that never crossed the wire. The server proves its identity with its certificate and a signature over the whole conversation, which blocks a man in the middle. The Finished messages guarantee nothing was altered, then all traffic is encrypted and authenticated with AEAD.",
           "Cliente y servidor hacen un intercambio Diffie-Hellman efímero desde el primer viaje de ida y vuelta: obtienen un secreto común que nunca ha circulado. El servidor demuestra su identidad con su certificado y una firma de toda la conversación, lo que bloquea al intermediario. Los mensajes Finished garantizan que nada se ha modificado y después todo el tráfico va cifrado y autenticado con AEAD.",
           "Cliente e servidor fazem uma troca Diffie-Hellman efémera logo na primeira ida e volta: obtêm um segredo comum que nunca circulou. O servidor prova a sua identidade com o certificado e uma assinatura de toda a conversa, o que bloqueia o intermediário. As mensagens Finished garantem que nada foi alterado e depois todo o tráfego é cifrado e autenticado em AEAD.",
           "Client und Server führen schon im ersten Roundtrip einen ephemeren Diffie-Hellman-Austausch durch: Sie erhalten ein gemeinsames Geheimnis, das nie übertragen wurde. Der Server beweist seine Identität mit seinem Zertifikat und einer Signatur über das ganze Gespräch – das stoppt den Mittelsmann. Die Finished-Nachrichten garantieren, dass nichts verändert wurde, danach ist der gesamte Verkehr per AEAD verschlüsselt und authentifiziert."),
    refs=[("https://www.rfc-editor.org/rfc/rfc8446", "RFC 8446",
           ("La spécification officielle de TLS 1.3.", "The official TLS 1.3 specification.", "La especificación oficial de TLS 1.3.", "A especificação oficial do TLS 1.3.", "Die offizielle TLS-1.3-Spezifikation.")),
          ("https://tls13.xargs.org/", "The Illustrated TLS 1.3 Connection",
           ("Une vraie connexion décortiquée octet par octet.", "A real connection dissected byte by byte.", "Una conexión real desmenuzada byte a byte.", "Uma ligação real dissecada byte a byte.", "Eine echte Verbindung, Byte für Byte zerlegt."))],
)

# ---------------------------------------------------------------- Kerberoasting

KERB = dict(
    slug="kerberoasting", k="k-orange",
    title=("L'attaque Kerberoasting", "The Kerberoasting attack", "El ataque Kerberoasting", "O ataque Kerberoasting", "Der Kerberoasting-Angriff"),
    meta="Kerberoasting explained step by step: why any domain user can request a service ticket, offline cracking, RC4 vs AES, detection with event 4769 and defenses (gMSA, long passwords).",
    chips=[("Active Directory", "Active Directory", "Active Directory", "Active Directory", "Active Directory"), "MITRE T1558.003", ("Défense", "Defense", "Defensa", "Defesa", "Abwehr")],
    lead=("Une attaque très courante dans les tests d'intrusion Active Directory : avec un simple compte utilisateur du domaine, on obtient de quoi deviner hors ligne le mot de passe d'un compte de service, sans jamais toucher le service ni déclencher de verrouillage. Comprendre le mécanisme, c'est aussi savoir le détecter et le rendre inutile.",
          "A very common attack in Active Directory penetration tests: with a plain domain user account, you get material to guess a service account's password offline, without ever touching the service or triggering a lockout. Understanding the mechanism is also knowing how to detect it and make it useless.",
          "Un ataque muy habitual en las pruebas de intrusión de Active Directory: con una simple cuenta de usuario del dominio se obtiene material para adivinar sin conexión la contraseña de una cuenta de servicio, sin tocar nunca el servicio ni provocar bloqueos. Entender el mecanismo es también saber detectarlo y volverlo inútil.",
          "Um ataque muito comum nos testes de intrusão de Active Directory: com uma simples conta de utilizador do domínio obtém-se material para adivinhar offline a palavra-passe de uma conta de serviço, sem nunca tocar no serviço nem provocar bloqueios. Compreender o mecanismo é também saber detetá-lo e torná-lo inútil.",
          "Ein sehr häufiger Angriff bei Active-Directory-Pentests: Mit einem einfachen Domänenbenutzerkonto erhält man Material, um das Passwort eines Dienstkontos offline zu erraten – ohne den Dienst je zu berühren oder eine Sperre auszulösen. Den Mechanismus zu verstehen heißt auch, ihn erkennen und nutzlos machen zu können."),
    n=3,
    actors=[(("Attaquant", "Attacker", "Atacante", "Atacante", "Angreifer"), ("compte du domaine", "domain account", "cuenta del dominio", "conta do domínio", "Domänenkonto")),
            ("KDC", ("contrôleur de domaine", "domain controller", "controlador de dominio", "controlador de domínio", "Domänencontroller")),
            (("Service SQL", "SQL service", "Servicio SQL", "Serviço SQL", "SQL-Dienst"), "svc_sql")],
    steps=[
        ("m-1-2", "AS-REQ", ("authentification", "authentication", "autenticación", "autenticação", "Authentifizierung"),
         ("1. Un simple compte suffit", "1. A plain account is enough", "1. Basta una cuenta normal", "1. Basta uma conta simples", "1. Ein normales Konto genügt"),
         L("<p>L'attaquant dispose d'un compte du domaine quelconque, sans droits particuliers : obtenu par hameçonnage, réutilisation de mot de passe ou simplement un poste compromis. Il s'authentifie auprès du KDC (le service Kerberos du contrôleur de domaine).</p>",
           "<p>The attacker has any domain account, with no special rights: obtained through phishing, password reuse or simply a compromised workstation. They authenticate to the KDC (the domain controller's Kerberos service).</p>",
           "<p>El atacante dispone de una cuenta cualquiera del dominio, sin derechos especiales: obtenida por phishing, reutilización de contraseñas o simplemente un equipo comprometido. Se autentica ante el KDC (el servicio Kerberos del controlador de dominio).</p>",
           "<p>O atacante dispõe de uma conta qualquer do domínio, sem direitos especiais: obtida por phishing, reutilização de palavras-passe ou simplesmente um posto comprometido. Autentica-se junto do KDC (o serviço Kerberos do controlador de domínio).</p>",
           "<p>Der Angreifer hat irgendein Domänenkonto ohne besondere Rechte: per Phishing, Passwort-Wiederverwendung oder einfach über einen kompromittierten Arbeitsplatz. Er authentifiziert sich beim KDC (dem Kerberos-Dienst des Domänencontrollers).</p>")),
        ("m-2-1", "AS-REP · TGT", ("ticket d'accès général", "ticket-granting ticket", "ticket de acceso general", "ticket de acesso geral", "Ticket-Granting-Ticket"),
         ("2. Le TGT", "2. The TGT", "2. El TGT", "2. O TGT", "2. Das TGT"),
         L("<p>Le KDC renvoie un <strong>TGT</strong> (Ticket-Granting Ticket), une sorte de badge qui permettra de demander des tickets pour n'importe quel service du domaine sans retaper son mot de passe. Tout est encore parfaitement normal.</p>",
           "<p>The KDC returns a <strong>TGT</strong> (Ticket-Granting Ticket), a kind of badge used to request tickets for any service in the domain without typing the password again. Everything is still perfectly normal.</p>",
           "<p>El KDC devuelve un <strong>TGT</strong> (Ticket-Granting Ticket), una especie de credencial que permitirá pedir tickets para cualquier servicio del dominio sin volver a escribir la contraseña. Todo sigue siendo totalmente normal.</p>",
           "<p>O KDC devolve um <strong>TGT</strong> (Ticket-Granting Ticket), uma espécie de crachá que permite pedir tickets para qualquer serviço do domínio sem voltar a escrever a palavra-passe. Tudo continua perfeitamente normal.</p>",
           "<p>Der KDC gibt ein <strong>TGT</strong> (Ticket-Granting Ticket) zurück, eine Art Ausweis, mit dem man Tickets für jeden Dienst der Domäne anfordern kann, ohne das Passwort erneut einzugeben. Alles ist noch völlig normal.</p>")),
        ("m-1-2", "TGS-REQ", "SPN MSSQLSvc/sql01",
         ("3. Demander un ticket de service", "3. Requesting a service ticket", "3. Pedir un ticket de servicio", "3. Pedir um ticket de serviço", "3. Ein Service-Ticket anfordern"),
         L("<p>Les comptes qui font tourner un service sont identifiés par un <strong>SPN</strong> (Service Principal Name), et la liste des SPN est lisible par <strong>tout utilisateur authentifié</strong> via LDAP. L'attaquant repère les comptes <em>utilisateurs</em> qui portent un SPN, comme <code>svc_sql</code>, et demande un ticket pour chacun.</p><p>C'est une requête légitime : c'est exactement ce que fait un poste qui veut se connecter au serveur SQL.</p>",
           "<p>Accounts that run a service are identified by an <strong>SPN</strong> (Service Principal Name), and the list of SPNs is readable by <strong>any authenticated user</strong> over LDAP. The attacker spots <em>user</em> accounts that carry an SPN, such as <code>svc_sql</code>, and requests a ticket for each one.</p><p>This is a legitimate request: it is exactly what a workstation does when it wants to connect to the SQL server.</p>",
           "<p>Las cuentas que ejecutan un servicio se identifican con un <strong>SPN</strong> (Service Principal Name), y la lista de SPN es legible por <strong>cualquier usuario autenticado</strong> mediante LDAP. El atacante localiza las cuentas de <em>usuario</em> que llevan un SPN, como <code>svc_sql</code>, y pide un ticket para cada una.</p><p>Es una petición legítima: es exactamente lo que hace un equipo que quiere conectarse al servidor SQL.</p>",
           "<p>As contas que executam um serviço são identificadas por um <strong>SPN</strong> (Service Principal Name), e a lista de SPN é legível por <strong>qualquer utilizador autenticado</strong> via LDAP. O atacante localiza as contas de <em>utilizador</em> que têm um SPN, como <code>svc_sql</code>, e pede um ticket para cada uma.</p><p>É um pedido legítimo: é exatamente o que faz um posto que se quer ligar ao servidor SQL.</p>",
           "<p>Konten, die einen Dienst ausführen, werden über einen <strong>SPN</strong> (Service Principal Name) identifiziert, und die SPN-Liste ist für <strong>jeden authentifizierten Benutzer</strong> per LDAP lesbar. Der Angreifer sucht <em>Benutzer</em>konten mit SPN, etwa <code>svc_sql</code>, und fordert für jedes ein Ticket an.</p><p>Das ist eine legitime Anfrage: Genau das tut ein Arbeitsplatz, der sich mit dem SQL-Server verbinden will.</p>")),
        ("m-2-1 is-bad", "TGS-REP", ("chiffré avec la clé de svc_sql", "encrypted with svc_sql's key", "cifrado con la clave de svc_sql", "cifrado com a chave de svc_sql", "mit dem Schlüssel von svc_sql verschlüsselt"),
         ("4. Le cœur du problème", "4. The heart of the problem", "4. El núcleo del problema", "4. O cerne do problema", "4. Der Kern des Problems"),
         L("<p>Le KDC ne vérifie pas si le demandeur a le droit d'utiliser le service : c'est le rôle du service lui-même. Il délivre donc le ticket.</p><p>Or une partie de ce ticket est <strong>chiffrée avec une clé dérivée du mot de passe du compte de service</strong> (pour que seul le service puisse la lire). L'attaquant a maintenant entre les mains un bloc chiffré avec une clé qui vient d'un mot de passe choisi par un humain.</p>",
           "<p>The KDC doesn't check whether the requester is allowed to use the service: that is the service's own job. So it issues the ticket.</p><p>But part of that ticket is <strong>encrypted with a key derived from the service account's password</strong> (so that only the service can read it). The attacker now holds a block encrypted with a key that comes from a human-chosen password.</p>",
           "<p>El KDC no comprueba si el solicitante tiene derecho a usar el servicio: esa es tarea del propio servicio. Así que entrega el ticket.</p><p>Pero una parte de ese ticket está <strong>cifrada con una clave derivada de la contraseña de la cuenta de servicio</strong> (para que solo el servicio pueda leerla). El atacante tiene ahora un bloque cifrado con una clave que procede de una contraseña elegida por una persona.</p>",
           "<p>O KDC não verifica se quem pede tem direito a usar o serviço: isso cabe ao próprio serviço. Por isso entrega o ticket.</p><p>Ora, uma parte desse ticket está <strong>cifrada com uma chave derivada da palavra-passe da conta de serviço</strong> (para que só o serviço a possa ler). O atacante tem agora nas mãos um bloco cifrado com uma chave que vem de uma palavra-passe escolhida por uma pessoa.</p>",
           "<p>Der KDC prüft nicht, ob der Anfragende den Dienst nutzen darf: Das ist Aufgabe des Dienstes selbst. Also stellt er das Ticket aus.</p><p>Ein Teil dieses Tickets ist jedoch <strong>mit einem aus dem Passwort des Dienstkontos abgeleiteten Schlüssel verschlüsselt</strong> (damit nur der Dienst ihn lesen kann). Der Angreifer hält nun einen Block in der Hand, der mit einem Schlüssel aus einem von Menschen gewählten Passwort verschlüsselt ist.</p>")),
        ("seq__note n-3", ("💤 jamais contacté", "💤 never contacted", "💤 nunca contactado", "💤 nunca contactado", "💤 nie kontaktiert"), ("aucune trace ici", "no trace here", "ningún rastro aquí", "nenhum rasto aqui", "keine Spur hier"),
         ("5. Le service ne voit rien", "5. The service sees nothing", "5. El servicio no ve nada", "5. O serviço não vê nada", "5. Der Dienst sieht nichts"),
         L("<p>L'attaquant n'utilise jamais le ticket : aucun paquet n'arrive au serveur SQL, rien dans ses journaux. La seule trace se trouve sur le contrôleur de domaine, noyée parmi des milliers de demandes de tickets légitimes.</p>",
           "<p>The attacker never uses the ticket: no packet reaches the SQL server, nothing shows up in its logs. The only trace is on the domain controller, buried among thousands of legitimate ticket requests.</p>",
           "<p>El atacante nunca usa el ticket: ningún paquete llega al servidor SQL, nada en sus registros. El único rastro está en el controlador de dominio, perdido entre miles de peticiones de tickets legítimas.</p>",
           "<p>O atacante nunca usa o ticket: nenhum pacote chega ao servidor SQL, nada nos seus registos. O único rasto está no controlador de domínio, perdido entre milhares de pedidos de tickets legítimos.</p>",
           "<p>Der Angreifer nutzt das Ticket nie: Kein Paket erreicht den SQL-Server, nichts in dessen Logs. Die einzige Spur liegt auf dem Domänencontroller, versteckt zwischen tausenden legitimen Ticket-Anfragen.</p>")),
        ("seq__note seq__note--alert n-1", ("🔥 cassage hors ligne", "🔥 offline cracking", "🔥 cracking sin conexión", "🔥 cracking offline", "🔥 Offline-Cracking"), ("sur sa propre machine", "on their own machine", "en su propia máquina", "na própria máquina", "auf dem eigenen Rechner"),
         ("6. Deviner le mot de passe, hors ligne", "6. Guessing the password, offline", "6. Adivinar la contraseña, sin conexión", "6. Adivinhar a palavra-passe, offline", "6. Das Passwort offline erraten"),
         L("<p>Sur sa propre carte graphique, l'attaquant essaie des mots de passe candidats : il dérive la clé, tente de déchiffrer le ticket et regarde si le résultat a la bonne structure. Pas de réseau, pas de limite d'essais, pas de verrouillage de compte.</p><p>La vitesse dépend du chiffrement du ticket : avec <strong>RC4</strong> (type <code>0x17</code>), la clé est un simple hachage du mot de passe et se teste par milliards par seconde. Avec <strong>AES</strong>, la dérivation itère 4 096 fois : environ mille fois plus lent.</p>",
           "<p>On their own graphics card, the attacker tries candidate passwords: derive the key, try to decrypt the ticket and check whether the result has the right structure. No network, no attempt limit, no account lockout.</p><p>The speed depends on the ticket's encryption: with <strong>RC4</strong> (type <code>0x17</code>), the key is a simple hash of the password and can be tested billions of times per second. With <strong>AES</strong>, the derivation iterates 4,096 times: roughly a thousand times slower.</p>",
           "<p>En su propia tarjeta gráfica, el atacante prueba contraseñas candidatas: deriva la clave, intenta descifrar el ticket y mira si el resultado tiene la estructura correcta. Sin red, sin límite de intentos, sin bloqueo de cuenta.</p><p>La velocidad depende del cifrado del ticket: con <strong>RC4</strong> (tipo <code>0x17</code>), la clave es un simple hash de la contraseña y se prueban miles de millones por segundo. Con <strong>AES</strong>, la derivación itera 4096 veces: unas mil veces más lento.</p>",
           "<p>Na sua própria placa gráfica, o atacante experimenta palavras-passe candidatas: deriva a chave, tenta decifrar o ticket e vê se o resultado tem a estrutura certa. Sem rede, sem limite de tentativas, sem bloqueio de conta.</p><p>A velocidade depende da cifra do ticket: com <strong>RC4</strong> (tipo <code>0x17</code>), a chave é um simples hash da palavra-passe e testam-se milhares de milhões por segundo. Com <strong>AES</strong>, a derivação itera 4096 vezes: cerca de mil vezes mais lento.</p>",
           "<p>Auf seiner eigenen Grafikkarte probiert der Angreifer Passwortkandidaten: Schlüssel ableiten, Entschlüsselung des Tickets versuchen, prüfen, ob das Ergebnis die richtige Struktur hat. Kein Netzwerk, keine Versuchsgrenze, keine Kontosperre.</p><p>Das Tempo hängt von der Verschlüsselung des Tickets ab: Bei <strong>RC4</strong> (Typ <code>0x17</code>) ist der Schlüssel ein einfacher Hash des Passworts und lässt sich milliardenfach pro Sekunde testen. Bei <strong>AES</strong> iteriert die Ableitung 4.096-mal: etwa tausendmal langsamer.</p>")),
        ("seq__note seq__note--alert n-1", ("🔓 mot de passe trouvé", "🔓 password found", "🔓 contraseña encontrada", "🔓 palavra-passe encontrada", "🔓 Passwort gefunden"), ("compte de service à privilèges", "privileged service account", "cuenta de servicio con privilegios", "conta de serviço com privilégios", "privilegiertes Dienstkonto"),
         ("7. Pourquoi c'est grave", "7. Why it matters", "7. Por qué es grave", "7. Porque é grave", "7. Warum das schlimm ist"),
         L("<p>Les comptes de service ont souvent un mot de passe ancien, jamais changé (« ça risque de casser l'appli »), et des droits élevés : administrateur local de nombreux serveurs, parfois membre des administrateurs du domaine. Un seul mot de passe faible peut ouvrir la voie à l'élévation de privilèges et au mouvement latéral.</p>",
           "<p>Service accounts often have an old password that never changes (“it might break the app”) and high privileges: local admin on many servers, sometimes a member of Domain Admins. A single weak password can open the way to privilege escalation and lateral movement.</p>",
           "<p>Las cuentas de servicio suelen tener una contraseña antigua que nunca se cambia («podría romper la aplicación») y privilegios altos: administrador local de muchos servidores, a veces miembro de los administradores del dominio. Una sola contraseña débil puede abrir la puerta a la escalada de privilegios y al movimiento lateral.</p>",
           "<p>As contas de serviço têm muitas vezes uma palavra-passe antiga, nunca mudada («pode partir a aplicação»), e privilégios elevados: administrador local de muitos servidores, por vezes membro dos administradores do domínio. Uma única palavra-passe fraca pode abrir caminho à elevação de privilégios e ao movimento lateral.</p>",
           "<p>Dienstkonten haben oft ein altes, nie geändertes Passwort („das könnte die Anwendung kaputt machen“) und hohe Rechte: lokaler Admin auf vielen Servern, manchmal Mitglied der Domänen-Admins. Ein einziges schwaches Passwort kann den Weg zu Rechteausweitung und Lateral Movement öffnen.</p>")),
        ("seq__note seq__note--ok n-2", ("🛡 événement 4769", "🛡 event 4769", "🛡 evento 4769", "🛡 evento 4769", "🛡 Ereignis 4769"), ("ce que voit le défenseur", "what the defender sees", "lo que ve el defensor", "o que vê o defensor", "was der Verteidiger sieht"),
         ("8. La détection", "8. Detection", "8. La detección", "8. A deteção", "8. Die Erkennung"),
         L("<p>Chaque demande de ticket génère l'événement Windows <strong>4769</strong> sur le contrôleur de domaine. Les signaux à surveiller :</p><ul><li>un type de chiffrement <code>0x17</code> (RC4) alors que le domaine utilise AES ;</li><li>un même compte qui demande des tickets pour beaucoup de SPN différents en peu de temps ;</li><li>une demande pour un <strong>SPN leurre</strong> : un faux compte de service que personne n'utilise, dont chaque ticket demandé déclenche une alerte.</li></ul>",
           "<p>Every ticket request generates Windows event <strong>4769</strong> on the domain controller. Signals to watch:</p><ul><li>an encryption type of <code>0x17</code> (RC4) while the domain uses AES;</li><li>one account requesting tickets for many different SPNs in a short time;</li><li>a request for a <strong>decoy SPN</strong>: a fake service account nobody uses, so any ticket requested for it raises an alert.</li></ul>",
           "<p>Cada petición de ticket genera el evento de Windows <strong>4769</strong> en el controlador de dominio. Señales que vigilar:</p><ul><li>un tipo de cifrado <code>0x17</code> (RC4) cuando el dominio usa AES;</li><li>una misma cuenta que pide tickets para muchos SPN distintos en poco tiempo;</li><li>una petición para un <strong>SPN señuelo</strong>: una cuenta de servicio falsa que nadie usa, de modo que cualquier ticket pedido genera una alerta.</li></ul>",
           "<p>Cada pedido de ticket gera o evento Windows <strong>4769</strong> no controlador de domínio. Sinais a vigiar:</p><ul><li>um tipo de cifra <code>0x17</code> (RC4) quando o domínio usa AES;</li><li>uma mesma conta a pedir tickets para muitos SPN diferentes em pouco tempo;</li><li>um pedido para um <strong>SPN isco</strong>: uma conta de serviço falsa que ninguém usa, pelo que qualquer ticket pedido gera um alerta.</li></ul>",
           "<p>Jede Ticket-Anfrage erzeugt auf dem Domänencontroller das Windows-Ereignis <strong>4769</strong>. Zu beobachtende Signale:</p><ul><li>Verschlüsselungstyp <code>0x17</code> (RC4), obwohl die Domäne AES nutzt;</li><li>ein Konto, das in kurzer Zeit Tickets für viele verschiedene SPNs anfordert;</li><li>eine Anfrage für einen <strong>Köder-SPN</strong>: ein falsches Dienstkonto, das niemand nutzt – jedes dafür angeforderte Ticket löst einen Alarm aus.</li></ul>")),
    ],
    keys=[(("gMSA", "gMSA", "gMSA", "gMSA", "gMSA"),
           ("Comptes de service gérés : mot de passe aléatoire de 120 caractères, renouvelé automatiquement. Le cassage devient impossible.", "Group managed service accounts: a random 120-character password, rotated automatically. Cracking becomes impossible.", "Cuentas de servicio administradas: contraseña aleatoria de 120 caracteres renovada automáticamente. El cracking se vuelve imposible.", "Contas de serviço geridas: palavra-passe aleatória de 120 caracteres, renovada automaticamente. O cracking torna-se impossível.", "Gruppenverwaltete Dienstkonten: zufälliges 120-Zeichen-Passwort, automatisch erneuert. Cracking wird unmöglich.")),
          (("Mots de passe longs", "Long passwords", "Contraseñas largas", "Palavras-passe longas", "Lange Passwörter"),
           ("Sinon, 25 caractères aléatoires minimum pour tout compte qui porte un SPN, et une rotation régulière.", "Otherwise, at least 25 random characters for any account with an SPN, and regular rotation.", "Si no, al menos 25 caracteres aleatorios para toda cuenta con SPN y rotación periódica.", "Caso contrário, pelo menos 25 caracteres aleatórios para qualquer conta com SPN e rotação regular.", "Sonst mindestens 25 zufällige Zeichen für jedes Konto mit SPN und regelmäßige Rotation.")),
          (("AES seulement", "AES only", "Solo AES", "Só AES", "Nur AES"),
           ("Désactiver RC4 sur les comptes et le domaine : chaque essai devient environ mille fois plus coûteux, et une demande RC4 devient suspecte.", "Disable RC4 on accounts and the domain: each guess becomes roughly a thousand times costlier, and any RC4 request becomes suspicious.", "Desactivar RC4 en las cuentas y el dominio: cada intento cuesta unas mil veces más y cualquier petición RC4 se vuelve sospechosa.", "Desativar RC4 nas contas e no domínio: cada tentativa fica cerca de mil vezes mais cara e qualquer pedido RC4 torna-se suspeito.", "RC4 für Konten und Domäne deaktivieren: Jeder Versuch wird etwa tausendmal teurer, und jede RC4-Anfrage wird verdächtig.")),
          (("Moindre privilège", "Least privilege", "Mínimo privilegio", "Menor privilégio", "Minimale Rechte"),
           ("Un compte de service n'a rien à faire dans les administrateurs du domaine. Surveiller 4769 et poser un SPN leurre.", "A service account has no business in Domain Admins. Monitor 4769 and set up a decoy SPN.", "Una cuenta de servicio no pinta nada en los administradores del dominio. Vigilar el 4769 y poner un SPN señuelo.", "Uma conta de serviço não tem nada que fazer nos administradores do domínio. Vigiar o 4769 e criar um SPN isco.", "Ein Dienstkonto hat in den Domänen-Admins nichts verloren. 4769 überwachen und einen Köder-SPN einrichten."))],
    pitch=("N'importe quel utilisateur du domaine peut demander au contrôleur de domaine un ticket pour un service, et ce ticket est chiffré avec une clé dérivée du mot de passe du compte de service. L'attaquant le récupère et devine le mot de passe hors ligne, sans bruit ni verrouillage. La parade : des gMSA ou des mots de passe très longs, AES au lieu de RC4, peu de privilèges, et une surveillance de l'événement 4769 avec un compte leurre.",
           "Any domain user can ask the domain controller for a service ticket, and that ticket is encrypted with a key derived from the service account's password. The attacker grabs it and guesses the password offline, with no noise and no lockout. The fix: gMSAs or very long passwords, AES instead of RC4, few privileges, and monitoring of event 4769 with a decoy account.",
           "Cualquier usuario del dominio puede pedir al controlador de dominio un ticket de servicio, y ese ticket va cifrado con una clave derivada de la contraseña de la cuenta de servicio. El atacante lo obtiene y adivina la contraseña sin conexión, sin ruido ni bloqueo. La defensa: gMSA o contraseñas muy largas, AES en lugar de RC4, pocos privilegios y vigilancia del evento 4769 con una cuenta señuelo.",
           "Qualquer utilizador do domínio pode pedir ao controlador de domínio um ticket de serviço, e esse ticket é cifrado com uma chave derivada da palavra-passe da conta de serviço. O atacante obtém-no e adivinha a palavra-passe offline, sem ruído nem bloqueio. A defesa: gMSA ou palavras-passe muito longas, AES em vez de RC4, poucos privilégios e vigilância do evento 4769 com uma conta isco.",
           "Jeder Domänenbenutzer kann beim Domänencontroller ein Service-Ticket anfordern, und dieses Ticket ist mit einem aus dem Passwort des Dienstkontos abgeleiteten Schlüssel verschlüsselt. Der Angreifer holt es sich und errät das Passwort offline, ohne Lärm und ohne Sperre. Die Abwehr: gMSAs oder sehr lange Passwörter, AES statt RC4, wenige Rechte und Überwachung von Ereignis 4769 mit einem Köderkonto."),
    refs=[("https://attack.mitre.org/techniques/T1558/003/", "MITRE ATT&amp;CK T1558.003",
           ("La fiche de la technique, avec détections et mitigations.", "The technique page, with detections and mitigations.", "La ficha de la técnica, con detecciones y mitigaciones.", "A ficha da técnica, com deteções e mitigações.", "Die Technikseite mit Erkennungen und Gegenmaßnahmen.")),
          ("https://www.thehacker.recipes/ad/movement/kerberos/kerberoast", "The Hacker Recipes",
           ("Le fonctionnement détaillé, côté attaque.", "The detailed mechanics, from the attack side.", "El funcionamiento detallado, desde el lado del ataque.", "O funcionamento detalhado, do lado do ataque.", "Die genaue Funktionsweise aus Angreifersicht.")),
          ("https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4769", "Microsoft · 4769",
           ("L'événement de demande de ticket et ses champs (type de chiffrement).", "The ticket request event and its fields (encryption type).", "El evento de petición de ticket y sus campos (tipo de cifrado).", "O evento de pedido de ticket e os seus campos (tipo de cifra).", "Das Ticket-Anfrage-Ereignis und seine Felder (Verschlüsselungstyp).")),
          ("https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview", "Microsoft · gMSA",
           ("Mettre en place des comptes de service gérés.", "Setting up group managed service accounts.", "Implantar cuentas de servicio administradas.", "Implementar contas de serviço geridas.", "Gruppenverwaltete Dienstkonten einrichten."))],
)

# ---------------------------------------------------------------- Injection SQL

SQLI = dict(
    slug="sql-injection", k="k-violet",
    title=("L'injection SQL et sa correction", "SQL injection and its fix", "La inyección SQL y su corrección", "A injeção SQL e a sua correção", "SQL-Injection und ihre Behebung"),
    meta="SQL injection explained with a live simulator: how string concatenation turns input into code, the classic login bypass, and why prepared statements fix it.",
    chips=[("Web", "Web", "Web", "Web", "Web"), "CWE-89", "OWASP A03"],
    lead=("L'une des failles web les plus anciennes, et toujours dans le Top 10 de l'OWASP. Son origine tient en une phrase : l'application construit sa requête en collant du texte, si bien que la base de données ne sait plus distinguer ce qu'a écrit le développeur de ce qu'a tapé l'utilisateur. Essaie toi-même dans le simulateur plus bas.",
          "One of the oldest web flaws, and still in the OWASP Top 10. Its root cause fits in one sentence: the application builds its query by gluing text together, so the database can no longer tell what the developer wrote from what the user typed. Try it yourself in the simulator below.",
          "Uno de los fallos web más antiguos y todavía en el Top 10 de OWASP. Su origen cabe en una frase: la aplicación construye la consulta pegando texto, de modo que la base de datos ya no distingue lo que escribió el desarrollador de lo que tecleó el usuario. Pruébalo tú mismo en el simulador de abajo.",
          "Uma das falhas web mais antigas, e ainda no Top 10 da OWASP. A sua origem cabe numa frase: a aplicação constrói a consulta colando texto, pelo que a base de dados deixa de distinguir o que o programador escreveu do que o utilizador digitou. Experimenta tu mesmo no simulador mais abaixo.",
          "Eine der ältesten Web-Schwachstellen und immer noch in den OWASP Top 10. Ihre Ursache passt in einen Satz: Die Anwendung baut ihre Abfrage durch Zusammenkleben von Text, sodass die Datenbank nicht mehr unterscheiden kann, was der Entwickler geschrieben und was der Benutzer eingetippt hat. Probier es unten im Simulator selbst aus."),
    n=3,
    actors=[(("Navigateur", "Browser", "Navegador", "Navegador", "Browser"), ("utilisateur", "user", "usuario", "utilizador", "Benutzer")),
            (("Application", "Application", "Aplicación", "Aplicação", "Anwendung"), ("code serveur", "server code", "código servidor", "código servidor", "Servercode")),
            (("Base de données", "Database", "Base de datos", "Base de dados", "Datenbank"), "SQL")],
    steps=[
        ("m-1-2", "POST /login", "username = admin' --",
         ("1. Le formulaire est envoyé", "1. The form is submitted", "1. Se envía el formulario", "1. O formulário é enviado", "1. Das Formular wird gesendet"),
         L("<p>L'utilisateur saisit un identifiant et un mot de passe. Ici, au lieu d'un nom, il tape <code>admin' --</code> et n'importe quoi comme mot de passe. Pour l'instant, ce n'est qu'une chaîne de caractères.</p>",
           "<p>The user enters a username and a password. Here, instead of a name, they type <code>admin' --</code> and anything as the password. For now, it is just a string.</p>",
           "<p>El usuario introduce un nombre y una contraseña. Aquí, en lugar de un nombre, escribe <code>admin' --</code> y cualquier cosa como contraseña. Por ahora, solo es una cadena de caracteres.</p>",
           "<p>O utilizador introduz um nome e uma palavra-passe. Aqui, em vez de um nome, escreve <code>admin' --</code> e qualquer coisa como palavra-passe. Por enquanto, é só uma cadeia de caracteres.</p>",
           "<p>Der Benutzer gibt Benutzernamen und Passwort ein. Hier tippt er statt eines Namens <code>admin' --</code> und irgendetwas als Passwort. Noch ist das nur eine Zeichenkette.</p>")),
        ("seq__note seq__note--alert n-2", ("⚠ concaténation", "⚠ concatenation", "⚠ concatenación", "⚠ concatenação", "⚠ Verkettung"), "\"…'\" + username + \"'…\"",
         ("2. La saisie devient du code", "2. Input turns into code", "2. La entrada se convierte en código", "2. A entrada torna-se código", "2. Die Eingabe wird zu Code"),
         L("<p>L'application fabrique la requête en <strong>collant</strong> la saisie au milieu du texte SQL. Le résultat est une seule chaîne envoyée à la base : elle n'a aucun moyen de savoir quelle partie vient du développeur et laquelle vient de l'utilisateur.</p>",
           "<p>The application builds the query by <strong>pasting</strong> the input into the middle of the SQL text. The result is a single string sent to the database: it has no way to know which part came from the developer and which from the user.</p>",
           "<p>La aplicación fabrica la consulta <strong>pegando</strong> la entrada en medio del texto SQL. El resultado es una sola cadena enviada a la base: no tiene forma de saber qué parte viene del desarrollador y cuál del usuario.</p>",
           "<p>A aplicação fabrica a consulta <strong>colando</strong> a entrada no meio do texto SQL. O resultado é uma única cadeia enviada à base: ela não tem forma de saber que parte vem do programador e que parte vem do utilizador.</p>",
           "<p>Die Anwendung baut die Abfrage, indem sie die Eingabe mitten in den SQL-Text <strong>klebt</strong>. Das Ergebnis ist eine einzige Zeichenkette an die Datenbank: Sie kann nicht wissen, welcher Teil vom Entwickler und welcher vom Benutzer stammt.</p>")),
        ("m-2-3 is-bad", "WHERE username = 'admin' -- …", ("vérification du mot de passe commentée", "password check commented out", "comprobación de contraseña comentada", "verificação da palavra-passe comentada", "Passwortprüfung auskommentiert"),
         ("3. La requête est détournée", "3. The query is hijacked", "3. La consulta queda desviada", "3. A consulta é desviada", "3. Die Abfrage wird umgelenkt"),
         L("<p>L'apostrophe tapée par l'utilisateur <strong>ferme la chaîne</strong> ouverte par le développeur, et <code>--</code> ouvre un commentaire SQL : tout ce qui suit, y compris <code>AND password = '…'</code>, est ignoré. La requête devient simplement « donne-moi l'utilisateur admin ».</p>",
           "<p>The quote typed by the user <strong>closes the string</strong> opened by the developer, and <code>--</code> starts an SQL comment: everything after it, including <code>AND password = '…'</code>, is ignored. The query simply becomes “give me the admin user”.</p>",
           "<p>El apóstrofo que escribe el usuario <strong>cierra la cadena</strong> abierta por el desarrollador, y <code>--</code> abre un comentario SQL: todo lo que sigue, incluido <code>AND password = '…'</code>, se ignora. La consulta se convierte simplemente en «dame el usuario admin».</p>",
           "<p>O apóstrofo escrito pelo utilizador <strong>fecha a cadeia</strong> aberta pelo programador, e <code>--</code> abre um comentário SQL: tudo o que vem depois, incluindo <code>AND password = '…'</code>, é ignorado. A consulta passa a ser simplesmente «dá-me o utilizador admin».</p>",
           "<p>Das vom Benutzer getippte Anführungszeichen <strong>schließt die Zeichenkette</strong>, die der Entwickler geöffnet hat, und <code>--</code> beginnt einen SQL-Kommentar: Alles danach, einschließlich <code>AND password = '…'</code>, wird ignoriert. Die Abfrage lautet nun einfach „gib mir den Benutzer admin“.</p>")),
        ("m-3-2", ("1 ligne : admin", "1 row: admin", "1 fila: admin", "1 linha: admin", "1 Zeile: admin"), ("la base obéit", "the database obeys", "la base obedece", "a base obedece", "die Datenbank gehorcht"),
         ("4. La base exécute fidèlement", "4. The database faithfully runs it", "4. La base la ejecuta fielmente", "4. A base executa fielmente", "4. Die Datenbank führt treu aus"),
         L("<p>La base de données n'a rien fait de mal : elle a exécuté une requête valide et renvoie la ligne du compte admin.</p>",
           "<p>The database did nothing wrong: it ran a valid query and returns the admin account's row.</p>",
           "<p>La base de datos no ha hecho nada malo: ha ejecutado una consulta válida y devuelve la fila de la cuenta admin.</p>",
           "<p>A base de dados não fez nada de errado: executou uma consulta válida e devolve a linha da conta admin.</p>",
           "<p>Die Datenbank hat nichts falsch gemacht: Sie hat eine gültige Abfrage ausgeführt und gibt die Zeile des Admin-Kontos zurück.</p>")),
        ("m-2-1 is-bad", ("Connecté : admin", "Logged in: admin", "Conectado: admin", "Ligado: admin", "Angemeldet: admin"), ("sans mot de passe", "without a password", "sin contraseña", "sem palavra-passe", "ohne Passwort"),
         ("5. L'impact", "5. The impact", "5. El impacto", "5. O impacto", "5. Die Auswirkung"),
         L("<p>L'application voit une ligne et en conclut que l'identifiant et le mot de passe étaient bons. Et le contournement de connexion n'est qu'un début : selon les droits du compte de base de données, une injection permet de lire toutes les tables, de modifier ou supprimer des données, parfois d'exécuter des commandes sur le serveur.</p>",
           "<p>The application sees a row and concludes that the username and password were right. And the login bypass is only the start: depending on the database account's rights, an injection can read every table, modify or delete data, sometimes run commands on the server.</p>",
           "<p>La aplicación ve una fila y concluye que el nombre y la contraseña eran correctos. Y saltarse el inicio de sesión es solo el principio: según los derechos de la cuenta de base de datos, una inyección permite leer todas las tablas, modificar o borrar datos y a veces ejecutar comandos en el servidor.</p>",
           "<p>A aplicação vê uma linha e conclui que o nome e a palavra-passe estavam certos. E contornar o login é só o começo: conforme os direitos da conta da base de dados, uma injeção permite ler todas as tabelas, alterar ou apagar dados e por vezes executar comandos no servidor.</p>",
           "<p>Die Anwendung sieht eine Zeile und folgert, dass Benutzername und Passwort stimmten. Und die Umgehung der Anmeldung ist nur der Anfang: Je nach Rechten des Datenbankkontos kann eine Injection alle Tabellen lesen, Daten ändern oder löschen, manchmal sogar Befehle auf dem Server ausführen.</p>")),
        ("seq__note seq__note--ok n-2-3", ("✔ requête préparée", "✔ prepared statement", "✔ consulta preparada", "✔ consulta preparada", "✔ Prepared Statement"), ("SQL et données envoyés séparément", "SQL and data sent separately", "SQL y datos enviados por separado", "SQL e dados enviados à parte", "SQL und Daten getrennt gesendet"),
         ("6. La correction", "6. The fix", "6. La corrección", "6. A correção", "6. Die Behebung"),
         L("<p>Avec une <strong>requête préparée</strong>, l'application envoie d'abord la structure de la requête avec des emplacements (<code>?</code>), puis les valeurs à part. La base analyse la requête <em>avant</em> de voir les données : <code>admin' --</code> n'est plus qu'un nom d'utilisateur bizarre, qui n'existe pas.</p><p>Ce n'est pas de l'échappement de caractères : c'est une séparation stricte entre le code et les données, ce qui rend l'injection impossible par construction.</p>",
           "<p>With a <strong>prepared statement</strong>, the application first sends the query's structure with placeholders (<code>?</code>), then the values separately. The database parses the query <em>before</em> seeing the data: <code>admin' --</code> is now just an odd username that doesn't exist.</p><p>This isn't character escaping: it is a strict separation between code and data, which makes injection impossible by design.</p>",
           "<p>Con una <strong>consulta preparada</strong>, la aplicación envía primero la estructura de la consulta con marcadores (<code>?</code>) y después los valores por separado. La base analiza la consulta <em>antes</em> de ver los datos: <code>admin' --</code> ya solo es un nombre de usuario raro que no existe.</p><p>No es escapar caracteres: es una separación estricta entre código y datos, que hace la inyección imposible por diseño.</p>",
           "<p>Com uma <strong>consulta preparada</strong>, a aplicação envia primeiro a estrutura da consulta com marcadores (<code>?</code>) e depois os valores à parte. A base analisa a consulta <em>antes</em> de ver os dados: <code>admin' --</code> passa a ser apenas um nome de utilizador estranho que não existe.</p><p>Não é escapar caracteres: é uma separação estrita entre código e dados, que torna a injeção impossível por construção.</p>",
           "<p>Mit einem <strong>Prepared Statement</strong> sendet die Anwendung zuerst die Struktur der Abfrage mit Platzhaltern (<code>?</code>), danach die Werte getrennt. Die Datenbank analysiert die Abfrage, <em>bevor</em> sie die Daten sieht: <code>admin' --</code> ist nur noch ein seltsamer Benutzername, den es nicht gibt.</p><p>Das ist kein Escapen von Zeichen, sondern eine strikte Trennung von Code und Daten – damit ist Injection konstruktionsbedingt unmöglich.</p>")),
    ],
    keys=[(("Requêtes préparées", "Prepared statements", "Consultas preparadas", "Consultas preparadas", "Prepared Statements"),
           ("Partout, sans exception, y compris les requêtes « brutes » écrites à côté d'un ORM.", "Everywhere, no exceptions, including “raw” queries written alongside an ORM.", "En todas partes, sin excepción, incluidas las consultas «en bruto» junto a un ORM.", "Em todo o lado, sem exceção, incluindo as consultas «em bruto» ao lado de um ORM.", "Überall, ohne Ausnahme, auch bei „rohen“ Abfragen neben einem ORM.")),
          (("Liste blanche", "Allow-list", "Lista blanca", "Lista branca", "Allow-List"),
           ("Un nom de table ou un sens de tri ne peut pas être un paramètre : on le choisit dans une liste de valeurs autorisées.", "A table name or sort order can't be a parameter: pick it from a list of allowed values.", "Un nombre de tabla o un orden no pueden ser parámetros: se eligen de una lista de valores permitidos.", "Um nome de tabela ou uma ordenação não podem ser parâmetros: escolhem-se de uma lista de valores autorizados.", "Ein Tabellenname oder eine Sortierrichtung kann kein Parameter sein: Man wählt ihn aus einer Liste erlaubter Werte.")),
          (("Moindre privilège", "Least privilege", "Mínimo privilegio", "Menor privilégio", "Minimale Rechte"),
           ("Le compte de base de l'application n'a que les droits nécessaires : pas d'administration, pas d'accès aux autres bases.", "The application's database account only has the rights it needs: no admin rights, no access to other databases.", "La cuenta de base de datos de la aplicación solo tiene los derechos necesarios: sin administración ni acceso a otras bases.", "A conta de base de dados da aplicação só tem os direitos necessários: sem administração nem acesso a outras bases.", "Das Datenbankkonto der Anwendung hat nur die nötigen Rechte: keine Administration, kein Zugriff auf andere Datenbanken.")),
          (("Défense en profondeur", "Defense in depth", "Defensa en profundidad", "Defesa em profundidade", "Defense in Depth"),
           ("Messages d'erreur génériques, mots de passe hachés (Argon2, bcrypt), WAF et validation en complément, jamais à la place.", "Generic error messages, hashed passwords (Argon2, bcrypt), WAF and validation as extras, never as a replacement.", "Mensajes de error genéricos, contraseñas con hash (Argon2, bcrypt), WAF y validación como complemento, nunca como sustituto.", "Mensagens de erro genéricas, palavras-passe com hash (Argon2, bcrypt), WAF e validação como complemento, nunca como substituto.", "Allgemeine Fehlermeldungen, gehashte Passwörter (Argon2, bcrypt), WAF und Validierung als Ergänzung, nie als Ersatz."))],
    pitch=("Une injection SQL arrive quand l'application construit sa requête en concaténant la saisie de l'utilisateur : une apostrophe suffit à sortir de la chaîne et à réécrire la logique, par exemple pour se connecter sans mot de passe. La correction est la requête préparée : la structure SQL et les valeurs sont envoyées séparément, donc la saisie reste une donnée. On y ajoute le moindre privilège, des erreurs génériques et des mots de passe hachés.",
           "SQL injection happens when the application builds its query by concatenating user input: a single quote is enough to break out of the string and rewrite the logic, for example to log in without a password. The fix is the prepared statement: SQL structure and values are sent separately, so input stays data. Add least privilege, generic errors and hashed passwords on top.",
           "Una inyección SQL ocurre cuando la aplicación construye la consulta concatenando la entrada del usuario: basta un apóstrofo para salir de la cadena y reescribir la lógica, por ejemplo para entrar sin contraseña. La corrección es la consulta preparada: la estructura SQL y los valores se envían por separado, así que la entrada sigue siendo un dato. Se añade mínimo privilegio, errores genéricos y contraseñas con hash.",
           "Uma injeção SQL acontece quando a aplicação constrói a consulta concatenando a entrada do utilizador: basta um apóstrofo para sair da cadeia e reescrever a lógica, por exemplo para entrar sem palavra-passe. A correção é a consulta preparada: a estrutura SQL e os valores são enviados à parte, por isso a entrada continua a ser um dado. Junta-se menor privilégio, erros genéricos e palavras-passe com hash.",
           "SQL-Injection entsteht, wenn die Anwendung ihre Abfrage durch Verketten der Benutzereingabe baut: Ein Anführungszeichen reicht, um aus der Zeichenkette auszubrechen und die Logik umzuschreiben, etwa um sich ohne Passwort anzumelden. Die Lösung ist das Prepared Statement: SQL-Struktur und Werte werden getrennt gesendet, die Eingabe bleibt also Daten. Dazu kommen minimale Rechte, allgemeine Fehlermeldungen und gehashte Passwörter."),
    refs=[("https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html", "OWASP Cheat Sheet",
           ("Les défenses recommandées, avec des exemples par langage.", "The recommended defenses, with examples per language.", "Las defensas recomendadas, con ejemplos por lenguaje.", "As defesas recomendadas, com exemplos por linguagem.", "Die empfohlenen Abwehrmaßnahmen mit Beispielen je Sprache.")),
          ("https://cwe.mitre.org/data/definitions/89.html", "CWE-89",
           ("La définition de la faiblesse et ses variantes.", "The weakness definition and its variants.", "La definición de la debilidad y sus variantes.", "A definição da fraqueza e as suas variantes.", "Die Definition der Schwäche und ihre Varianten."))],
)


# ---------------------------------------------------------------- blocs spécifiques

def sqlsim_block(k):
    ex = [("alice", "s3cret!", ("Connexion normale", "Normal login", "Acceso normal", "Login normal", "Normale Anmeldung")),
          ("alice", "1234", ("Mauvais mot de passe", "Wrong password", "Contraseña incorrecta", "Palavra-passe errada", "Falsches Passwort")),
          ("admin' -- ", "x", "admin' --"),
          ("' OR '1'='1' -- ", "x", "' OR '1'='1' --"),
          ("O'Brien", "x", ("Un nom avec apostrophe", "A name with a quote", "Un nombre con apóstrofo", "Um nome com apóstrofo", "Ein Name mit Apostroph"))]
    q = lambda v: v.replace("&", "&amp;").replace('"', "&quot;").replace("'", "&#39;")
    exb = "".join(f'<button type="button" data-example="{q(u)}" data-pass="{q(p)}">{t(lbl)}</button>' for u, p, lbl in ex)
    return f"""{h3(k, ("Essaie toi-même", "Try it yourself", "Pruébalo tú mismo", "Experimenta tu mesmo", "Probier es selbst"))}
<div class="x-panel sqlsim {k}" data-sqlsim data-reveal>
<p class="ex-nojs">{L("Le simulateur a besoin de JavaScript.", "The simulator needs JavaScript.", "El simulador necesita JavaScript.", "O simulador precisa de JavaScript.", "Der Simulator benötigt JavaScript.")}</p>
<div class="ex-needs-js">
<div class="ex-seg" role="group" aria-label="mode">
<button type="button" data-mode="vuln" aria-pressed="true">✗ {L("Code vulnérable (concaténation)", "Vulnerable code (concatenation)", "Código vulnerable (concatenación)", "Código vulnerável (concatenação)", "Verwundbarer Code (Verkettung)")}</button>
<button type="button" data-mode="params" aria-pressed="false">✔ {L("Code corrigé (requête préparée)", "Fixed code (prepared statement)", "Código corregido (consulta preparada)", "Código corrigido (consulta preparada)", "Behobener Code (Prepared Statement)")}</button>
</div>
<form class="sqlsim__form" autocomplete="off">
<label>{L("Nom d'utilisateur", "Username", "Usuario", "Utilizador", "Benutzername")}<input name="sim-user" value="alice" spellcheck="false" autocapitalize="off"></label>
<label>{L("Mot de passe", "Password", "Contraseña", "Palavra-passe", "Passwort")}<input name="sim-pass" value="s3cret!" spellcheck="false" autocapitalize="off"></label>
</form>
<div class="sqlsim__ex">{L("Exemples :", "Examples:", "Ejemplos:", "Exemplos:", "Beispiele:")} {exb}</div>
<div class="x-term"><div class="x-term__bar"><span>{L("requête envoyée à la base", "query sent to the database", "consulta enviada a la base", "consulta enviada à base", "an die Datenbank gesendete Abfrage")}</span></div>
<p class="sqlsim__query"></p><p class="sqlsim__params" hidden></p></div>
<div class="sqlsim__result" role="status" aria-live="polite"></div>
<p class="sqlsim__note" hidden></p>
<p class="sqlsim__legend"><span class="lg-code">{L("code SQL", "SQL code", "código SQL", "código SQL", "SQL-Code")}</span><span class="lg-data">{L("ta saisie (donnée)", "your input (data)", "tu entrada (dato)", "a tua entrada (dado)", "deine Eingabe (Daten)")}</span><span class="lg-inj">{L("ta saisie interprétée comme du code", "your input read as code", "tu entrada interpretada como código", "a tua entrada interpretada como código", "deine Eingabe als Code gelesen")}</span></p>
<p class="kcalc__fine">{L("Simulation entièrement locale dans ton navigateur, sur une table fictive <code>users</code> (admin, alice, bob). Seule une petite partie de SQL est simulée.",
  "Fully local simulation in your browser, on a fictional <code>users</code> table (admin, alice, bob). Only a small subset of SQL is simulated.",
  "Simulación totalmente local en tu navegador, sobre una tabla ficticia <code>users</code> (admin, alice, bob). Solo se simula una pequeña parte de SQL.",
  "Simulação totalmente local no teu navegador, sobre uma tabela fictícia <code>users</code> (admin, alice, bob). Só uma pequena parte de SQL é simulada.",
  "Vollständig lokale Simulation in deinem Browser auf einer fiktiven Tabelle <code>users</code> (admin, alice, bob). Nur ein kleiner Teil von SQL wird simuliert.")}</p>
</div>
</div>
{h3(k, ("Le code, avant et après", "The code, before and after", "El código, antes y después", "O código, antes e depois", "Der Code, vorher und nachher"))}
<div class="ex-compare" data-reveal>
<figure class="ex-code ex-code--bad"><figcaption class="ex-code__head">✗ {L("Vulnérable", "Vulnerable", "Vulnerable", "Vulnerável", "Verwundbar")}</figcaption><pre><code><span class="c-k">def</span> <span class="c-f">login</span>(username, password):
    query = (<span class="c-s">"SELECT * FROM users WHERE username = '"</span>
             <span class="c-bad">+ username +</span> <span class="c-s">"' AND password = '"</span>
             <span class="c-bad">+ password +</span> <span class="c-s">"'"</span>)
    row = db.execute(query).fetchone()
    <span class="c-k">return</span> row <span class="c-k">is not</span> <span class="c-k">None</span>
<span class="c-c"># {L("la saisie devient du SQL", "input becomes SQL", "la entrada se vuelve SQL", "a entrada torna-se SQL", "Eingabe wird zu SQL")}</span>
<span class="c-c"># {L("et le mot de passe est stocké en clair", "and the password is stored in plain text", "y la contraseña se guarda en claro", "e a palavra-passe é guardada em claro", "und das Passwort liegt im Klartext")}</span></code></pre></figure>
<figure class="ex-code ex-code--good"><figcaption class="ex-code__head">✔ {L("Corrigé", "Fixed", "Corregido", "Corrigido", "Behoben")}</figcaption><pre><code><span class="c-k">from</span> argon2 <span class="c-k">import</span> PasswordHasher
<span class="c-k">from</span> argon2.exceptions <span class="c-k">import</span> VerifyMismatchError
ph = PasswordHasher()

<span class="c-k">def</span> <span class="c-f">login</span>(username, password):
    row = db.execute(
        <span class="c-s">"SELECT password_hash FROM users WHERE username = <span class="c-good">?</span>"</span>,
        <span class="c-good">(username,)</span>,  <span class="c-c"># {L("donnée envoyée à part", "data sent separately", "dato enviado aparte", "dado enviado à parte", "Daten separat gesendet")}</span>
    ).fetchone()
    <span class="c-k">if</span> row <span class="c-k">is</span> <span class="c-k">None</span>:
        <span class="c-k">return</span> <span class="c-k">False</span>
    <span class="c-k">try</span>:
        <span class="c-k">return</span> ph.verify(row[<span class="c-n">0</span>], password)
    <span class="c-k">except</span> VerifyMismatchError:
        <span class="c-k">return</span> <span class="c-k">False</span></code></pre></figure>
</div>"""


def kcalc_block(k):
    sc = [("dict", ("Mot de passe « humain »", "“Human” password", "Contraseña «humana»", "Palavra-passe «humana»", "„Menschliches“ Passwort")),
          ("r8", ("8 caractères aléatoires", "8 random characters", "8 caracteres aleatorios", "8 caracteres aleatórios", "8 zufällige Zeichen")),
          ("r12", ("12 caractères aléatoires", "12 random characters", "12 caracteres aleatorios", "12 caracteres aleatórios", "12 zufällige Zeichen")),
          ("r25", ("25 caractères aléatoires", "25 random characters", "25 caracteres aleatorios", "25 caracteres aleatórios", "25 zufällige Zeichen")),
          ("gmsa", "gMSA")]
    scb = "".join(f'<button type="button" data-scenario="{v}" aria-pressed="{"true" if v == "dict" else "false"}">{t(lbl)}</button>' for v, lbl in sc)
    return f"""{h3(k, ("Combien de temps pour casser le ticket ?", "How long to crack the ticket?", "¿Cuánto se tarda en romper el ticket?", "Quanto tempo para quebrar o ticket?", "Wie lange dauert das Knacken des Tickets?"))}
<div class="x-panel kcalc {k}" data-kcalc data-level="bad" data-reveal>
<p class="ex-nojs">{L("Le calculateur a besoin de JavaScript.", "The calculator needs JavaScript.", "La calculadora necesita JavaScript.", "A calculadora precisa de JavaScript.", "Der Rechner benötigt JavaScript.")}</p>
<div class="ex-needs-js">
<p class="kcalc__label">{L("Mot de passe du compte de service", "Service account password", "Contraseña de la cuenta de servicio", "Palavra-passe da conta de serviço", "Passwort des Dienstkontos")}</p>
<div class="ex-seg" role="group">{scb}</div>
<p class="kcalc__label">{L("Chiffrement du ticket", "Ticket encryption", "Cifrado del ticket", "Cifra do ticket", "Verschlüsselung des Tickets")}</p>
<div class="ex-seg" role="group"><button type="button" data-enc="rc4" aria-pressed="true">RC4 (0x17)</button><button type="button" data-enc="aes" aria-pressed="false">AES-256 (0x12)</button></div>
<div class="kcalc__out" role="status" aria-live="polite">
<span class="kcalc__time"></span>
<div class="kcalc__bar" aria-hidden="true"><span></span></div>
<p class="kcalc__verdict"></p>
</div>
<p class="kcalc__fine">{L("Ordres de grandeur pour une carte graphique récente : environ un milliard d'essais par seconde en RC4, un million en AES ; temps moyen (la moitié des possibilités). Un mot de passe « humain » (du type <code>Printemps2024!</code>) se retrouve en général dans un gros dictionnaire combiné à des règles de transformation, soit de l'ordre de 10<sup>12</sup> candidats.",
  "Orders of magnitude for a recent graphics card: about a billion guesses per second with RC4, a million with AES; average time (half the possibilities). A “human” password (like <code>Summer2024!</code>) usually falls within a large wordlist combined with mangling rules, on the order of 10<sup>12</sup> candidates.",
  "Órdenes de magnitud para una tarjeta gráfica reciente: unos mil millones de intentos por segundo con RC4, un millón con AES; tiempo medio (la mitad de las posibilidades). Una contraseña «humana» (tipo <code>Verano2024!</code>) suele caer en un gran diccionario combinado con reglas de transformación, del orden de 10<sup>12</sup> candidatos.",
  "Ordens de grandeza para uma placa gráfica recente: cerca de mil milhões de tentativas por segundo em RC4, um milhão em AES; tempo médio (metade das possibilidades). Uma palavra-passe «humana» (tipo <code>Verao2024!</code>) costuma cair num grande dicionário combinado com regras de transformação, da ordem de 10<sup>12</sup> candidatos.",
  "Größenordnungen für eine aktuelle Grafikkarte: etwa eine Milliarde Versuche pro Sekunde bei RC4, eine Million bei AES; durchschnittliche Zeit (die Hälfte der Möglichkeiten). Ein „menschliches“ Passwort (etwa <code>Sommer2024!</code>) steckt meist in einer großen Wortliste mit Umformungsregeln, in der Größenordnung von 10<sup>12</sup> Kandidaten.")}</p>
</div>
</div>"""


# ---------------------------------------------------------------- pages

def page_body(p, extra):
    kick = " ".join([chip_dot(t(p["chips"][0]))] + [chip_plain(t(c)) for c in p["chips"][1:]])
    return f"""<p class="x-kicker {p['k']}">{kick}</p>
<p class="x-lead {p['k']}">{t(p['lead'])}</p>
{h3(p['k'], H_STEPS)}
{stepper(p['k'], p['n'], p['actors'], p['steps'])}
{extra}
{h3(p['k'], H_KEYS)}
{keys(p['k'], p['keys'])}
{h3(p['k'], H_PITCH)}
{pitch(p['k'], p['pitch'])}
{h3(p['k'], H_REFS)}
{refs(p['k'], p['refs'])}
{BACK}"""


def set_head(s, title5, desc, url, name_en):
    fr, en, es, pt, de = title5
    tt = lambda x: f"{x} :: Manthole — Blog"
    s = re.sub(r"<title[^>]*>.*?</title>",
               f'<title data-fr="{tt(fr)}" data-es="{tt(es)}" data-pt="{tt(pt)}" data-de="{tt(de)}">{tt(en)}</title>',
               s, count=1, flags=re.S)
    for attr in ['name="description"', 'itemprop="description"', 'name="twitter:description"', 'property="og:description"']:
        s = re.sub(rf'(<meta {attr} content=")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), s, count=1)
    for attr in ['itemprop="name"', 'name="twitter:title"', 'property="og:title"']:
        s = re.sub(rf'(<meta {attr} content=")[^"]*(")', lambda m: m.group(1) + name_en + m.group(2), s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*" />', f'<link rel="canonical" href="{url}" />', s, count=1)
    s = re.sub(r'<meta property="og:url" content="[^"]*" />', f'<meta property="og:url" content="{url}" />', s, count=1)
    return s


def build_page(tpl, p, extra):
    url = f"{SITE}/explain/{p['slug']}/"
    s = set_head(tpl, p["title"], p["meta"], url, p["title"][1])
    s = s.replace('<script src="/js/fx.js"></script>', '<script src="/js/fx.js"></script>\n<script src="/js/explain.js" defer></script>', 1)
    main_html = (f'<main class="post">\n        <article>\n'
                 f'            <h2 class="post-title"><a href="{url}">{t(p["title"])}</a></h2>\n'
                 f'            <div class="post-content">\n{page_body(p, extra)}\n            </div>\n'
                 f'        </article>\n    </main>')
    s = re.sub(r'<main class="post"[^>]*>.*?</main>', lambda m: main_html, s, count=1, flags=re.S)
    d = ROOT / "explain" / p["slug"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(s, encoding="utf-8")
    print(f"explain/{p['slug']}/index.html écrit")


EX5 = ("Exercices", "Exercises", "Ejercicios", "Exercícios", "Übungen")
CARDS = [
    (TLS, "🔐", ("Comment deux machines s'accordent sur une clé secrète en un aller-retour, et pourquoi l'homme du milieu échoue.",
                 "How two machines agree on a secret key in one round trip, and why a man in the middle fails.",
                 "Cómo dos máquinas acuerdan una clave secreta en un solo viaje y por qué falla el intermediario.",
                 "Como duas máquinas acordam uma chave secreta numa ida e volta e porque falha o intermediário.",
                 "Wie sich zwei Rechner in einem Roundtrip auf einen geheimen Schlüssel einigen und warum der Mittelsmann scheitert.")),
    (KERB, "🎟", ("Pourquoi un simple compte du domaine suffit à attaquer un compte de service, et comment le détecter.",
                  "Why a plain domain account is enough to attack a service account, and how to detect it.",
                  "Por qué basta una cuenta normal del dominio para atacar una cuenta de servicio y cómo detectarlo.",
                  "Porque basta uma conta simples do domínio para atacar uma conta de serviço e como o detetar.",
                  "Warum ein normales Domänenkonto reicht, um ein Dienstkonto anzugreifen, und wie man es erkennt.")),
    (SQLI, "💉", ("Un simulateur pour voir ta saisie devenir du code, puis la requête préparée qui corrige tout.",
                  "A simulator to watch your input turn into code, then the prepared statement that fixes it.",
                  "Un simulador para ver tu entrada convertirse en código y luego la consulta preparada que lo corrige.",
                  "Um simulador para ver a tua entrada tornar-se código e depois a consulta preparada que corrige tudo.",
                  "Ein Simulator, in dem deine Eingabe zu Code wird – und das Prepared Statement, das es behebt.")),
]


def build_hub():
    path = ROOT / "posts" / "index.html"
    s = path.read_text(encoding="utf-8")
    # liste des write-ups existants (reprise telle quelle depuis la page actuelle ou le bloc déjà généré)
    m = re.search(r'<li class="post-item">.*?</li>', s, flags=re.S)
    items = re.findall(r'<li class="post-item">.*?</li>', s, flags=re.S) or re.findall(r'<li data-reveal><a class="x-row" href="https://manthole.github.io/posts/.*?</li>', s, flags=re.S)
    rows = []
    for it in items:
        href = re.search(r'href="([^"]+)"', it).group(1)
        title = re.search(r'<span class="(?:post-title|x-row__title)">(.*?)</span>(?=\s*<span class="(?:post-day|x-row__date)")', it, flags=re.S).group(1)
        day = re.search(r'<span class="(?:post-day|x-row__date)">(.*?)</span>\s*</a>', it, flags=re.S).group(1)
        rows.append(f'<li data-reveal><a class="x-row" href="{href}"><span class="x-row__title">{title}</span> <span class="x-row__date">{day}</span></a></li>')
    assert rows, "aucun write-up trouvé"
    cards = []
    for p, icon, desc in CARDS:
        k = p["k"]
        cards.append(
            f'<li data-reveal><a class="x-card {k}" href="{SITE}/explain/{p["slug"]}/">'
            f'{chip_dot(L("Interactif", "Interactive", "Interactivo", "Interativo", "Interaktiv"))}'
            f'<span class="x-card__title">{icon} {t(p["title"])}</span><span class="x-card__desc">{t(desc)}</span>'
            f'<span class="x-card__foot"><span></span><span class="x-cta">{L("explorer ›", "explore ›", "explorar ›", "explorar ›", "erkunden ›")}</span></span></a></li>')
    body = f"""<p class="x-kicker k-gold">{chip_dot(L("Apprendre", "Learn", "Aprender", "Aprender", "Lernen"))} {chip_plain(L("Explications", "Explainers", "Explicaciones", "Explicações", "Erklärungen"))} {chip_plain("Write-ups")}</p>
<p class="x-lead k-gold">{L("Des concepts expliqués en profondeur, pas seulement des outils lancés : comprendre ce qui se passe sur le réseau et dans le code, et pourquoi la défense fonctionne.",
  "Concepts explained in depth, not just tools being run: understanding what happens on the wire and in the code, and why the defense works.",
  "Conceptos explicados en profundidad, no solo herramientas ejecutadas: entender lo que pasa en la red y en el código, y por qué funciona la defensa.",
  "Conceitos explicados em profundidade, não só ferramentas executadas: perceber o que acontece na rede e no código, e porque é que a defesa funciona.",
  "Konzepte in der Tiefe erklärt, nicht nur Tools gestartet: verstehen, was im Netz und im Code passiert und warum die Abwehr funktioniert.")}</p>
<h3 class="x-h k-gold">{L("Explications interactives", "Interactive explainers", "Explicaciones interactivas", "Explicações interativas", "Interaktive Erklärungen")}</h3>
<ul class="x-cards k-gold">{"".join(cards)}</ul>
<h3 class="x-h k-gold">{L("Write-ups et exercices", "Write-ups and exercises", "Write-ups y ejercicios", "Write-ups e exercícios", "Write-ups und Übungen")}</h3>
<ul class="x-rows k-gold">{"".join(rows)}</ul>"""
    url = f"{SITE}/posts/"
    s = set_head(s, EX5, "Exercises and interactive explainers: the TLS 1.3 handshake, Kerberoasting, SQL injection and its fix, plus cryptography write-ups.", url, "Exercises")
    main_html = (f'<main class="post">\n        <article>\n'
                 f'            <h2 class="post-title"><a href="{url}">{t(EX5)}</a></h2>\n'
                 f'            <div class="post-content">\n{body}\n            </div>\n'
                 f'        </article>\n    </main>')
    s = re.sub(r'<main class="(?:posts|post)"[^>]*>.*?</main>', lambda m: main_html, s, count=1, flags=re.S)
    path.write_text(s, encoding="utf-8")
    print("posts/index.html (hub Exercices) écrit")


OLD_MENU = L("Articles", "Posts", "Artículos", "Artigos", "Artikel")
OLD_DESC = L("Write-ups et exercices, comme mes exercices de cryptographie.", "Write-ups and exercises, such as my cryptography exercises.",
             "Write-ups y ejercicios, como mis ejercicios de criptografía.", "Write-ups e exercícios, como os meus exercícios de criptografia.",
             "Write-ups und Übungen, etwa meine Kryptografie-Übungen.")
NEW_DESC = L("Explications interactives (TLS, Kerberoasting, injection SQL) et write-ups.",
             "Interactive explainers (TLS, Kerberoasting, SQL injection) and write-ups.",
             "Explicaciones interactivas (TLS, Kerberoasting, inyección SQL) y write-ups.",
             "Explicações interativas (TLS, Kerberoasting, injeção SQL) e write-ups.",
             "Interaktive Erklärungen (TLS, Kerberoasting, SQL-Injection) und Write-ups.")


def rename_everywhere():
    n = 0
    for f in ROOT.rglob("*.html"):
        if any(part in (".git", "node_modules") for part in f.parts):
            continue
        s = f.read_text(encoding="utf-8")
        o = s.replace(OLD_MENU, L(*EX5)).replace(OLD_DESC, NEW_DESC)
        if o != s:
            f.write_text(o, encoding="utf-8")
            n += 1
    print(f"libellé « Exercices » appliqué dans {n} fichiers")


def sitemap():
    p = ROOT / "sitemap.xml"
    s = p.read_text(encoding="utf-8")
    add = ""
    for slug in ("tls", "kerberoasting", "sql-injection"):
        loc = f"{SITE}/explain/{slug}/"
        if loc not in s:
            add += f"  <url>\n    <loc>{loc}</loc>\n  </url>\n"
    if add:
        s = s.replace("</urlset>", add + "</urlset>")
        p.write_text(s, encoding="utf-8")
    print("sitemap.xml à jour")


def main():
    tpl = (ROOT / "about" / "index.html").read_text(encoding="utf-8")
    build_page(tpl, TLS, "")
    build_page(tpl, KERB, kcalc_block(KERB["k"]))
    build_page(tpl, SQLI, sqlsim_block(SQLI["k"]))
    build_hub()
    rename_everywhere()
    sitemap()


if __name__ == "__main__":
    main()
