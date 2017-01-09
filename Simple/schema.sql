
-- Table: public.page

-- DROP TABLE public.page;

CREATE TABLE public.page
(
  page_id serial NOT NULL,
  page_name text NOT NULL,
  page_label text NOT NULL,
  CONSTRAINT page_pkey PRIMARY KEY (page_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.page
  OWNER TO postgres;


-- Table: public.div

-- DROP TABLE public.div;

CREATE TABLE public.div
(
  div_id serial NOT NULL,
  page_id integer NOT NULL,
  div_class text DEFAULT 'solid'::text,
  div_text text,
  page_div_order integer,
  CONSTRAINT div_pkey PRIMARY KEY (div_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.div
  OWNER TO postgres;