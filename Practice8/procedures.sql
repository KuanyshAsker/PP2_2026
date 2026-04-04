CREATE OR REPLACE PROCEDURE insert_or_update_user(p_name TEXT, p_phone TEXT) 
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts
        SET phone = p_phone
        WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$ LANGUAGE plpgsql; -- insert or update user


CREATE OR REPLACE PROCEDURE delete_user(p_value TEXT)
AS $$
BEGIN
    DELETE FROM contacts
    WHERE name = p_value OR phone = p_value;
END;
$$ LANGUAGE plpgsql; -- delete user 


CREATE OR REPLACE FUNCTION insert_many(names TEXT[], phones TEXT[])
RETURNS TABLE(name TEXT, phone TEXT)
AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..array_length(names, 1)
    LOOP
        IF phones[i] ~ '^[0-9]+$' THEN
            INSERT INTO contacts(name, phone)
            VALUES (names[i], phones[i]);
        ELSE
            RETURN QUERY SELECT names[i], phones[i];
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql; -- insert multiple users 