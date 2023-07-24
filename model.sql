CREATE TABLE IF NOT EXISTS names
(
	id INT NOT NULL PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	nickname VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS public.relations
(
    id_person integer NOT NULL UNIQUE,
    id_father integer,
    id_mother integer,
	FOREIGN KEY(id_person) REFERENCES names(id) ON DELETE CASCADE,
	FOREIGN KEY(id_father) REFERENCES names(id) ON DELETE CASCADE,
	FOREIGN KEY(id_mother) REFERENCES names(id) ON DELETE CASCADE
);

SELECT * 
FROM NAMES;

SELECT *
FROM relations;