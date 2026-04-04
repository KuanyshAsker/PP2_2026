CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT) 
RETURNS TABLE(id INT, name TEXT, phone TEXT)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.phone
    FROM contacts c
    WHERE c.name ILIKE '%' || pattern || '%'
       OR c.phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql; -- search by pattern 


CREATE OR REPLACE FUNCTION get_contacts_paginated(limit_val INT, offset_val INT) 
RETURNS TABLE(id INT, name TEXT, phone TEXT)
AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM contacts
    LIMIT limit_val OFFSET offset_val;
END;
$$ LANGUAGE plpgsql; -- pagination which is limited chunks of rows 