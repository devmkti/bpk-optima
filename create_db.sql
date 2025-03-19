-- 1. Buat database optima dengan owner postgres
CREATE DATABASE IF NOT EXISTS optima OWNER postgres;

-- 2. Gunakan database optima
\c optima

-- 3. Buat tabel-tabel dalam database optima

-- public.detail_partisipasi1 definition

-- Drop table

-- DROP TABLE public.detail_partisipasi1;

CREATE TABLE public.detail_partisipasi1 (
	nip varchar NOT NULL,
	id_proyek uuid NOT NULL,
	best_to_others uuid NULL,
	others_to_worst uuid NULL
);

-- Permissions

ALTER TABLE public.detail_partisipasi1 OWNER TO postgres;
GRANT ALL ON TABLE public.detail_partisipasi1 TO postgres;


-- public.detail_partisipasi2 definition

-- Drop table

-- DROP TABLE public.detail_partisipasi2;

CREATE TABLE public.detail_partisipasi2 (
	nip varchar NOT NULL,
	id_kriteria uuid NOT NULL,
	opsi varchar NULL,
	skor int4 NULL,
	id_proyek uuid NULL
);

-- Permissions

ALTER TABLE public.detail_partisipasi2 OWNER TO postgres;
GRANT ALL ON TABLE public.detail_partisipasi2 TO postgres;


-- public.hasil_simulasi definition

-- Drop table

-- DROP TABLE public.hasil_simulasi;

CREATE TABLE public.hasil_simulasi (
	id uuid NOT NULL,
	id_task uuid NOT NULL,
	id_kriteria uuid NOT NULL,
	bobot numeric(10, 2) NOT NULL,
	CONSTRAINT hasil_simulasi_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE public.hasil_simulasi OWNER TO postgres;
GRANT ALL ON TABLE public.hasil_simulasi TO postgres;


-- public.kriteria definition

-- Drop table

-- DROP TABLE public.kriteria;

CREATE TABLE public.kriteria (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	id_proyek uuid NOT NULL,
	nama_kriteria varchar NULL,
	deskripsi varchar NULL,
	CONSTRAINT kriteria_pk PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE public.kriteria OWNER TO postgres;
GRANT ALL ON TABLE public.kriteria TO postgres;


-- public.kriteria_skor definition

-- Drop table

-- DROP TABLE public.kriteria_skor;

CREATE TABLE public.kriteria_skor (
	id_proyek uuid NULL,
	nip varchar NULL,
	id_kriteria uuid NULL,
	bobot float8 NULL,
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	CONSTRAINT kriteria_skor_pk PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE public.kriteria_skor OWNER TO postgres;
GRANT ALL ON TABLE public.kriteria_skor TO postgres;


-- public.pegawai definition

-- Drop table

-- DROP TABLE public.pegawai;

CREATE TABLE public.pegawai (
	nip varchar NOT NULL,
	nama varchar NULL,
	email varchar NULL,
	administrator bool NULL,
	CONSTRAINT pegawai_pk PRIMARY KEY (nip)
);

-- Permissions

ALTER TABLE public.pegawai OWNER TO postgres;
GRANT ALL ON TABLE public.pegawai TO postgres;


-- public.proyek definition

-- Drop table

-- DROP TABLE public.proyek;

CREATE TABLE public.proyek (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	nama_proyek varchar NULL,
	deskripsi varchar NULL,
	jumlah_kriteria int4 NULL,
	jumlah_responden int4 NULL,
	periode_mulai date NULL,
	periode_selesai date NULL,
	status varchar NULL,
	created_by varchar NULL,
	created_at date NULL,
	CONSTRAINT proyek_pk PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE public.proyek OWNER TO postgres;
GRANT ALL ON TABLE public.proyek TO postgres;


-- public.task_simulasi definition

-- Drop table

-- DROP TABLE public.task_simulasi;

CREATE TABLE public.task_simulasi (
	id uuid NOT NULL,
	nama_task varchar(255) NOT NULL,
	nama_metode varchar(255) NOT NULL,
	id_proyek uuid NOT NULL,
	tgl_simulasi timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT task_simulasi_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE public.task_simulasi OWNER TO postgres;
GRANT ALL ON TABLE public.task_simulasi TO postgres;