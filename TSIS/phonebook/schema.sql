-- TSIS 1 / 3.1 Extended Contact Model
-- Migration-compatible version for your Practice 7-8 PhoneBook project.
-- It keeps the old contacts.phone column so your current code, functions.sql,
-- and procedures.sql do not break yet. The new normalized phones table is added
-- and existing contacts.phone values are copied into it as mobile numbers.

-- 1) Groups table
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO groups (name)
VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

-- 2) Contacts table
-- The phone column is intentionally kept as a legacy column for now.
-- Later, after we update all functions/procedures to use phones, we can remove it.
CREATE TABLE IF NOT EXISTS contacts (
    id    SERIAL PRIMARY KEY,
    name  TEXT,
    phone TEXT
);

ALTER TABLE contacts
    ADD COLUMN IF NOT EXISTS email      VARCHAR(100),
    ADD COLUMN IF NOT EXISTS birthday   DATE,
    ADD COLUMN IF NOT EXISTS group_id   INTEGER,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

UPDATE contacts
SET created_at = CURRENT_TIMESTAMP
WHERE created_at IS NULL;

-- Add FK separately so this file works even when contacts already existed before.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'contacts_group_id_fkey'
    ) THEN
        ALTER TABLE contacts
        ADD CONSTRAINT contacts_group_id_fkey
        FOREIGN KEY (group_id) REFERENCES groups(id);
    END IF;
END;
$$;

-- Put existing contacts into the default group if no group was assigned yet.
UPDATE contacts
SET group_id = (SELECT id FROM groups WHERE name = 'Other')
WHERE group_id IS NULL;

-- 3) Phones table: one contact can have many phone numbers.
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) NOT NULL DEFAULT 'mobile'
               CHECK (type IN ('home', 'work', 'mobile'))
);

-- Prevent duplicated phone rows when schema.sql is run multiple times.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'phones_contact_phone_type_unique'
    ) THEN
        ALTER TABLE phones
        ADD CONSTRAINT phones_contact_phone_type_unique
        UNIQUE (contact_id, phone, type);
    END IF;
END;
$$;

-- Helpful indexes for joins/searches.
CREATE INDEX IF NOT EXISTS idx_contacts_group_id ON contacts(group_id);
CREATE INDEX IF NOT EXISTS idx_phones_contact_id ON phones(contact_id);
CREATE INDEX IF NOT EXISTS idx_phones_phone ON phones(phone);

-- 4) Data migration from the old model to the new model.
-- Existing contacts.phone values become mobile numbers in phones.
INSERT INTO phones (contact_id, phone, type)
SELECT id, phone, 'mobile'
FROM contacts
WHERE phone IS NOT NULL
  AND BTRIM(phone) <> ''
ON CONFLICT (contact_id, phone, type) DO NOTHING;
