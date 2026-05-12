# ConsultaES

Traductor de lenguaje natural a SQL en español, construido desde formalismos de PLN.

## Descripción

ConsultaES es un sistema de PLN que traduce consultas en lenguaje natural español a sentencias SQL, implementado con autómatas finitos, gramáticas independientes del contexto, y parsing Earley desde cero.

Proyecto universitario: Procesamiento de Lenguaje Natural (Universidad del Valle, 2026-1).

## Instalación y uso

```bash
# Instalar en modo desarrollo
pip install -e ".[dev]"

# Construir la base de datos de prueba
python scripts/build_db.py

# Ejecutar pruebas
pytest

# Lanzar interfaz Streamlit
streamlit run src/consultaES/ui/app.py
```

## Estructura del proyecto

- `src/consultaES/` — módulos del pipeline (tokenizer, lexicon, parser, semantics, sqlgen)
- `data/` — esquema y datos de prueba
- `tests/` — suite de pruebas
- `docs/` — documentación
- `demo/` — ejemplos y demostraciones
- `scripts/` — herramientas de construcción
