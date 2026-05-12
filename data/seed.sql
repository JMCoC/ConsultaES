-- vendedores
INSERT INTO vendedores VALUES (1, 'Juan',      'Medellín',     '2021-03-15');
INSERT INTO vendedores VALUES (2, 'Pedro',     'Medellín',     '2020-07-01');
INSERT INTO vendedores VALUES (3, 'Andrés',    'Cali',         '2021-09-10');
INSERT INTO vendedores VALUES (4, 'Camila',    'Bogotá',       '2022-01-20');
INSERT INTO vendedores VALUES (5, 'Luisa',     'Cali',         '2019-11-05');
INSERT INTO vendedores VALUES (6, 'Carlos',    'Barranquilla', '2020-04-18');
INSERT INTO vendedores VALUES (7, 'Natalia',   'Bogotá',       '2023-02-14');
INSERT INTO vendedores VALUES (8, 'Sebastián', 'Barranquilla', '2018-06-30');

-- clientes
INSERT INTO clientes VALUES (1,  'Laura',    'Bogotá',       '2022-05-10', 'regular');
INSERT INTO clientes VALUES (2,  'Carlos',   'Medellín',     '2021-08-22', 'premium');
INSERT INTO clientes VALUES (3,  'Juan',     'Cali',         '2020-11-03', 'premium');
INSERT INTO clientes VALUES (4,  'María',    'Cali',         '2023-01-15', 'regular');
INSERT INTO clientes VALUES (5,  'Andrés',   'Barranquilla', '2022-07-19', 'regular');
INSERT INTO clientes VALUES (6,  'Sofía',    'Bogotá',       '2021-03-28', 'premium');
INSERT INTO clientes VALUES (7,  'Valentina','Medellín',     '2023-06-11', 'regular');
INSERT INTO clientes VALUES (8,  'Diego',    'Cali',         '2020-09-04', 'premium');
INSERT INTO clientes VALUES (9,  'Camila',   'Barranquilla', '2022-12-01', 'regular');
INSERT INTO clientes VALUES (10, 'Felipe',   'Bogotá',       '2021-04-17', 'regular');
INSERT INTO clientes VALUES (11, 'Daniela',  'Cali',         '2023-08-29', 'premium');
INSERT INTO clientes VALUES (12, 'Mateo',    'Medellín',     '2020-02-14', 'regular');
INSERT INTO clientes VALUES (13, 'Isabella', 'Bogotá',       '2022-10-05', 'premium');
INSERT INTO clientes VALUES (14, 'Nicolás',  'Barranquilla', '2021-07-23', 'regular');
INSERT INTO clientes VALUES (15, 'Paula',    'Cali',         '2023-03-12', 'regular');
INSERT INTO clientes VALUES (16, 'Santiago', 'Medellín',     '2022-09-08', 'premium');
INSERT INTO clientes VALUES (17, 'Alejandra','Bogotá',       '2021-11-30', 'regular');
INSERT INTO clientes VALUES (18, 'Julián',   'Cali',         '2020-05-21', 'regular');
INSERT INTO clientes VALUES (19, 'Mariana',  'Barranquilla', '2023-04-06', 'premium');
INSERT INTO clientes VALUES (20, 'Ricardo',  'Bogotá',       '2022-02-17', 'regular');
INSERT INTO clientes VALUES (21, 'Gabriela', 'Medellín',     '2021-06-09', 'premium');
INSERT INTO clientes VALUES (22, 'Esteban',  'Cali',         '2023-09-14', 'regular');
INSERT INTO clientes VALUES (23, 'Natalia',  'Barranquilla', '2020-12-28', 'premium');

-- productos
INSERT INTO productos VALUES (1,  'Teclado',             'Electrónica', 120000.0);
INSERT INTO productos VALUES (2,  'Mouse inalámbrico',   'Electrónica',  85000.0);
INSERT INTO productos VALUES (3,  'Monitor 24"',         'Electrónica', 750000.0);
INSERT INTO productos VALUES (4,  'Audífonos Bluetooth', 'Electrónica', 220000.0);
INSERT INTO productos VALUES (5,  'Cargador USB-C',      'Electrónica',  45000.0);
INSERT INTO productos VALUES (6,  'Camiseta deportiva',  'Ropa',          55000.0);
INSERT INTO productos VALUES (7,  'Chaqueta impermeable','Ropa',         180000.0);
INSERT INTO productos VALUES (8,  'Jeans clásico',       'Ropa',         130000.0);
INSERT INTO productos VALUES (9,  'Zapatillas running',  'Deportes',     280000.0);
INSERT INTO productos VALUES (10, 'Balón de fútbol',     'Deportes',      65000.0);
INSERT INTO productos VALUES (11, 'Colchoneta yoga',     'Deportes',      90000.0);
INSERT INTO productos VALUES (12, 'Lámpara de escritorio','Hogar',        95000.0);
INSERT INTO productos VALUES (13, 'Cafetera eléctrica',  'Hogar',        195000.0);
INSERT INTO productos VALUES (14, 'Juego de sábanas',    'Hogar',        120000.0);
INSERT INTO productos VALUES (15, 'Novela colombiana',   'Libros',        38000.0);
INSERT INTO productos VALUES (16, 'Atlas de historia',   'Libros',        52000.0);
INSERT INTO productos VALUES (17, 'Libro de cocina',     'Libros',        44000.0);

-- pedidos
-- 2024 — distribuidos a lo largo del año con ~25 en marzo
INSERT INTO pedidos VALUES (1,  3,  2, '2024-03-02',  250000.0);
INSERT INTO pedidos VALUES (2,  4,  2, '2024-03-05',  180000.0);
INSERT INTO pedidos VALUES (3,  8,  2, '2024-03-07',  550000.0);
INSERT INTO pedidos VALUES (4,  11, 2, '2024-03-09',  220000.0);
INSERT INTO pedidos VALUES (5,  15, 3, '2024-03-10',  130000.0);
INSERT INTO pedidos VALUES (6,  18, 5, '2024-03-11',   95000.0);
INSERT INTO pedidos VALUES (7,  22, 2, '2024-03-12',  320000.0);
INSERT INTO pedidos VALUES (8,  3,  1, '2024-03-14',  450000.0);
INSERT INTO pedidos VALUES (9,  4,  3, '2024-03-15',  280000.0);
INSERT INTO pedidos VALUES (10, 8,  5, '2024-03-17',  190000.0);
INSERT INTO pedidos VALUES (11, 11, 2, '2024-03-18',  660000.0);
INSERT INTO pedidos VALUES (12, 15, 1, '2024-03-19',  120000.0);
INSERT INTO pedidos VALUES (13, 18, 3, '2024-03-20',  385000.0);
INSERT INTO pedidos VALUES (14, 22, 2, '2024-03-21',  510000.0);
INSERT INTO pedidos VALUES (15, 3,  5, '2024-03-22',  250000.0);
INSERT INTO pedidos VALUES (16, 4,  2, '2024-03-23',  870000.0);
INSERT INTO pedidos VALUES (17, 8,  1, '2024-03-24',  430000.0);
INSERT INTO pedidos VALUES (18, 11, 3, '2024-03-25',  290000.0);
INSERT INTO pedidos VALUES (19, 15, 2, '2024-03-26',  145000.0);
INSERT INTO pedidos VALUES (20, 18, 5, '2024-03-27',  530000.0);
INSERT INTO pedidos VALUES (21, 22, 2, '2024-03-28',  210000.0);
INSERT INTO pedidos VALUES (22, 3,  1, '2024-03-29',  680000.0);
INSERT INTO pedidos VALUES (23, 4,  3, '2024-03-30',  350000.0);
INSERT INTO pedidos VALUES (24, 8,  2, '2024-03-31',  120000.0);
-- resto del año 2024
INSERT INTO pedidos VALUES (25, 1,  4, '2024-01-08',  310000.0);
INSERT INTO pedidos VALUES (26, 2,  6, '2024-01-15',  450000.0);
INSERT INTO pedidos VALUES (27, 5,  8, '2024-01-22',   90000.0);
INSERT INTO pedidos VALUES (28, 6,  4, '2024-02-03',  780000.0);
INSERT INTO pedidos VALUES (29, 7,  7, '2024-02-10',  165000.0);
INSERT INTO pedidos VALUES (30, 9,  6, '2024-02-18',  240000.0);
INSERT INTO pedidos VALUES (31, 10, 4, '2024-02-25',  130000.0);
INSERT INTO pedidos VALUES (32, 12, 7, '2024-04-05',  560000.0);
INSERT INTO pedidos VALUES (33, 13, 4, '2024-04-12',  880000.0);
INSERT INTO pedidos VALUES (34, 14, 8, '2024-04-19',  200000.0);
INSERT INTO pedidos VALUES (35, 16, 7, '2024-04-26',  340000.0);
INSERT INTO pedidos VALUES (36, 17, 4, '2024-05-03',  420000.0);
INSERT INTO pedidos VALUES (37, 19, 6, '2024-05-10',  750000.0);
INSERT INTO pedidos VALUES (38, 20, 8, '2024-05-17',  185000.0);
INSERT INTO pedidos VALUES (39, 21, 4, '2024-05-24',  630000.0);
INSERT INTO pedidos VALUES (40, 23, 7, '2024-05-31',  270000.0);
INSERT INTO pedidos VALUES (41, 1,  6, '2024-06-07',  495000.0);
INSERT INTO pedidos VALUES (42, 2,  8, '2024-06-14',  120000.0);
INSERT INTO pedidos VALUES (43, 5,  4, '2024-06-21',  810000.0);
INSERT INTO pedidos VALUES (44, 6,  7, '2024-06-28',  350000.0);
INSERT INTO pedidos VALUES (45, 7,  6, '2024-07-05',  230000.0);
INSERT INTO pedidos VALUES (46, 9,  4, '2024-07-12',  670000.0);
INSERT INTO pedidos VALUES (47, 10, 8, '2024-07-19',  145000.0);
INSERT INTO pedidos VALUES (48, 12, 7, '2024-07-26',  540000.0);
INSERT INTO pedidos VALUES (49, 13, 6, '2024-08-02',  290000.0);
INSERT INTO pedidos VALUES (50, 14, 4, '2024-08-09',  720000.0);
INSERT INTO pedidos VALUES (51, 16, 8, '2024-08-16',  380000.0);
INSERT INTO pedidos VALUES (52, 17, 7, '2024-08-23',  195000.0);
INSERT INTO pedidos VALUES (53, 19, 4, '2024-08-30',  860000.0);
INSERT INTO pedidos VALUES (54, 20, 6, '2024-09-06',  440000.0);
INSERT INTO pedidos VALUES (55, 21, 8, '2024-09-13',  310000.0);
INSERT INTO pedidos VALUES (56, 23, 4, '2024-09-20',  580000.0);
INSERT INTO pedidos VALUES (57, 1,  7, '2024-09-27',  260000.0);
INSERT INTO pedidos VALUES (58, 2,  6, '2024-10-04',  920000.0);
INSERT INTO pedidos VALUES (59, 5,  4, '2024-10-11',  170000.0);
INSERT INTO pedidos VALUES (60, 6,  8, '2024-10-18',  740000.0);
INSERT INTO pedidos VALUES (61, 7,  7, '2024-10-25',  330000.0);
INSERT INTO pedidos VALUES (62, 9,  4, '2024-11-01',  210000.0);
INSERT INTO pedidos VALUES (63, 10, 6, '2024-11-08',  650000.0);
INSERT INTO pedidos VALUES (64, 12, 8, '2024-11-15',  480000.0);
INSERT INTO pedidos VALUES (65, 13, 7, '2024-11-22',  295000.0);
INSERT INTO pedidos VALUES (66, 14, 4, '2024-11-29', 1100000.0);
INSERT INTO pedidos VALUES (67, 16, 6, '2024-12-06',  580000.0);
INSERT INTO pedidos VALUES (68, 17, 8, '2024-12-13',  420000.0);
INSERT INTO pedidos VALUES (69, 19, 7, '2024-12-20', 1350000.0);
INSERT INTO pedidos VALUES (70, 20, 4, '2024-12-27',  290000.0);
-- 2025
INSERT INTO pedidos VALUES (71, 21, 6, '2025-01-03',  510000.0);
INSERT INTO pedidos VALUES (72, 23, 8, '2025-01-10',  175000.0);
INSERT INTO pedidos VALUES (73, 1,  4, '2025-01-17',  640000.0);
INSERT INTO pedidos VALUES (74, 2,  7, '2025-01-24',  380000.0);
INSERT INTO pedidos VALUES (75, 5,  6, '2025-01-31',  225000.0);
INSERT INTO pedidos VALUES (76, 6,  4, '2025-02-07',  790000.0);
INSERT INTO pedidos VALUES (77, 7,  8, '2025-02-14',  155000.0);
INSERT INTO pedidos VALUES (78, 9,  7, '2025-02-21',  430000.0);
INSERT INTO pedidos VALUES (79, 10, 4, '2025-02-28',  300000.0);
-- 2025 marzo — segundo bloque de ~25
INSERT INTO pedidos VALUES (80, 3,  2, '2025-03-01',  480000.0);
INSERT INTO pedidos VALUES (81, 4,  2, '2025-03-03',  220000.0);
INSERT INTO pedidos VALUES (82, 8,  2, '2025-03-05',  350000.0);
INSERT INTO pedidos VALUES (83, 11, 2, '2025-03-07',  590000.0);
INSERT INTO pedidos VALUES (84, 15, 3, '2025-03-09',  140000.0);
INSERT INTO pedidos VALUES (85, 18, 5, '2025-03-11',  270000.0);
INSERT INTO pedidos VALUES (86, 22, 2, '2025-03-13',  415000.0);
INSERT INTO pedidos VALUES (87, 3,  1, '2025-03-15',  620000.0);
INSERT INTO pedidos VALUES (88, 4,  3, '2025-03-17',  195000.0);
INSERT INTO pedidos VALUES (89, 8,  5, '2025-03-19',  510000.0);
INSERT INTO pedidos VALUES (90, 11, 2, '2025-03-21',  330000.0);
INSERT INTO pedidos VALUES (91, 15, 1, '2025-03-23',  250000.0);
INSERT INTO pedidos VALUES (92, 18, 3, '2025-03-24',  680000.0);
INSERT INTO pedidos VALUES (93, 22, 2, '2025-03-25',  175000.0);
INSERT INTO pedidos VALUES (94, 3,  5, '2025-03-26',  920000.0);
INSERT INTO pedidos VALUES (95, 4,  2, '2025-03-27',  340000.0);
INSERT INTO pedidos VALUES (96, 8,  1, '2025-03-28',  460000.0);
INSERT INTO pedidos VALUES (97, 11, 3, '2025-03-29',  285000.0);
INSERT INTO pedidos VALUES (98, 15, 2, '2025-03-30',  730000.0);
INSERT INTO pedidos VALUES (99, 18, 5, '2025-03-31',  190000.0);
-- resto 2025
INSERT INTO pedidos VALUES (100, 12, 6, '2025-04-04',  550000.0);
INSERT INTO pedidos VALUES (101, 13, 4, '2025-04-11',  870000.0);
INSERT INTO pedidos VALUES (102, 14, 8, '2025-04-18',  210000.0);
INSERT INTO pedidos VALUES (103, 16, 7, '2025-04-25',  395000.0);
INSERT INTO pedidos VALUES (104, 17, 4, '2025-05-02',  680000.0);
INSERT INTO pedidos VALUES (105, 19, 6, '2025-05-09',  145000.0);
INSERT INTO pedidos VALUES (106, 20, 8, '2025-05-16',  830000.0);
INSERT INTO pedidos VALUES (107, 21, 4, '2025-05-23',  270000.0);
INSERT INTO pedidos VALUES (108, 23, 7, '2025-05-30',  510000.0);
INSERT INTO pedidos VALUES (109, 1,  6, '2025-06-06',  360000.0);
INSERT INTO pedidos VALUES (110, 2,  8, '2025-06-13',  980000.0);

-- detalle_pedidos
-- cada pedido tiene al menos una línea; varios pedidos tienen múltiples productos
-- Ambiguity case 3: clientes 3, 4, 8, 11, 15, 18, 22 compran Electrónica
-- (cubrimos los 4 productos eléctricos 1-5 para al menos 3 clientes por producto)

-- Pedido 1 (cliente 3, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (1,  1,  1, 120000.0);
INSERT INTO detalle_pedidos VALUES (1,  2,  1,  85000.0);

-- Pedido 2 (cliente 4, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (2,  3,  1, 750000.0);

-- Pedido 3 (cliente 8, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (3,  1,  1, 120000.0);
INSERT INTO detalle_pedidos VALUES (3,  4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (3,  5,  4,  45000.0);

-- Pedido 4 (cliente 11, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (4,  2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (4,  4,  1, 220000.0);

-- Pedido 5 (cliente 15, Cali, vendedor 3)
INSERT INTO detalle_pedidos VALUES (5,  8,  1, 130000.0);

-- Pedido 6 (cliente 18, Cali, vendedor 5)
INSERT INTO detalle_pedidos VALUES (6, 12,  1,  95000.0);

-- Pedido 7 (cliente 22, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (7,  1,  1, 120000.0);
INSERT INTO detalle_pedidos VALUES (7,  5,  2,  45000.0);
INSERT INTO detalle_pedidos VALUES (7,  9,  1, 280000.0);

-- Pedido 8 (cliente 3, Cali, vendedor Juan)
INSERT INTO detalle_pedidos VALUES (8,  3,  1, 750000.0);

-- Pedido 9 (cliente 4, Cali, vendedor 3)
INSERT INTO detalle_pedidos VALUES (9,  7,  1, 180000.0);
INSERT INTO detalle_pedidos VALUES (9, 10,  1,  65000.0);

-- Pedido 10 (cliente 8, Cali, vendedor 5)
INSERT INTO detalle_pedidos VALUES (10, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (10, 5,  1,  45000.0);

-- Pedido 11 (cliente 11, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (11, 3,  1, 750000.0);

-- Pedido 12 (cliente 15, Cali, vendedor Juan)
INSERT INTO detalle_pedidos VALUES (12, 6,  2,  55000.0);

-- Pedido 13 (cliente 18, Cali, vendedor 3)
INSERT INTO detalle_pedidos VALUES (13, 9,  1, 280000.0);
INSERT INTO detalle_pedidos VALUES (13,11,  1,  90000.0);

-- Pedido 14 (cliente 22, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (14, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (14, 1,  1, 120000.0);
INSERT INTO detalle_pedidos VALUES (14,13,  1, 195000.0);

-- Pedido 15 (cliente 3, Cali, vendedor 5)
INSERT INTO detalle_pedidos VALUES (15, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (15,14,  1, 120000.0);

-- Pedido 16 (cliente 4, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (16, 3,  1, 750000.0);
INSERT INTO detalle_pedidos VALUES (16, 4,  1, 220000.0);

-- Pedido 17 (cliente 8, Cali, vendedor Juan)
INSERT INTO detalle_pedidos VALUES (17, 1,  2, 120000.0);
INSERT INTO detalle_pedidos VALUES (17, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (17, 5,  1,  45000.0);

-- Pedido 18 (cliente 11, Cali, vendedor 3)
INSERT INTO detalle_pedidos VALUES (18,11,  2,  90000.0);
INSERT INTO detalle_pedidos VALUES (18,10,  1,  65000.0);

-- Pedido 19 (cliente 15, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (19, 6,  1,  55000.0);
INSERT INTO detalle_pedidos VALUES (19,15,  1,  38000.0);
INSERT INTO detalle_pedidos VALUES (19,17,  1,  44000.0);

-- Pedido 20 (cliente 18, Cali, vendedor 5)
INSERT INTO detalle_pedidos VALUES (20, 9,  1, 280000.0);
INSERT INTO detalle_pedidos VALUES (20,16,  1,  52000.0);
INSERT INTO detalle_pedidos VALUES (20,12,  1,  95000.0);
INSERT INTO detalle_pedidos VALUES (20,17,  1,  44000.0);

-- Pedido 21 (cliente 22, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (21, 5,  1,  45000.0);
INSERT INTO detalle_pedidos VALUES (21, 8,  1, 130000.0);

-- Pedido 22 (cliente 3, Cali, vendedor Juan)
INSERT INTO detalle_pedidos VALUES (22, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (22, 3,  1, 750000.0);

-- Pedido 23 (cliente 4, Cali, vendedor 3)
INSERT INTO detalle_pedidos VALUES (23, 7,  1, 180000.0);
INSERT INTO detalle_pedidos VALUES (23,13,  1, 195000.0);

-- Pedido 24 (cliente 8, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (24, 5,  1,  45000.0);
INSERT INTO detalle_pedidos VALUES (24,15,  2,  38000.0);

-- Pedido 25 (cliente 1, Bogotá)
INSERT INTO detalle_pedidos VALUES (25, 7,  1, 180000.0);
INSERT INTO detalle_pedidos VALUES (25,15,  1,  38000.0);

-- Pedido 26 (cliente 2, Medellín)
INSERT INTO detalle_pedidos VALUES (26, 9,  1, 280000.0);
INSERT INTO detalle_pedidos VALUES (26,13,  1, 195000.0);

-- Pedido 27 (cliente 5, Barranquilla)
INSERT INTO detalle_pedidos VALUES (27,10,  1,  65000.0);

-- Pedido 28 (cliente 6, Bogotá)
INSERT INTO detalle_pedidos VALUES (28, 3,  1, 750000.0);

-- Pedido 29 (cliente 7, Medellín)
INSERT INTO detalle_pedidos VALUES (29, 6,  1,  55000.0);
INSERT INTO detalle_pedidos VALUES (29, 8,  1, 130000.0);

-- Pedido 30 (cliente 9, Barranquilla)
INSERT INTO detalle_pedidos VALUES (30,12,  1,  95000.0);
INSERT INTO detalle_pedidos VALUES (30,16,  1,  52000.0);

-- Pedido 31 (cliente 10, Bogotá)
INSERT INTO detalle_pedidos VALUES (31, 8,  1, 130000.0);

-- Pedido 32 (cliente 12, Medellín)
INSERT INTO detalle_pedidos VALUES (32, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (32, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (32,14,  2, 120000.0);

-- Pedido 33 (cliente 13, Bogotá)
INSERT INTO detalle_pedidos VALUES (33, 3,  1, 750000.0);
INSERT INTO detalle_pedidos VALUES (33, 1,  1, 120000.0);

-- Pedido 34 (cliente 14, Barranquilla)
INSERT INTO detalle_pedidos VALUES (34, 6,  2,  55000.0);
INSERT INTO detalle_pedidos VALUES (34,15,  1,  38000.0);

-- Pedido 35 (cliente 16, Medellín)
INSERT INTO detalle_pedidos VALUES (35,11,  2,  90000.0);
INSERT INTO detalle_pedidos VALUES (35,16,  1,  52000.0);

-- Pedido 36 (cliente 17, Bogotá)
INSERT INTO detalle_pedidos VALUES (36, 9,  1, 280000.0);
INSERT INTO detalle_pedidos VALUES (36,13,  1, 195000.0);

-- Pedido 37 (cliente 19, Barranquilla)
INSERT INTO detalle_pedidos VALUES (37, 3,  1, 750000.0);

-- Pedido 38 (cliente 20, Bogotá)
INSERT INTO detalle_pedidos VALUES (38, 6,  1,  55000.0);
INSERT INTO detalle_pedidos VALUES (38,10,  2,  65000.0);

-- Pedido 39 (cliente 21, Medellín)
INSERT INTO detalle_pedidos VALUES (39, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (39, 9,  1, 280000.0);
INSERT INTO detalle_pedidos VALUES (39, 5,  2,  45000.0);

-- Pedido 40 (cliente 23, Barranquilla)
INSERT INTO detalle_pedidos VALUES (40,12,  1,  95000.0);
INSERT INTO detalle_pedidos VALUES (40,17,  1,  44000.0);

-- Pedido 41 (cliente 1, Bogotá)
INSERT INTO detalle_pedidos VALUES (41, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (41, 5,  2,  45000.0);
INSERT INTO detalle_pedidos VALUES (41,15,  1,  38000.0);
INSERT INTO detalle_pedidos VALUES (41,17,  1,  44000.0);

-- Pedido 42 (cliente 2, Medellín)
INSERT INTO detalle_pedidos VALUES (42, 8,  1, 130000.0);

-- Pedido 43 (cliente 5, Barranquilla)
INSERT INTO detalle_pedidos VALUES (43, 3,  1, 750000.0);
INSERT INTO detalle_pedidos VALUES (43, 2,  1,  85000.0);

-- Pedido 44 (cliente 6, Bogotá)
INSERT INTO detalle_pedidos VALUES (44,11,  2,  90000.0);
INSERT INTO detalle_pedidos VALUES (44,16,  1,  52000.0);

-- Pedido 45 (cliente 7, Medellín)
INSERT INTO detalle_pedidos VALUES (45, 6,  2,  55000.0);
INSERT INTO detalle_pedidos VALUES (45,10,  1,  65000.0);

-- Pedido 46 (cliente 9, Barranquilla)
INSERT INTO detalle_pedidos VALUES (46, 9,  1, 280000.0);
INSERT INTO detalle_pedidos VALUES (46,13,  1, 195000.0);

-- Pedido 47 (cliente 10, Bogotá)
INSERT INTO detalle_pedidos VALUES (47, 8,  1, 130000.0);

-- Pedido 48 (cliente 12, Medellín) — Electrónica completa
INSERT INTO detalle_pedidos VALUES (48, 1,  1, 120000.0);
INSERT INTO detalle_pedidos VALUES (48, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (48, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (48, 5,  1,  45000.0);

-- Pedido 49 (cliente 13, Bogotá) — Electrónica
INSERT INTO detalle_pedidos VALUES (49, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (49, 5,  1,  45000.0);
INSERT INTO detalle_pedidos VALUES (49,17,  1,  44000.0);

-- Pedido 50 (cliente 14, Barranquilla)
INSERT INTO detalle_pedidos VALUES (50, 3,  1, 750000.0);

-- Pedido 51 (cliente 16, Medellín)
INSERT INTO detalle_pedidos VALUES (51,14,  2, 120000.0);
INSERT INTO detalle_pedidos VALUES (51, 6,  1,  55000.0);
INSERT INTO detalle_pedidos VALUES (51, 8,  1, 130000.0);

-- Pedido 52 (cliente 17, Bogotá)
INSERT INTO detalle_pedidos VALUES (52, 6,  1,  55000.0);
INSERT INTO detalle_pedidos VALUES (52,10,  2,  65000.0);

-- Pedido 53 (cliente 19, Barranquilla)
INSERT INTO detalle_pedidos VALUES (53, 3,  1, 750000.0);
INSERT INTO detalle_pedidos VALUES (53, 1,  1, 120000.0);

-- Pedido 54 (cliente 20, Bogotá)
INSERT INTO detalle_pedidos VALUES (54,12,  2,  95000.0);
INSERT INTO detalle_pedidos VALUES (54,16,  1,  52000.0);

-- Pedido 55 (cliente 21, Medellín)
INSERT INTO detalle_pedidos VALUES (55,11,  2,  90000.0);
INSERT INTO detalle_pedidos VALUES (55, 9,  1, 280000.0);

-- Pedido 56 (cliente 23, Barranquilla)
INSERT INTO detalle_pedidos VALUES (56, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (56, 5,  2,  45000.0);
INSERT INTO detalle_pedidos VALUES (56,14,  1, 120000.0);

-- Pedido 57 (cliente 1, Bogotá)
INSERT INTO detalle_pedidos VALUES (57, 7,  1, 180000.0);
INSERT INTO detalle_pedidos VALUES (57,17,  1,  44000.0);

-- Pedido 58 (cliente 2, Medellín)
INSERT INTO detalle_pedidos VALUES (58, 3,  1, 750000.0);
INSERT INTO detalle_pedidos VALUES (58, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (58, 4,  1, 220000.0);

-- Pedido 59 (cliente 5, Barranquilla)
INSERT INTO detalle_pedidos VALUES (59, 8,  1, 130000.0);

-- Pedido 60 (cliente 6, Bogotá)
INSERT INTO detalle_pedidos VALUES (60, 3,  1, 750000.0);

-- Pedido 61 (cliente 7, Medellín)
INSERT INTO detalle_pedidos VALUES (61,13,  1, 195000.0);
INSERT INTO detalle_pedidos VALUES (61, 8,  1, 130000.0);

-- Pedido 62 (cliente 9, Barranquilla)
INSERT INTO detalle_pedidos VALUES (62, 6,  2,  55000.0);
INSERT INTO detalle_pedidos VALUES (62,10,  1,  65000.0);

-- Pedido 63 (cliente 10, Bogotá)
INSERT INTO detalle_pedidos VALUES (63, 9,  1, 280000.0);
INSERT INTO detalle_pedidos VALUES (63, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (63, 5,  1,  45000.0);

-- Pedido 64 (cliente 12, Medellín)
INSERT INTO detalle_pedidos VALUES (64,12,  2,  95000.0);
INSERT INTO detalle_pedidos VALUES (64,14,  1, 120000.0);
INSERT INTO detalle_pedidos VALUES (64,16,  1,  52000.0);

-- Pedido 65 (cliente 13, Bogotá)
INSERT INTO detalle_pedidos VALUES (65, 6,  1,  55000.0);
INSERT INTO detalle_pedidos VALUES (65,11,  1,  90000.0);
INSERT INTO detalle_pedidos VALUES (65,15,  1,  38000.0);

-- Pedido 66 (cliente 14, Barranquilla)
INSERT INTO detalle_pedidos VALUES (66, 3,  1, 750000.0);
INSERT INTO detalle_pedidos VALUES (66, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (66, 1,  1, 120000.0);

-- Pedido 67 (cliente 16, Medellín)
INSERT INTO detalle_pedidos VALUES (67, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (67, 5,  2,  45000.0);
INSERT INTO detalle_pedidos VALUES (67, 9,  1, 280000.0);

-- Pedido 68 (cliente 17, Bogotá)
INSERT INTO detalle_pedidos VALUES (68, 8,  1, 130000.0);
INSERT INTO detalle_pedidos VALUES (68,17,  1,  44000.0);
INSERT INTO detalle_pedidos VALUES (68,16,  2,  52000.0);

-- Pedido 69 (cliente 19, Barranquilla)
INSERT INTO detalle_pedidos VALUES (69, 3,  1, 750000.0);
INSERT INTO detalle_pedidos VALUES (69, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (69, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (69, 1,  1, 120000.0);
INSERT INTO detalle_pedidos VALUES (69, 5,  1,  45000.0);

-- Pedido 70 (cliente 20, Bogotá)
INSERT INTO detalle_pedidos VALUES (70,12,  1,  95000.0);
INSERT INTO detalle_pedidos VALUES (70,17,  1,  44000.0);

-- Pedido 71 (cliente 21, Medellín)
INSERT INTO detalle_pedidos VALUES (71, 9,  1, 280000.0);
INSERT INTO detalle_pedidos VALUES (71,13,  1, 195000.0);

-- Pedido 72 (cliente 23, Barranquilla)
INSERT INTO detalle_pedidos VALUES (72, 6,  1,  55000.0);
INSERT INTO detalle_pedidos VALUES (72,15,  1,  38000.0);
INSERT INTO detalle_pedidos VALUES (72,10,  1,  65000.0);

-- Pedido 73 (cliente 1, Bogotá)
INSERT INTO detalle_pedidos VALUES (73, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (73, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (73, 5,  1,  45000.0);
INSERT INTO detalle_pedidos VALUES (73, 8,  1, 130000.0);
INSERT INTO detalle_pedidos VALUES (73,17,  1,  44000.0);

-- Pedido 74 (cliente 2, Medellín)
INSERT INTO detalle_pedidos VALUES (74,11,  2,  90000.0);
INSERT INTO detalle_pedidos VALUES (74,14,  1, 120000.0);

-- Pedido 75 (cliente 5, Barranquilla)
INSERT INTO detalle_pedidos VALUES (75, 6,  2,  55000.0);
INSERT INTO detalle_pedidos VALUES (75,16,  1,  52000.0);

-- Pedido 76 (cliente 6, Bogotá)
INSERT INTO detalle_pedidos VALUES (76, 3,  1, 750000.0);

-- Pedido 77 (cliente 7, Medellín)
INSERT INTO detalle_pedidos VALUES (77, 8,  1, 130000.0);

-- Pedido 78 (cliente 9, Barranquilla)
INSERT INTO detalle_pedidos VALUES (78,12,  1,  95000.0);
INSERT INTO detalle_pedidos VALUES (78,13,  1, 195000.0);
INSERT INTO detalle_pedidos VALUES (78,15,  1,  38000.0);

-- Pedido 79 (cliente 10, Bogotá)
INSERT INTO detalle_pedidos VALUES (79, 9,  1, 280000.0);

-- 2025 marzo
-- Pedido 80 (cliente 3, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (80, 1,  2, 120000.0);
INSERT INTO detalle_pedidos VALUES (80, 5,  1,  45000.0);
INSERT INTO detalle_pedidos VALUES (80, 4,  1, 220000.0);

-- Pedido 81 (cliente 4, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (81, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (81, 8,  1, 130000.0);

-- Pedido 82 (cliente 8, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (82, 3,  1, 750000.0);

-- Pedido 83 (cliente 11, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (83, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (83, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (83, 1,  1, 120000.0);
INSERT INTO detalle_pedidos VALUES (83, 5,  1,  45000.0);

-- Pedido 84 (cliente 15, Cali, vendedor 3)
INSERT INTO detalle_pedidos VALUES (84, 8,  1, 130000.0);

-- Pedido 85 (cliente 18, Cali, vendedor 5)
INSERT INTO detalle_pedidos VALUES (85,12,  1,  95000.0);
INSERT INTO detalle_pedidos VALUES (85,17,  1,  44000.0);
INSERT INTO detalle_pedidos VALUES (85, 6,  1,  55000.0);

-- Pedido 86 (cliente 22, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (86, 9,  1, 280000.0);
INSERT INTO detalle_pedidos VALUES (86, 5,  1,  45000.0);
INSERT INTO detalle_pedidos VALUES (86,16,  1,  52000.0);

-- Pedido 87 (cliente 3, Cali, vendedor Juan)
INSERT INTO detalle_pedidos VALUES (87, 3,  1, 750000.0);

-- Pedido 88 (cliente 4, Cali, vendedor 3)
INSERT INTO detalle_pedidos VALUES (88, 6,  2,  55000.0);
INSERT INTO detalle_pedidos VALUES (88,15,  1,  38000.0);
INSERT INTO detalle_pedidos VALUES (88,10,  1,  65000.0);

-- Pedido 89 (cliente 8, Cali, vendedor 5)
INSERT INTO detalle_pedidos VALUES (89, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (89, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (89, 5,  1,  45000.0);
INSERT INTO detalle_pedidos VALUES (89, 1,  1, 120000.0);

-- Pedido 90 (cliente 11, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (90, 7,  1, 180000.0);
INSERT INTO detalle_pedidos VALUES (90,13,  1, 195000.0);

-- Pedido 91 (cliente 15, Cali, vendedor Juan)
INSERT INTO detalle_pedidos VALUES (91,11,  1,  90000.0);
INSERT INTO detalle_pedidos VALUES (91,14,  1, 120000.0);

-- Pedido 92 (cliente 18, Cali, vendedor 3)
INSERT INTO detalle_pedidos VALUES (92, 9,  1, 280000.0);
INSERT INTO detalle_pedidos VALUES (92, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (92, 2,  1,  85000.0);

-- Pedido 93 (cliente 22, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (93, 5,  1,  45000.0);
INSERT INTO detalle_pedidos VALUES (93,16,  1,  52000.0);
INSERT INTO detalle_pedidos VALUES (93,10,  1,  65000.0);

-- Pedido 94 (cliente 3, Cali, vendedor 5)
INSERT INTO detalle_pedidos VALUES (94, 3,  1, 750000.0);
INSERT INTO detalle_pedidos VALUES (94, 4,  1, 220000.0);

-- Pedido 95 (cliente 4, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (95, 1,  1, 120000.0);
INSERT INTO detalle_pedidos VALUES (95, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (95, 5,  1,  45000.0);

-- Pedido 96 (cliente 8, Cali, vendedor Juan)
INSERT INTO detalle_pedidos VALUES (96, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (96, 3,  1, 750000.0);

-- Pedido 97 (cliente 11, Cali, vendedor 3)
INSERT INTO detalle_pedidos VALUES (97,11,  2,  90000.0);
INSERT INTO detalle_pedidos VALUES (97,12,  1,  95000.0);

-- Pedido 98 (cliente 15, Cali, vendedor Pedro)
INSERT INTO detalle_pedidos VALUES (98, 9,  1, 280000.0);
INSERT INTO detalle_pedidos VALUES (98,13,  1, 195000.0);
INSERT INTO detalle_pedidos VALUES (98, 7,  1, 180000.0);

-- Pedido 99 (cliente 18, Cali, vendedor 5)
INSERT INTO detalle_pedidos VALUES (99, 6,  2,  55000.0);
INSERT INTO detalle_pedidos VALUES (99,15,  1,  38000.0);
INSERT INTO detalle_pedidos VALUES (99,10,  2,  65000.0);

-- Pedidos 100-110
INSERT INTO detalle_pedidos VALUES (100, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (100, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (100, 5,  2,  45000.0);

INSERT INTO detalle_pedidos VALUES (101, 3,  1, 750000.0);
INSERT INTO detalle_pedidos VALUES (101, 1,  1, 120000.0);

INSERT INTO detalle_pedidos VALUES (102, 8,  1, 130000.0);
INSERT INTO detalle_pedidos VALUES (102,15,  1,  38000.0);

INSERT INTO detalle_pedidos VALUES (103,11,  2,  90000.0);
INSERT INTO detalle_pedidos VALUES (103,16,  1,  52000.0);

INSERT INTO detalle_pedidos VALUES (104, 9,  1, 280000.0);
INSERT INTO detalle_pedidos VALUES (104,13,  1, 195000.0);
INSERT INTO detalle_pedidos VALUES (104, 5,  1,  45000.0);

INSERT INTO detalle_pedidos VALUES (105, 6,  1,  55000.0);
INSERT INTO detalle_pedidos VALUES (105,10,  1,  65000.0);

INSERT INTO detalle_pedidos VALUES (106, 3,  1, 750000.0);
INSERT INTO detalle_pedidos VALUES (106, 4,  1, 220000.0);

INSERT INTO detalle_pedidos VALUES (107,12,  1,  95000.0);
INSERT INTO detalle_pedidos VALUES (107,17,  1,  44000.0);

INSERT INTO detalle_pedidos VALUES (108, 4,  1, 220000.0);
INSERT INTO detalle_pedidos VALUES (108, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (108, 5,  1,  45000.0);

INSERT INTO detalle_pedidos VALUES (109, 7,  1, 180000.0);
INSERT INTO detalle_pedidos VALUES (109,16,  1,  52000.0);
INSERT INTO detalle_pedidos VALUES (109,15,  1,  38000.0);

INSERT INTO detalle_pedidos VALUES (110, 3,  1, 750000.0);
INSERT INTO detalle_pedidos VALUES (110, 2,  1,  85000.0);
INSERT INTO detalle_pedidos VALUES (110, 4,  1, 220000.0);
