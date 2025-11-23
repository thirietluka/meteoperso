-- 1) Créer le rôle (login + mot de passe)
CREATE ROLE meteo_user LOGIN PASSWORD 'motdepasse';

-- 2) Créer la base
CREATE DATABASE meteoperso_db OWNER meteo_user;

-- 3) Se connecter à la base
\c meteoperso_db

-- 4) Créer la table users
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    login TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- 5) Créer la table meteo_table
CREATE TABLE public.meteo_table (
    id SERIAL PRIMARY KEY,
    cpu INTEGER,
    ram INTEGER,
    disk INTEGER,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6) Donner les droits au rôle (par sécurité)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO meteo_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO meteo_user;
