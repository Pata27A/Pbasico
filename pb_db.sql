PGDMP                      }            pb_db    17.4    17.4 �    v           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false            w           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false            x           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false            y           1262    17293    pb_db    DATABASE     k   CREATE DATABASE pb_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'es-ES';
    DROP DATABASE pb_db;
                     postgres    false            �            1259    17294    alembic_version    TABLE     X   CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);
 #   DROP TABLE public.alembic_version;
       public         heap r       postgres    false            �            1259    17300    archivos_rg90    TABLE     �   CREATE TABLE public.archivos_rg90 (
    id integer NOT NULL,
    fecha_generacion timestamp without time zone,
    nombre_archivo character varying(150) NOT NULL,
    ruta_archivo character varying(255) NOT NULL,
    estado character varying(50)
);
 !   DROP TABLE public.archivos_rg90;
       public         heap r       postgres    false            �            1259    17299    archivos_rg90_id_seq    SEQUENCE     �   CREATE SEQUENCE public.archivos_rg90_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.archivos_rg90_id_seq;
       public               postgres    false    219            z           0    0    archivos_rg90_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.archivos_rg90_id_seq OWNED BY public.archivos_rg90.id;
          public               postgres    false    218            �            1259    17461    bitacora    TABLE     �   CREATE TABLE public.bitacora (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    accion character varying(255) NOT NULL,
    fecha timestamp without time zone,
    detalles text
);
    DROP TABLE public.bitacora;
       public         heap r       postgres    false            �            1259    17460    bitacora_id_seq    SEQUENCE     �   CREATE SEQUENCE public.bitacora_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.bitacora_id_seq;
       public               postgres    false    247            {           0    0    bitacora_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public.bitacora_id_seq OWNED BY public.bitacora.id;
          public               postgres    false    246            �            1259    17307    cajas    TABLE     �   CREATE TABLE public.cajas (
    id integer NOT NULL,
    fecha date NOT NULL,
    monto_apertura double precision NOT NULL,
    monto_cierre double precision,
    abierta boolean
);
    DROP TABLE public.cajas;
       public         heap r       postgres    false            �            1259    17306    cajas_id_seq    SEQUENCE     �   CREATE SEQUENCE public.cajas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.cajas_id_seq;
       public               postgres    false    221            |           0    0    cajas_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.cajas_id_seq OWNED BY public.cajas.id;
          public               postgres    false    220            �            1259    17316 
   categorias    TABLE     �   CREATE TABLE public.categorias (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion character varying(255)
);
    DROP TABLE public.categorias;
       public         heap r       postgres    false            �            1259    17315    categorias_id_seq    SEQUENCE     �   CREATE SEQUENCE public.categorias_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.categorias_id_seq;
       public               postgres    false    223            }           0    0    categorias_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.categorias_id_seq OWNED BY public.categorias.id;
          public               postgres    false    222            �            1259    17325    clientes    TABLE     �   CREATE TABLE public.clientes (
    id integer NOT NULL,
    nombre character varying(150) NOT NULL,
    documento character varying(50),
    telefono character varying(50),
    email character varying(100)
);
    DROP TABLE public.clientes;
       public         heap r       postgres    false            �            1259    17324    clientes_id_seq    SEQUENCE     �   CREATE SEQUENCE public.clientes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.clientes_id_seq;
       public               postgres    false    225            ~           0    0    clientes_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public.clientes_id_seq OWNED BY public.clientes.id;
          public               postgres    false    224            �            1259    17390 	   cobranzas    TABLE       CREATE TABLE public.cobranzas (
    id integer NOT NULL,
    factura_id integer NOT NULL,
    fecha timestamp without time zone,
    monto double precision NOT NULL,
    metodo_pago_id integer NOT NULL,
    descripcion character varying(255),
    usuario_id integer NOT NULL
);
    DROP TABLE public.cobranzas;
       public         heap r       postgres    false            �            1259    17389    cobranzas_id_seq    SEQUENCE     �   CREATE SEQUENCE public.cobranzas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public.cobranzas_id_seq;
       public               postgres    false    237                       0    0    cobranzas_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public.cobranzas_id_seq OWNED BY public.cobranzas.id;
          public               postgres    false    236            �            1259    17407    detalle_factura    TABLE     �   CREATE TABLE public.detalle_factura (
    id integer NOT NULL,
    factura_id integer NOT NULL,
    producto_id integer NOT NULL,
    cantidad integer NOT NULL,
    precio_unitario double precision NOT NULL,
    subtotal double precision NOT NULL
);
 #   DROP TABLE public.detalle_factura;
       public         heap r       postgres    false            �            1259    17406    detalle_factura_id_seq    SEQUENCE     �   CREATE SEQUENCE public.detalle_factura_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.detalle_factura_id_seq;
       public               postgres    false    239            �           0    0    detalle_factura_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.detalle_factura_id_seq OWNED BY public.detalle_factura.id;
          public               postgres    false    238            �            1259    17498    empresa    TABLE     �  CREATE TABLE public.empresa (
    id integer NOT NULL,
    nombre character varying(150) NOT NULL,
    ruc character varying(20) NOT NULL,
    direccion character varying(150) NOT NULL,
    ciudad character varying(100) NOT NULL,
    telefono character varying(50) NOT NULL,
    timbrado_numero character varying(20) NOT NULL,
    timbrado_vigencia_desde date NOT NULL,
    timbrado_vigencia_hasta date NOT NULL,
    fecha_creacion timestamp without time zone
);
    DROP TABLE public.empresa;
       public         heap r       postgres    false            �            1259    17497    empresa_id_seq    SEQUENCE     �   CREATE SEQUENCE public.empresa_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE public.empresa_id_seq;
       public               postgres    false    249            �           0    0    empresa_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public.empresa_id_seq OWNED BY public.empresa.id;
          public               postgres    false    248            �            1259    17350    facturas    TABLE     4  CREATE TABLE public.facturas (
    id integer NOT NULL,
    cliente_id integer,
    numero character varying(50) NOT NULL,
    fecha timestamp without time zone,
    total double precision NOT NULL,
    impuesto double precision NOT NULL,
    estado character varying(20),
    usuario_id integer NOT NULL
);
    DROP TABLE public.facturas;
       public         heap r       postgres    false            �            1259    17349    facturas_id_seq    SEQUENCE     �   CREATE SEQUENCE public.facturas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.facturas_id_seq;
       public               postgres    false    231            �           0    0    facturas_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public.facturas_id_seq OWNED BY public.facturas.id;
          public               postgres    false    230            �            1259    17332    ganancias_diarias    TABLE     �   CREATE TABLE public.ganancias_diarias (
    id integer NOT NULL,
    fecha date NOT NULL,
    total_ganancia double precision NOT NULL
);
 %   DROP TABLE public.ganancias_diarias;
       public         heap r       postgres    false            �            1259    17331    ganancias_diarias_id_seq    SEQUENCE     �   CREATE SEQUENCE public.ganancias_diarias_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.ganancias_diarias_id_seq;
       public               postgres    false    227            �           0    0    ganancias_diarias_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.ganancias_diarias_id_seq OWNED BY public.ganancias_diarias.id;
          public               postgres    false    226            �            1259    17341    metodos_pago    TABLE     i   CREATE TABLE public.metodos_pago (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL
);
     DROP TABLE public.metodos_pago;
       public         heap r       postgres    false            �            1259    17340    metodos_pago_id_seq    SEQUENCE     �   CREATE SEQUENCE public.metodos_pago_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.metodos_pago_id_seq;
       public               postgres    false    229            �           0    0    metodos_pago_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.metodos_pago_id_seq OWNED BY public.metodos_pago.id;
          public               postgres    false    228            �            1259    17364    movimientos_caja    TABLE       CREATE TABLE public.movimientos_caja (
    id integer NOT NULL,
    caja_id integer NOT NULL,
    tipo character varying(20) NOT NULL,
    monto double precision NOT NULL,
    descripcion character varying(255),
    fecha timestamp without time zone,
    usuario_id integer NOT NULL
);
 $   DROP TABLE public.movimientos_caja;
       public         heap r       postgres    false            �            1259    17363    movimientos_caja_id_seq    SEQUENCE     �   CREATE SEQUENCE public.movimientos_caja_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.movimientos_caja_id_seq;
       public               postgres    false    233            �           0    0    movimientos_caja_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.movimientos_caja_id_seq OWNED BY public.movimientos_caja.id;
          public               postgres    false    232            �            1259    17424    movimientos_stock    TABLE       CREATE TABLE public.movimientos_stock (
    id integer NOT NULL,
    producto_id integer NOT NULL,
    tipo character varying(20) NOT NULL,
    cantidad integer NOT NULL,
    descripcion character varying(255),
    fecha timestamp without time zone,
    usuario_id integer NOT NULL
);
 %   DROP TABLE public.movimientos_stock;
       public         heap r       postgres    false            �            1259    17423    movimientos_stock_id_seq    SEQUENCE     �   CREATE SEQUENCE public.movimientos_stock_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.movimientos_stock_id_seq;
       public               postgres    false    241            �           0    0    movimientos_stock_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.movimientos_stock_id_seq OWNED BY public.movimientos_stock.id;
          public               postgres    false    240            �            1259    17376 	   productos    TABLE     A  CREATE TABLE public.productos (
    id integer NOT NULL,
    codigo character varying(50) NOT NULL,
    nombre character varying(150) NOT NULL,
    categoria_id integer,
    precio_costo double precision NOT NULL,
    precio_venta double precision NOT NULL,
    stock_minimo integer,
    stock_actual integer NOT NULL
);
    DROP TABLE public.productos;
       public         heap r       postgres    false            �            1259    17375    productos_id_seq    SEQUENCE     �   CREATE SEQUENCE public.productos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public.productos_id_seq;
       public               postgres    false    235            �           0    0    productos_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public.productos_id_seq OWNED BY public.productos.id;
          public               postgres    false    234            �            1259    17436    roles    TABLE     �   CREATE TABLE public.roles (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL,
    descripcion character varying(255)
);
    DROP TABLE public.roles;
       public         heap r       postgres    false            �            1259    17435    roles_id_seq    SEQUENCE     �   CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.roles_id_seq;
       public               postgres    false    243            �           0    0    roles_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;
          public               postgres    false    242            �            1259    17445    usuarios    TABLE     �   CREATE TABLE public.usuarios (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash text NOT NULL,
    rol_id integer NOT NULL,
    activo boolean
);
    DROP TABLE public.usuarios;
       public         heap r       postgres    false            �            1259    17444    usuarios_id_seq    SEQUENCE     �   CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.usuarios_id_seq;
       public               postgres    false    245            �           0    0    usuarios_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;
          public               postgres    false    244            p           2604    17303    archivos_rg90 id    DEFAULT     t   ALTER TABLE ONLY public.archivos_rg90 ALTER COLUMN id SET DEFAULT nextval('public.archivos_rg90_id_seq'::regclass);
 ?   ALTER TABLE public.archivos_rg90 ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    218    219    219            ~           2604    17464    bitacora id    DEFAULT     j   ALTER TABLE ONLY public.bitacora ALTER COLUMN id SET DEFAULT nextval('public.bitacora_id_seq'::regclass);
 :   ALTER TABLE public.bitacora ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    247    246    247            q           2604    17310    cajas id    DEFAULT     d   ALTER TABLE ONLY public.cajas ALTER COLUMN id SET DEFAULT nextval('public.cajas_id_seq'::regclass);
 7   ALTER TABLE public.cajas ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    220    221    221            r           2604    17319    categorias id    DEFAULT     n   ALTER TABLE ONLY public.categorias ALTER COLUMN id SET DEFAULT nextval('public.categorias_id_seq'::regclass);
 <   ALTER TABLE public.categorias ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    222    223    223            s           2604    17328    clientes id    DEFAULT     j   ALTER TABLE ONLY public.clientes ALTER COLUMN id SET DEFAULT nextval('public.clientes_id_seq'::regclass);
 :   ALTER TABLE public.clientes ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    225    224    225            y           2604    17393    cobranzas id    DEFAULT     l   ALTER TABLE ONLY public.cobranzas ALTER COLUMN id SET DEFAULT nextval('public.cobranzas_id_seq'::regclass);
 ;   ALTER TABLE public.cobranzas ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    236    237    237            z           2604    17410    detalle_factura id    DEFAULT     x   ALTER TABLE ONLY public.detalle_factura ALTER COLUMN id SET DEFAULT nextval('public.detalle_factura_id_seq'::regclass);
 A   ALTER TABLE public.detalle_factura ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    238    239    239                       2604    17501 
   empresa id    DEFAULT     h   ALTER TABLE ONLY public.empresa ALTER COLUMN id SET DEFAULT nextval('public.empresa_id_seq'::regclass);
 9   ALTER TABLE public.empresa ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    249    248    249            v           2604    17353    facturas id    DEFAULT     j   ALTER TABLE ONLY public.facturas ALTER COLUMN id SET DEFAULT nextval('public.facturas_id_seq'::regclass);
 :   ALTER TABLE public.facturas ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    230    231    231            t           2604    17335    ganancias_diarias id    DEFAULT     |   ALTER TABLE ONLY public.ganancias_diarias ALTER COLUMN id SET DEFAULT nextval('public.ganancias_diarias_id_seq'::regclass);
 C   ALTER TABLE public.ganancias_diarias ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    227    226    227            u           2604    17344    metodos_pago id    DEFAULT     r   ALTER TABLE ONLY public.metodos_pago ALTER COLUMN id SET DEFAULT nextval('public.metodos_pago_id_seq'::regclass);
 >   ALTER TABLE public.metodos_pago ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    228    229    229            w           2604    17367    movimientos_caja id    DEFAULT     z   ALTER TABLE ONLY public.movimientos_caja ALTER COLUMN id SET DEFAULT nextval('public.movimientos_caja_id_seq'::regclass);
 B   ALTER TABLE public.movimientos_caja ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    232    233    233            {           2604    17427    movimientos_stock id    DEFAULT     |   ALTER TABLE ONLY public.movimientos_stock ALTER COLUMN id SET DEFAULT nextval('public.movimientos_stock_id_seq'::regclass);
 C   ALTER TABLE public.movimientos_stock ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    241    240    241            x           2604    17379    productos id    DEFAULT     l   ALTER TABLE ONLY public.productos ALTER COLUMN id SET DEFAULT nextval('public.productos_id_seq'::regclass);
 ;   ALTER TABLE public.productos ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    235    234    235            |           2604    17439    roles id    DEFAULT     d   ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);
 7   ALTER TABLE public.roles ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    243    242    243            }           2604    17448    usuarios id    DEFAULT     j   ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);
 :   ALTER TABLE public.usuarios ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    244    245    245            S          0    17294    alembic_version 
   TABLE DATA           6   COPY public.alembic_version (version_num) FROM stdin;
    public               postgres    false    217   �       U          0    17300    archivos_rg90 
   TABLE DATA           c   COPY public.archivos_rg90 (id, fecha_generacion, nombre_archivo, ruta_archivo, estado) FROM stdin;
    public               postgres    false    219   �       q          0    17461    bitacora 
   TABLE DATA           K   COPY public.bitacora (id, usuario_id, accion, fecha, detalles) FROM stdin;
    public               postgres    false    247   2�       W          0    17307    cajas 
   TABLE DATA           Q   COPY public.cajas (id, fecha, monto_apertura, monto_cierre, abierta) FROM stdin;
    public               postgres    false    221   O�       Y          0    17316 
   categorias 
   TABLE DATA           =   COPY public.categorias (id, nombre, descripcion) FROM stdin;
    public               postgres    false    223   ��       [          0    17325    clientes 
   TABLE DATA           J   COPY public.clientes (id, nombre, documento, telefono, email) FROM stdin;
    public               postgres    false    225   Ĭ       g          0    17390 	   cobranzas 
   TABLE DATA           j   COPY public.cobranzas (id, factura_id, fecha, monto, metodo_pago_id, descripcion, usuario_id) FROM stdin;
    public               postgres    false    237   �       i          0    17407    detalle_factura 
   TABLE DATA           k   COPY public.detalle_factura (id, factura_id, producto_id, cantidad, precio_unitario, subtotal) FROM stdin;
    public               postgres    false    239   ��       s          0    17498    empresa 
   TABLE DATA           �   COPY public.empresa (id, nombre, ruc, direccion, ciudad, telefono, timbrado_numero, timbrado_vigencia_desde, timbrado_vigencia_hasta, fecha_creacion) FROM stdin;
    public               postgres    false    249   o�       a          0    17350    facturas 
   TABLE DATA           f   COPY public.facturas (id, cliente_id, numero, fecha, total, impuesto, estado, usuario_id) FROM stdin;
    public               postgres    false    231   �       ]          0    17332    ganancias_diarias 
   TABLE DATA           F   COPY public.ganancias_diarias (id, fecha, total_ganancia) FROM stdin;
    public               postgres    false    227   g�       _          0    17341    metodos_pago 
   TABLE DATA           2   COPY public.metodos_pago (id, nombre) FROM stdin;
    public               postgres    false    229   ��       c          0    17364    movimientos_caja 
   TABLE DATA           d   COPY public.movimientos_caja (id, caja_id, tipo, monto, descripcion, fecha, usuario_id) FROM stdin;
    public               postgres    false    233   �       k          0    17424    movimientos_stock 
   TABLE DATA           l   COPY public.movimientos_stock (id, producto_id, tipo, cantidad, descripcion, fecha, usuario_id) FROM stdin;
    public               postgres    false    241   ˳       e          0    17376 	   productos 
   TABLE DATA           }   COPY public.productos (id, codigo, nombre, categoria_id, precio_costo, precio_venta, stock_minimo, stock_actual) FROM stdin;
    public               postgres    false    235   �       m          0    17436    roles 
   TABLE DATA           8   COPY public.roles (id, nombre, descripcion) FROM stdin;
    public               postgres    false    243   Y�       o          0    17445    usuarios 
   TABLE DATA           V   COPY public.usuarios (id, username, email, password_hash, rol_id, activo) FROM stdin;
    public               postgres    false    245   ��       �           0    0    archivos_rg90_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.archivos_rg90_id_seq', 1, false);
          public               postgres    false    218            �           0    0    bitacora_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public.bitacora_id_seq', 1, false);
          public               postgres    false    246            �           0    0    cajas_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.cajas_id_seq', 6, true);
          public               postgres    false    220            �           0    0    categorias_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.categorias_id_seq', 1, false);
          public               postgres    false    222            �           0    0    clientes_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.clientes_id_seq', 1, true);
          public               postgres    false    224            �           0    0    cobranzas_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.cobranzas_id_seq', 28, true);
          public               postgres    false    236            �           0    0    detalle_factura_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.detalle_factura_id_seq', 43, true);
          public               postgres    false    238            �           0    0    empresa_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.empresa_id_seq', 2, true);
          public               postgres    false    248            �           0    0    facturas_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public.facturas_id_seq', 27, true);
          public               postgres    false    230            �           0    0    ganancias_diarias_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.ganancias_diarias_id_seq', 1, false);
          public               postgres    false    226            �           0    0    metodos_pago_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.metodos_pago_id_seq', 4, true);
          public               postgres    false    228            �           0    0    movimientos_caja_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.movimientos_caja_id_seq', 27, true);
          public               postgres    false    232            �           0    0    movimientos_stock_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.movimientos_stock_id_seq', 1, false);
          public               postgres    false    240            �           0    0    productos_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public.productos_id_seq', 5, true);
          public               postgres    false    234            �           0    0    roles_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.roles_id_seq', 3, true);
          public               postgres    false    242            �           0    0    usuarios_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.usuarios_id_seq', 4, true);
          public               postgres    false    244            �           2606    17298 #   alembic_version alembic_version_pkc 
   CONSTRAINT     j   ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);
 M   ALTER TABLE ONLY public.alembic_version DROP CONSTRAINT alembic_version_pkc;
       public                 postgres    false    217            �           2606    17305     archivos_rg90 archivos_rg90_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.archivos_rg90
    ADD CONSTRAINT archivos_rg90_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.archivos_rg90 DROP CONSTRAINT archivos_rg90_pkey;
       public                 postgres    false    219            �           2606    17468    bitacora bitacora_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.bitacora
    ADD CONSTRAINT bitacora_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.bitacora DROP CONSTRAINT bitacora_pkey;
       public                 postgres    false    247            �           2606    17314    cajas cajas_fecha_key 
   CONSTRAINT     Q   ALTER TABLE ONLY public.cajas
    ADD CONSTRAINT cajas_fecha_key UNIQUE (fecha);
 ?   ALTER TABLE ONLY public.cajas DROP CONSTRAINT cajas_fecha_key;
       public                 postgres    false    221            �           2606    17312    cajas cajas_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.cajas
    ADD CONSTRAINT cajas_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.cajas DROP CONSTRAINT cajas_pkey;
       public                 postgres    false    221            �           2606    17323     categorias categorias_nombre_key 
   CONSTRAINT     ]   ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT categorias_nombre_key UNIQUE (nombre);
 J   ALTER TABLE ONLY public.categorias DROP CONSTRAINT categorias_nombre_key;
       public                 postgres    false    223            �           2606    17321    categorias categorias_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT categorias_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.categorias DROP CONSTRAINT categorias_pkey;
       public                 postgres    false    223            �           2606    17330    clientes clientes_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.clientes DROP CONSTRAINT clientes_pkey;
       public                 postgres    false    225            �           2606    17395    cobranzas cobranzas_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.cobranzas
    ADD CONSTRAINT cobranzas_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.cobranzas DROP CONSTRAINT cobranzas_pkey;
       public                 postgres    false    237            �           2606    17412 $   detalle_factura detalle_factura_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.detalle_factura
    ADD CONSTRAINT detalle_factura_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.detalle_factura DROP CONSTRAINT detalle_factura_pkey;
       public                 postgres    false    239            �           2606    17505    empresa empresa_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.empresa
    ADD CONSTRAINT empresa_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.empresa DROP CONSTRAINT empresa_pkey;
       public                 postgres    false    249            �           2606    17357    facturas facturas_numero_key 
   CONSTRAINT     Y   ALTER TABLE ONLY public.facturas
    ADD CONSTRAINT facturas_numero_key UNIQUE (numero);
 F   ALTER TABLE ONLY public.facturas DROP CONSTRAINT facturas_numero_key;
       public                 postgres    false    231            �           2606    17355    facturas facturas_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.facturas
    ADD CONSTRAINT facturas_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.facturas DROP CONSTRAINT facturas_pkey;
       public                 postgres    false    231            �           2606    17339 -   ganancias_diarias ganancias_diarias_fecha_key 
   CONSTRAINT     i   ALTER TABLE ONLY public.ganancias_diarias
    ADD CONSTRAINT ganancias_diarias_fecha_key UNIQUE (fecha);
 W   ALTER TABLE ONLY public.ganancias_diarias DROP CONSTRAINT ganancias_diarias_fecha_key;
       public                 postgres    false    227            �           2606    17337 (   ganancias_diarias ganancias_diarias_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.ganancias_diarias
    ADD CONSTRAINT ganancias_diarias_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.ganancias_diarias DROP CONSTRAINT ganancias_diarias_pkey;
       public                 postgres    false    227            �           2606    17348 $   metodos_pago metodos_pago_nombre_key 
   CONSTRAINT     a   ALTER TABLE ONLY public.metodos_pago
    ADD CONSTRAINT metodos_pago_nombre_key UNIQUE (nombre);
 N   ALTER TABLE ONLY public.metodos_pago DROP CONSTRAINT metodos_pago_nombre_key;
       public                 postgres    false    229            �           2606    17346    metodos_pago metodos_pago_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.metodos_pago
    ADD CONSTRAINT metodos_pago_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.metodos_pago DROP CONSTRAINT metodos_pago_pkey;
       public                 postgres    false    229            �           2606    17369 &   movimientos_caja movimientos_caja_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.movimientos_caja
    ADD CONSTRAINT movimientos_caja_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.movimientos_caja DROP CONSTRAINT movimientos_caja_pkey;
       public                 postgres    false    233            �           2606    17429 (   movimientos_stock movimientos_stock_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.movimientos_stock
    ADD CONSTRAINT movimientos_stock_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.movimientos_stock DROP CONSTRAINT movimientos_stock_pkey;
       public                 postgres    false    241            �           2606    17383    productos productos_codigo_key 
   CONSTRAINT     [   ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_codigo_key UNIQUE (codigo);
 H   ALTER TABLE ONLY public.productos DROP CONSTRAINT productos_codigo_key;
       public                 postgres    false    235            �           2606    17381    productos productos_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.productos DROP CONSTRAINT productos_pkey;
       public                 postgres    false    235            �           2606    17443    roles roles_nombre_key 
   CONSTRAINT     S   ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_nombre_key UNIQUE (nombre);
 @   ALTER TABLE ONLY public.roles DROP CONSTRAINT roles_nombre_key;
       public                 postgres    false    243            �           2606    17441    roles roles_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.roles DROP CONSTRAINT roles_pkey;
       public                 postgres    false    243            �           2606    17452    usuarios usuarios_email_key 
   CONSTRAINT     W   ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);
 E   ALTER TABLE ONLY public.usuarios DROP CONSTRAINT usuarios_email_key;
       public                 postgres    false    245            �           2606    17450    usuarios usuarios_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.usuarios DROP CONSTRAINT usuarios_pkey;
       public                 postgres    false    245            �           2606    17454    usuarios usuarios_username_key 
   CONSTRAINT     ]   ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_username_key UNIQUE (username);
 H   ALTER TABLE ONLY public.usuarios DROP CONSTRAINT usuarios_username_key;
       public                 postgres    false    245            �           2606    17469 !   bitacora bitacora_usuario_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.bitacora
    ADD CONSTRAINT bitacora_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);
 K   ALTER TABLE ONLY public.bitacora DROP CONSTRAINT bitacora_usuario_id_fkey;
       public               postgres    false    4781    245    247            �           2606    17396 #   cobranzas cobranzas_factura_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.cobranzas
    ADD CONSTRAINT cobranzas_factura_id_fkey FOREIGN KEY (factura_id) REFERENCES public.facturas(id);
 M   ALTER TABLE ONLY public.cobranzas DROP CONSTRAINT cobranzas_factura_id_fkey;
       public               postgres    false    4761    231    237            �           2606    17401 '   cobranzas cobranzas_metodo_pago_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.cobranzas
    ADD CONSTRAINT cobranzas_metodo_pago_id_fkey FOREIGN KEY (metodo_pago_id) REFERENCES public.metodos_pago(id);
 Q   ALTER TABLE ONLY public.cobranzas DROP CONSTRAINT cobranzas_metodo_pago_id_fkey;
       public               postgres    false    237    4757    229            �           2606    17474 #   cobranzas cobranzas_usuario_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.cobranzas
    ADD CONSTRAINT cobranzas_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);
 M   ALTER TABLE ONLY public.cobranzas DROP CONSTRAINT cobranzas_usuario_id_fkey;
       public               postgres    false    245    4781    237            �           2606    17413 /   detalle_factura detalle_factura_factura_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.detalle_factura
    ADD CONSTRAINT detalle_factura_factura_id_fkey FOREIGN KEY (factura_id) REFERENCES public.facturas(id);
 Y   ALTER TABLE ONLY public.detalle_factura DROP CONSTRAINT detalle_factura_factura_id_fkey;
       public               postgres    false    231    239    4761            �           2606    17418 0   detalle_factura detalle_factura_producto_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.detalle_factura
    ADD CONSTRAINT detalle_factura_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES public.productos(id);
 Z   ALTER TABLE ONLY public.detalle_factura DROP CONSTRAINT detalle_factura_producto_id_fkey;
       public               postgres    false    239    235    4767            �           2606    17358 !   facturas facturas_cliente_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.facturas
    ADD CONSTRAINT facturas_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);
 K   ALTER TABLE ONLY public.facturas DROP CONSTRAINT facturas_cliente_id_fkey;
       public               postgres    false    225    231    4749            �           2606    17479 !   facturas facturas_usuario_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.facturas
    ADD CONSTRAINT facturas_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);
 K   ALTER TABLE ONLY public.facturas DROP CONSTRAINT facturas_usuario_id_fkey;
       public               postgres    false    231    4781    245            �           2606    17370 .   movimientos_caja movimientos_caja_caja_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.movimientos_caja
    ADD CONSTRAINT movimientos_caja_caja_id_fkey FOREIGN KEY (caja_id) REFERENCES public.cajas(id);
 X   ALTER TABLE ONLY public.movimientos_caja DROP CONSTRAINT movimientos_caja_caja_id_fkey;
       public               postgres    false    233    4743    221            �           2606    17484 1   movimientos_caja movimientos_caja_usuario_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.movimientos_caja
    ADD CONSTRAINT movimientos_caja_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);
 [   ALTER TABLE ONLY public.movimientos_caja DROP CONSTRAINT movimientos_caja_usuario_id_fkey;
       public               postgres    false    233    4781    245            �           2606    17430 4   movimientos_stock movimientos_stock_producto_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.movimientos_stock
    ADD CONSTRAINT movimientos_stock_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES public.productos(id);
 ^   ALTER TABLE ONLY public.movimientos_stock DROP CONSTRAINT movimientos_stock_producto_id_fkey;
       public               postgres    false    235    241    4767            �           2606    17489 3   movimientos_stock movimientos_stock_usuario_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.movimientos_stock
    ADD CONSTRAINT movimientos_stock_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);
 ]   ALTER TABLE ONLY public.movimientos_stock DROP CONSTRAINT movimientos_stock_usuario_id_fkey;
       public               postgres    false    245    4781    241            �           2606    17384 %   productos productos_categoria_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_categoria_id_fkey FOREIGN KEY (categoria_id) REFERENCES public.categorias(id);
 O   ALTER TABLE ONLY public.productos DROP CONSTRAINT productos_categoria_id_fkey;
       public               postgres    false    235    4747    223            �           2606    17455    usuarios usuarios_rol_id_fkey    FK CONSTRAINT     {   ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES public.roles(id);
 G   ALTER TABLE ONLY public.usuarios DROP CONSTRAINT usuarios_rol_id_fkey;
       public               postgres    false    245    4777    243            S      x�K1M53�L�064I����� +��      U      x������ � �      q      x������ � �      W   H   x�3�4202�50"NC�Qi\�Is���)D�.gh�32�j4EH�M���4CHZ�$��rF �=... �V|      Y      x������ � �      [   ;   x�3�t�KO�QN�KL*�L�4442615�4��02���43��M��a���\�=... �d      g   c  x�u�[j�0�o�*fzK�Z���o�r[f씄@ �kI
B��O��5YQ�TA����a��I1�������t���i�!I֧��&0��<Y��4���r?���BM&�$�#� �+�)��ɜ;����zs��G:)�A��?e`Yf�QV��m��5E��h� ۬��ZL6tgud0�ڜ�B��Vס��ir����fWث�j&E�|�vZ��LL1����T���T(k�Ȱ���@����������z`]�UǴ�����J�����ۮ��Ů�)$�ղ���������nC�X�~1*��u�e��&Uu{����8l�dN�^Is:���p?����u�P��~��������      i   �   x�e���0C��a
>�]��%��JF� y�E���õT5�A�� ��M9m���6H���8�毖H�Z9���� ��cS��*٥�BqU�n�����M�K:��=U#k%+{�d]�>]��j�ɢ�C��,�=d���˻y���i0��NV="ȪG U�d{d�q$���ɯ�	��'Z)�7ŞӸ�,^�a�O`:YmzYm��c|��z�      s   i   x�E�1
�0 �9=E/PI�&m����"X\ʗ/�����x�o��c��A�[�������6����VD��l@�����j��P��z*#�(4��pv����j��      a   o  x�u�9n�@и�}�&���v �O�`��?��M��lB)ѓ(���˃�Q��\���'����^���,�~��x+vkIe�2�Nf���!��I����>M��7��)���ڷ�;t
��F`��O�����Y��A��G���+4iݩOQ2�za-m۬7���dO�k��)��t���k��m��>E�Uj��^�*�ެ�	#�Z/d�e�������8��H+�u�h��b�w+�Vw��iF���k͒��S���u��q��^YT�	�(9v��:��|�x��d�P��lԩ����yB���N,�%���'�ͺ�E�Z����5N�q�XhD�M8uUD�'��96^�EKN�վ��v����<      ]      x������ � �      _   N   x�3�tMKM.�,��2�I,�J-ITHIUpIM�,��2Fs.JM	�p�%�����%g&*8%�%'e&r��qqq L�3      c   �  x���͎�0�s�}��l�_��č�R`X!!f5���e���QҜF�/��Ni������e����x�z�~���	lB��+���%��c����~fh��.��}W�D��E<�s�܊�O��������<�9��|c�&̕�2�b��(+Fᘑ�Ԯ n���NF��D��9��:�d;E�T�\[4�ٌo�o���S�y'�}�O�Xђ�
G�#� ��N���z%���l�@\9w��kEN��͡�s�O��s��D���s�C;G��C�.����;N�;X�S�,V�#��yp�8?\^�0%3�e�P��MG����'�/I��r/�8T�+pr[^���v
���SVΝ�C�8�-\�ǋ�~"�́�YKn��Al��o�'0�!tN��˅r��;C8~���u%>H�����l���XEI��w���8��u/��.m�ާq�a�)      k      x������ � �      e   a   x�3�400��*M����4200�4��&\�@YSNǪ���"��)B�(o�铚���!mj�e�6�t�,NŢ۔�(m�Y���!il����� ��      m   6   x�3�tL����,.)JL�/���QH��S(�O�/V��Ԣ����b�=... ��      o   c   x�3�LL��̃����9�z����*FI*�F*~�Q9f�EN�ޅ�e�N�NUE����E��ف�a�FE����f&Q.�U��F�Ɯ%\1z\\\ ��R     