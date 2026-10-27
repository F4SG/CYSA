CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE TABLE IF NOT EXISTS conteos (
 mensaje_id uuid NOT NULL, interseccion text NOT NULL, acceso text NOT NULL,carril text NOT NULL,
 clase text NOT NULL CHECK (clase IN ('auto','micro','moto')), cantidad integer NOT NULL CHECK(cantidad>=0),
 inicio timestamptz NOT NULL,fin timestamptz NOT NULL,prueba boolean NOT NULL,
 CHECK(fin>inicio AND fin-inicio<=interval '30.5 seconds'),PRIMARY KEY(mensaje_id,inicio));
SELECT create_hypertable('conteos','inicio',if_not_exists=>TRUE);
CREATE INDEX IF NOT EXISTS conteos_busqueda ON conteos(interseccion,carril,inicio DESC);
CREATE TABLE IF NOT EXISTS estados(
 interseccion text PRIMARY KEY,mensaje_id uuid NOT NULL,fase_actual text NOT NULL,plan_activo text NOT NULL,
 estado_controlador text NOT NULL CHECK(estado_controlador IN ('conectado','desconectado','desconocido')),
 timestamp timestamptz NOT NULL,prueba boolean NOT NULL);
