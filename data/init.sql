-- Create tables that represent the chat conversion graph
CREATE TABLE IF NOT EXISTS chat_nodes (
    name VARCHAR(255) PRIMARY KEY NOT NULL,
    content TEXT,
    type VARCHAR(1) DEFAULT "o"
);

CREATE TABLE IF NOT EXISTS chat_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_name VARCHAR(255) NOT NULL,
    to_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (from_name) REFERENCES chat_nodes(name),
    FOREIGN KEY (to_name) REFERENCES chat_nodes(name)
);

INSERT INTO chat_nodes (name, content, type) VALUES
    -- Begrüßung
    ('start', 'Hallo. Ich bin der Support-Chatbot der Bugland Ltd. Bist du ein privater oder ein business Kunde?', 'o'),

    -- Auswahl Kunde
    ('private', 'privat;privater;ich bin privat', 'c'),
    ('business', 'business;firma;gewerbe', 'c'),

    -- Produktabfrage
    ('produkt', 'Um welches Produkt geht es?', 'o'),

    -- Produktauswahl
    ('cleanbug', 'cleanbug;roboter;reinigungsroboter', 'c'),
    ('windowfly', 'windowfly;fensterroboter', 'c'),
    ('gardenbeetle', 'gardenbeetle;gartenroboter;unkraut', 'c'),
    ('sonstiges_produkt', 'sonstiges;anderes', 'c'),

    -- Problemabfrage
    ('problem', 'Was ist das Problem?', 'o'),

    -- Cleanbug Probleme
    ('problem_cleanbug_1', 'geht nicht an;startet nicht;kein strom', 'c'),
    ('loesung_cleanbug_1', 'Der Cleanbug ist möglicherweise nicht aufgeladen. Bitte stelle sicher, dass er korrekt mit dem Ladegerät verbunden ist.', 'o'),

    ('problem_cleanbug_2', 'fällt herunter;runtergefallen;stürzt ab', 'c'),
    ('loesung_cleanbug_2', 'Bitte überprüfe, ob der Cleanbug auf einer geeigneten Oberfläche verwendet wird. Möglicherweise ist die Haftung auf glatten Flächen nicht ausreichend.', 'o'),

    -- Windowfly Probleme
    ('problem_windowfly_1', 'saugt sich fest;geht nicht mehr ab;festsaugen', 'c'),
    ('loesung_windowfly_1', 'Der Windowfly besitzt starke Saugnäpfe. Entferne ihn vorsichtig durch Drehen, nicht Ziehen.', 'o'),

    ('problem_windowfly_2', 'hält nicht;haftet nicht;fällt ab', 'c'),
    ('loesung_windowfly_2', 'Bitte reinige die Saugnäpfe und die Oberfläche gründlich. Rückstände können die Haftung beeinträchtigen.', 'o'),

    -- Gardenbeetle Probleme
    ('problem_gardenbeetle_1', 'erkennt kein unkraut;unkraut wird ignoriert', 'c'),
    ('loesung_gardenbeetle_1', 'Stelle sicher, dass die Kamera des Gardenbeetle sauber ist und ausreichende Lichtverhältnisse herrschen.', 'o'),

    ('problem_gardenbeetle_2', 'macht laute geräusche;laut;knackt', 'c'),
    ('loesung_gardenbeetle_2', 'Möglicherweise sind Fremdkörper im Gehäuse. Bitte überprüfe das Gerät und entferne mögliche Blockaden.', 'o'),

    -- Sonstiges Problem
    ('problem_sonstiges', 'sonstiges;anderes problem', 'c'),

    -- Rückfrage hilfreich
    ('konnte_helfen', 'Konnte ich dir damit weiterhelfen?', 'o'),
    ('ja', 'ja;hat geholfen', 'c'),
    ('nein', 'nein;nicht geholfen', 'c'),

    -- Ticket-Eröffnung
    ('ticket_eroeffnen', 'Ich werde ein Ticket für dich eröffnen. Bitte nenne mir deine E-Mail-Adresse.', 'o'),
    ('ticket_eroeffnen_email', 'E-Mail-Adresse', 'i'),
    ('ticket_eroeffnen_email_gesendet', 'Das Ticket wurde eröffnet. Du solltest in Kürze eine E-Mail erhalten. Deine Ticket-Nummer ist: {ticket_number}', 'o'),

    -- Ende
    ('ende', 'Einen schönen Tag dir noch!', 'o');

INSERT INTO chat_edges (from_name, to_name) VALUES
    -- Start-Auswahl: Kunde
    ('start', 'private'),
    ('start', 'business'),

    -- Produkt-Auswahl
    ('private', 'produkt'),
    ('business', 'produkt'),
    ('produkt', 'cleanbug'),
    ('produkt', 'windowfly'),
    ('produkt', 'gardenbeetle'),
    ('produkt', 'sonstiges_produkt'),

    -- Problem-Auswahl nach Produkt
    ('cleanbug', 'problem'),
    ('windowfly', 'problem'),
    ('gardenbeetle', 'problem'),
    ('sonstiges_produkt', 'problem'),

    -- Cleanbug Probleme
    ('problem', 'problem_cleanbug_1'),
    ('problem', 'problem_cleanbug_2'),
    ('problem_cleanbug_1', 'loesung_cleanbug_1'),
    ('problem_cleanbug_2', 'loesung_cleanbug_2'),

    -- Windowfly Probleme
    ('problem', 'problem_windowfly_1'),
    ('problem', 'problem_windowfly_2'),
    ('problem_windowfly_1', 'loesung_windowfly_1'),
    ('problem_windowfly_2', 'loesung_windowfly_2'),

    -- Gardenbeetle Probleme
    ('problem', 'problem_gardenbeetle_1'),
    ('problem', 'problem_gardenbeetle_2'),
    ('problem_gardenbeetle_1', 'loesung_gardenbeetle_1'),
    ('problem_gardenbeetle_2', 'loesung_gardenbeetle_2'),

    -- Sonstiges Problem → direkt zur Ticket-Eröffnung
    ('problem', 'problem_sonstiges'),
    ('problem_sonstiges', 'loesung_sonstiges'),

    -- Nach jeder Lösung zur Rückfrage
    ('loesung_cleanbug_1', 'konnte_helfen'),
    ('loesung_cleanbug_2', 'konnte_helfen'),
    ('loesung_windowfly_1', 'konnte_helfen'),
    ('loesung_windowfly_2', 'konnte_helfen'),
    ('loesung_gardenbeetle_1', 'konnte_helfen'),
    ('loesung_gardenbeetle_2', 'konnte_helfen'),

    -- Ja/Nein-Reaktion auf "Konnte helfen?"
    ('konnte_helfen', 'ja'),
    ('konnte_helfen', 'nein'),

    -- Ticket-Eröffnung
    ('nein', 'ticket_eroeffnen'),
    ('ticket_eroeffnen', 'ticket_eroeffnen_email'),
    ('ticket_eroeffnen_email', 'ticket_eroeffnen_email_gesendet'),

    -- Abschließend: Ende
    ('ja', 'ende'),
    ('ticket_eroeffnen_email_gesendet', 'ende');
