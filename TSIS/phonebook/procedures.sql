-- TSIS 1 / 3.4 New Stored Procedures
-- Do not duplicate Practice 8 procedures here.

-- 1) Adds a new phone number to an existing contact.
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
AS $$
DECLARE
    v_contact_id INTEGER;
    v_type VARCHAR(10);
BEGIN
    v_type := LOWER(TRIM(p_type));

    IF v_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type: %. Allowed types: home, work, mobile', p_type;
    END IF;

    SELECT id
    INTO v_contact_id
    FROM contacts
    WHERE LOWER(name) = LOWER(p_contact_name)
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" does not exist', p_contact_name;
    END IF;

    INSERT INTO phones(contact_id, phone, type)
    VALUES (v_contact_id, p_phone, v_type)
    ON CONFLICT (contact_id, phone, type) DO NOTHING;

    -- Keep old contacts.phone column compatible.
    IF v_type = 'mobile' THEN
        UPDATE contacts
        SET phone = p_phone
        WHERE id = v_contact_id;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- 2) Moves a contact to another group.
-- If the group does not exist, it creates it.
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id INTEGER;
    v_group_name VARCHAR(50);
BEGIN
    v_group_name := TRIM(p_group_name);

    IF v_group_name = '' THEN
        RAISE EXCEPTION 'Group name cannot be empty';
    END IF;

    SELECT id
    INTO v_contact_id
    FROM contacts
    WHERE LOWER(name) = LOWER(p_contact_name)
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" does not exist', p_contact_name;
    END IF;

    INSERT INTO groups(name)
    VALUES (v_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id
    INTO v_group_id
    FROM groups
    WHERE LOWER(name) = LOWER(v_group_name)
    LIMIT 1;

    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = v_contact_id;
END;
$$ LANGUAGE plpgsql;