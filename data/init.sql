-- Create tables that represent the chat conversion graph
CREATE TABLE IF NOT EXISTS chat_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    message TEXT,
    input BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS chat_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_id INT NOT NULL,
    to_id INT NOT NULL,
    FOREIGN KEY (from_id) REFERENCES chat_nodes(id),
    FOREIGN KEY (to_id) REFERENCES chat_nodes(id)
);

INSERT INTO chat_nodes (id, name, message, input) VALUES
    (1, 'start', 'Hallo. Ich bin der Support-Chatbot der XY Ltd. Bist du ein privater oder ein business Kunde?', false),
        (11, 'private', 'Privater Kunde', true),
        (12, 'business', 'Business Kunde', true),
    (2, 'produkt', 'Um welches Produkt geht es?', false),
        (21, 'cleanbug', 'Cleanbug', true),
        (22, 'windowfly', 'Windowfly', true),
        (23, 'gardenbeetle', 'Gardenbeetle', true),
        (24, 'sonstiges_produkt', 'Sonstiges', true),
    (3, 'problem', 'Was ist das Problem?', false),
        (31, 'problem_cleanbug_1', 'Cleanbug geht nicht an', true),
            (311, 'loesung_cleanbug_1', 'Der Cleanbug ist möglicherweise nicht aufgeladen. Bitte stelle sicher, dass er korrekt mit dem Ladegerät verbunden ist.', false),
        (32, 'problem_cleanbug_2', 'Cleanbug fällt herunter', true),
            (321, 'loesung_cleanbug_2', 'Bitte überprüfe, ob der Cleanbug auf einer geeigneten Oberfläche verwendet wird. Möglicherweise ist die Haftung auf glatten Flächen nicht ausreichend.', false),
        (33, 'problem_windowfly_1', 'Windowfly saugt sich fest', true),
            (331, 'loesung_windowfly_1', 'Der Windowfly besitzt starke Saugnäpfe. Entferne ihn vorsichtig durch Drehen, nicht Ziehen.', false),
        (34, 'problem_windowfly_2', 'Windowfly hält nicht', true),
            (341, 'loesung_windowfly_2', 'Bitte reinige die Saugnäpfe und die Oberfläche gründlich. Rückstände können die Haftung beeinträchtigen.', false),
        (35, 'problem_gardenbeetle_1', 'Gardenbeetle erkennt kein Unkraut', true),
            (351, 'loesung_gardenbeetle_1', 'Stelle sicher, dass die Kamera des Gardenbeetle sauber ist und ausreichende Lichtverhältnisse herrschen.', false),
        (36, 'problem_gardenbeetle_2', 'Gardenbeetle macht laute Geräusche', true),
            (361, 'loesung_gardenbeetle_2', 'Möglicherweise sind Fremdkörper im Gehäuse. Bitte überprüfe das Gerät und entferne mögliche Blockaden.', false),
        (37, 'problem_sonstiges', 'Sonstiges', true),
            (371, 'loesung_sonstiges', 'Danke für deine Nachricht. Ich werde ein Ticket für dich eröffnen.', false),
    (4, 'konnte_helfen', 'Konnte ich dir damit weiterhelfen?', false),
        (41, 'ja', 'Ja', true),
        (42, 'nein', 'Nein', true),
            (421, 'ticket_eroeffnen', 'Ich werde ein Ticket für dich eröffnen. Bitte nenne mir deine E-Mail-Adresse.', false),
                (4211, 'ticket_eroeffnen_email', 'E-Mail-Adresse', true),
                    (42111, 'ticket_eroeffnen_email_gesendet', 'Das Ticket wurde eröffnet. Du solltest in Kürze eine E-Mail erhalten. Deine Ticket-Nummer ist: {ticket_number}', false),
    (5, 'ende', 'Einen schönen Tag dir noch!', false);

INSERT INTO chat_edges (from_id, to_id) VALUES
    -- Start-Auswahl: Kunde
    (1, 11),  -- privater Kunde
    (1, 12),  -- Business Kunde

    -- Produkt-Auswahl
    (11, 2),
    (12, 2),
    (2, 21),  -- Cleanbug
    (2, 22),  -- Windowfly
    (2, 23),  -- Gardenbeetle
    (2, 24),  -- Sonstiges Produkt

    -- Problem-Auswahl nach Produkt
    (21, 3),
    (22, 3),
    (23, 3),
    (24, 3),

    -- Cleanbug Probleme
    (3, 31),
    (3, 32),
    -- Lösungen Cleanbug
    (31, 311),
    (32, 321),

    -- Windowfly Probleme
    (3, 33),
    (3, 34),
    -- Lösungen Windowfly
    (33, 331),
    (34, 341),

    -- Gardenbeetle Probleme
    (3, 35),
    (3, 36),
    -- Lösungen Gardenbeetle
    (35, 351),
    (36, 361),

    -- Sonstiges Problem → direkt zur Ticket-Eröffnung
    (3, 37),
    (37, 421),

    -- Nach jeder Lösung zur Rückfrage
    (311, 4),
    (321, 4),
    (331, 4),
    (341, 4),
    (351, 4),
    (361, 4),

    -- Ja/Nein-Reaktion auf "Konnte helfen?"
    (4, 41),  -- Ja → Ende
    (4, 42),  -- Nein → Ticket eröffnen

    -- Ticket-Eröffnung
    (42, 421),
    (421, 4211),
    (4211, 42111),

    -- Abschließend: Ende
    (41, 5),
    (42111, 5);
