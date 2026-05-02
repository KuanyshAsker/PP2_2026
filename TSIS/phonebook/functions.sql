-- TSIS 1 / 3.4 Extended search function
-- Searches by name, legacy phone, email, and all phones in phones table.

DROP FUNCTION IF EXISTS search_contacts(TEXT);

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    id INTEGER,
    name TEXT,
    email VARCHAR(100),
    birthday DATE,
    group_name VARCHAR(50),
    phones TEXT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name AS group_name,
        COALESCE(
            string_agg(
                ph.type || ': ' || ph.phone,
                ', '
                ORDER BY
                    CASE ph.type
                        WHEN 'mobile' THEN 1
                        WHEN 'home' THEN 2
                        WHEN 'work' THEN 3
                        ELSE 4
                    END
            ),
            '-'
        ) AS phones
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones ph ON ph.contact_id = c.id
    WHERE
        c.name ILIKE '%' || p_query || '%'
        OR c.phone ILIKE '%' || p_query || '%'
        OR c.email ILIKE '%' || p_query || '%'
        OR EXISTS (
            SELECT 1
            FROM phones ph2
            WHERE ph2.contact_id = c.id
              AND ph2.phone ILIKE '%' || p_query || '%'
        )
    GROUP BY c.id, c.name, c.email, c.birthday, g.name
    ORDER BY c.id;
END;
$$ LANGUAGE plpgsql;