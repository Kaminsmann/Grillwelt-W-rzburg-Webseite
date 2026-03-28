<?php
/**
 * Feuerhaus Kalina – Grillwelt
 * Kontaktformular Mailer
 * Sicher, validiert, DSGVO-konform
 */

// Nur POST-Anfragen erlaubt
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    exit('Method Not Allowed');
}

// JSON-Response Helper
function respond(bool $success, string $message): void {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['success' => $success, 'message' => $message]);
    exit;
}

// Rate-Limiting (einfach via Session)
session_start();
$now = time();
if (!isset($_SESSION['last_submit'])) {
    $_SESSION['last_submit'] = 0;
    $_SESSION['submit_count'] = 0;
}

// Max 3 Anfragen pro 10 Minuten
if ($now - $_SESSION['last_submit'] < 600) {
    $_SESSION['submit_count']++;
    if ($_SESSION['submit_count'] > 3) {
        respond(false, 'Zu viele Anfragen. Bitte warten Sie einige Minuten oder rufen Sie uns direkt an.');
    }
} else {
    $_SESSION['submit_count'] = 1;
    $_SESSION['last_submit'] = $now;
}

// DSGVO-Zustimmung prüfen
if (empty($_POST['dsgvo'])) {
    respond(false, 'Bitte stimmen Sie der Datenschutzerklärung zu.');
}

// Felder holen & bereinigen
function clean(string $input): string {
    return htmlspecialchars(strip_tags(trim($input)), ENT_QUOTES, 'UTF-8');
}

$name    = clean($_POST['name']    ?? '');
$email   = clean($_POST['email']   ?? '');
$phone   = clean($_POST['phone']   ?? '');
$thema   = clean($_POST['thema']   ?? '');
$message = clean($_POST['message'] ?? '');

// Validierung
if (strlen($name) < 2) {
    respond(false, 'Bitte geben Sie Ihren Namen ein.');
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    respond(false, 'Bitte geben Sie eine gültige E-Mail-Adresse ein.');
}
if (strlen($message) < 10) {
    respond(false, 'Bitte schreiben Sie eine kurze Nachricht.');
}

// Honeypot: verstecktes Feld – wenn gefüllt, ist es ein Bot
if (!empty($_POST['website'])) {
    // Stille Ablehnung – kein Fehler für den Bot
    respond(true, 'Vielen Dank für Ihre Nachricht.');
}

// Header-Injection verhindern
if (preg_match('/[\r\n]/', $name . $email . $thema)) {
    respond(false, 'Ungültige Eingabe erkannt.');
}

// E-Mail konfigurieren
$to      = 'info@feuerhaus-kalina.de';
$subject = '=?UTF-8?B?' . base64_encode('Neue Beratungsanfrage: ' . $thema) . '?=';

$thema_label = $thema ?: 'Allgemeine Anfrage';

$body = "Neue Kontaktanfrage über grills.feuerhaus-kalina.de\n";
$body .= str_repeat('=', 50) . "\n\n";
$body .= "Name:     " . $name . "\n";
$body .= "E-Mail:   " . $email . "\n";
if ($phone) {
    $body .= "Telefon:  " . $phone . "\n";
}
$body .= "Thema:    " . $thema_label . "\n";
$body .= "\nNachricht:\n" . str_repeat('-', 30) . "\n";
$body .= wordwrap($message, 70, "\n") . "\n\n";
$body .= str_repeat('=', 50) . "\n";
$body .= "Gesendet am: " . date('d.m.Y \u\m H:i \U\h\r') . "\n";
$body .= "IP: " . $_SERVER['REMOTE_ADDR'] . "\n";

$headers  = "From: Grillwelt Feuerhaus Kalina <noreply@feuerhaus-kalina.de>\r\n";
$headers .= "Reply-To: " . $name . " <" . $email . ">\r\n";
$headers .= "X-Mailer: PHP/" . phpversion() . "\r\n";
$headers .= "MIME-Version: 1.0\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$headers .= "Content-Transfer-Encoding: 8bit\r\n";

// Senden
$sent = mail($to, $subject, $body, $headers);

if ($sent) {
    // Auto-Antwort an Kunden
    $auto_subject = '=?UTF-8?B?' . base64_encode('Ihre Anfrage bei Feuerhaus Kalina – Grillwelt') . '?=';
    $auto_body  = "Hallo " . $name . ",\n\n";
    $auto_body .= "vielen Dank für Ihre Nachricht!\n\n";
    $auto_body .= "Wir haben Ihre Anfrage erhalten und melden uns schnellstmöglich bei Ihnen.\n\n";
    $auto_body .= "-------------------------------\n";
    $auto_body .= "Ihre Nachricht zum Thema: " . $thema_label . "\n";
    $auto_body .= wordwrap($message, 70, "\n") . "\n";
    $auto_body .= "-------------------------------\n\n";
    $auto_body .= "Mit freundlichen Grüßen\n";
    $auto_body .= "Feuerhaus Kalina – Grillwelt\n";
    $auto_body .= "Maidbronner Straße 3, 97222 Rimpar\n";
    $auto_body .= "Tel: 09365 / 888 42 18\n";
    $auto_body .= "info@feuerhaus-kalina.de\n";
    $auto_body .= "grills.feuerhaus-kalina.de\n\n";
    $auto_body .= "Öffnungszeiten: Mi–Fr 12–18:30 Uhr | Sa 10–14 Uhr\n";

    $auto_headers  = "From: Feuerhaus Kalina Grillwelt <info@feuerhaus-kalina.de>\r\n";
    $auto_headers .= "MIME-Version: 1.0\r\n";
    $auto_headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
    $auto_headers .= "Content-Transfer-Encoding: 8bit\r\n";

    mail($email, $auto_subject, $auto_body, $auto_headers);

    respond(true, 'Vielen Dank! Ihre Nachricht wurde gesendet. Wir melden uns schnellstmöglich bei Ihnen.');
} else {
    respond(false, 'Leider konnte Ihre Nachricht nicht gesendet werden. Bitte rufen Sie uns direkt an: 09365 / 888 42 18');
}
