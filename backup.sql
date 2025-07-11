PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE usuario (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    cuenta_activada BOOLEAN DEFAULT 0,
    codigo_unico TEXT
);
INSERT INTO usuario VALUES(1,'contacto.rockdata@gmail.com','scrypt:32768:8:1$mmCvC64wZQgs7Rul$2329689e5864dafdba3ef11434ce3d297820b6a963391d91fcf40ae8a3f013bf41a1ff24e460411cd4dd5912559a840f077fc53ee43277e9d20c202a9856104a',1,'1941-2001-3690');
CREATE TABLE codigo_acceso (
    id INTEGER PRIMARY KEY,
    codigo TEXT UNIQUE NOT NULL,
    usado BOOLEAN DEFAULT 0
);
INSERT INTO codigo_acceso VALUES(1,'1941-2001-3690',1);
INSERT INTO codigo_acceso VALUES(2,'1234-8888-5555',0);
COMMIT;