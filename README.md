# Tren-ES

**Sistema de Integración de Información Ferroviaria Española**

Tren-ES es un proyecto de integración de datos diseñado para mejorar la consulta de información sobre la red de ferrocarriles de España. El sistema actúa como un mediador que unifica datos heterogéneos, permitiendo realizar consultas complejas sobre estaciones, horarios, infraestructura y demografía sin preocuparse por la fuente original.

## 📦 Fuentes de Datos Integradas

El sistema integra y normaliza información de diversas fuentes:

*   **Renfe:** Horarios, trayectos y operación de trenes.
*   **Adif:** Infraestructura ferroviaria, estaciones y líneas.
*   **Wikidata:** Datos enriquecidos sobre estaciones y localizaciones geográficas.
*   **INE (Instituto Nacional de Estadística):** Datos demográficos de las poblaciones conectadas.

## 🛠️ Arquitectura

El proyecto implementa una arquitectura de integración basada en un **Esquema Mediador**, resolviendo conflictos semánticos y estructurales entre las fuentes. La documentación incluye:

*   **Esquema Global:** La visión unificada del dominio ferroviario.
*   **Mapeos GAV (Global-As-View) y LAV (Local-As-View):** Definiciones formales de cómo se relacionan las fuentes con el mediador.
*   **Reformulación de Consultas:** Estrategias para traducir consultas del usuario a las fuentes originales.

## 📂 Estructura del Repositorio

*   `EsquemaMediador.md`: Definición del esquema global.
*   `EsquemasOrigen.md`: Documentación de los esquemas de las fuentes nativas.
*   `EsquemasGAV.md` / `EsquemasLAV.md`: Especificación de los mapeos de integración.
*   `scripts/`: Scripts SQL y Python para la carga y mediación de datos. Actualmente un mero prototipo y demo para mostrar los objetivos.

