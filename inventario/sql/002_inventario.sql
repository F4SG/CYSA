CREATE TABLE IF NOT EXISTS inventario(
 activo_id text PRIMARY KEY,interseccion text NOT NULL,acceso text,
 tipo text NOT NULL CHECK(tipo IN ('interseccion','acceso','camara','controlador')),
 ubicacion text NOT NULL,protocolo text NOT NULL,prueba boolean NOT NULL);
CREATE INDEX IF NOT EXISTS inventario_interseccion ON inventario(interseccion);
