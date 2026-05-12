CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    ciudad TEXT NOT NULL,
    fecha_registro DATE NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('regular','premium'))
);
CREATE TABLE vendedores (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    ciudad TEXT NOT NULL,
    fecha_ingreso DATE NOT NULL
);
CREATE TABLE productos (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio REAL NOT NULL
);
CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY,
    id_cliente INTEGER REFERENCES clientes(id),
    id_vendedor INTEGER REFERENCES vendedores(id),
    fecha DATE NOT NULL,
    total REAL NOT NULL
);
CREATE TABLE detalle_pedidos (
    id_pedido INTEGER REFERENCES pedidos(id),
    id_producto INTEGER REFERENCES productos(id),
    cantidad INTEGER NOT NULL,
    precio_unitario REAL NOT NULL,
    PRIMARY KEY(id_pedido, id_producto)
);
