# Sistema de Información para Finanzas Personales

---

## Resumen del Proyecto

Este proyecto se desarrolló para crear una solución integral que permita a cualquier persona **gestionar y visualizar sus finanzas personales**. El objetivo principal fue construir un sistema de datos robusto que va desde la entrada de registros hasta la creación de un dashboard interactivo, facilitando la toma de decisiones financieras informadas.

---

## Desafíos y Soluciones

El núcleo de este proyecto fue el desarrollo de un pipeline de datos completo, demostrando las siguientes habilidades clave:

* **Diseño de Data Warehouse:** Se diseñó y construyó un **modelo de estrella** en **SQL Server Express** para optimizar el análisis de datos. Este esquema de datos separa la información transaccional de los atributos descriptivos, permitiendo consultas rápidas y análisis complejos en Power BI.

* **Aplicación de Escritorio Interactiva:** Se desarrolló un formulario de entrada de datos con **Python y CustomTkinter** para automatizar el registro de transacciones. Esta solución de escritorio es intuitiva y garantiza la integridad de los datos, ya que valida y crea nuevos registros en el Data Warehouse de manera dinámica.

* **Análisis con Power BI:** Se desarrollaron métricas clave **(KPIs)** y visualizaciones interactivas para explorar el conjunto de datos y presentar los hallazgos de forma clara, permitiendo la toma de decisiones informadas.

---

## Análisis Financiero y Dashboard

El análisis culminó en un dashboard en Power BI que sirve como una herramienta para explorar y entender las finanzas personales.

**Explora el dashboard aquí:** [Análisis de Finanzas Personales en Power BI](https://app.powerbi.com/view?r=eyJrIjoiMGFjYmE4MjQtNmQ2Yy00ODUyLWFiY2EtOWM1MTBkMGYxZmE4IiwidCI6ImRmNGI2MzcyLWEwM2EtNDZmMC05YmY1LTdmOGQzNzhhMzMzNCIsImMiOjR9)

**Hallazgos Principales:**

* **Saldos y Rendimiento:** El dashboard compara el **Saldo Actual** (el estado final de las cuentas) con el **Saldo Neto** (el rendimiento total del período), lo que permite entender la salud financiera.
* **Gasto Promedio:** Se pueden visualizar métricas clave como el gasto promedio por transacción, persona y categoría.
* **Tendencia y Distribución:** Se creó un gráfico que muestra la evolución de ingresos y gastos a lo largo del tiempo y un desglose de los gastos en categorías fijas y variables.

---

## Tecnologías y Código

* **Herramientas:** **Python, CustomTkinter, SQL Server Express, Power BI.**
* **Código:** El código utilizado para la gestión de datos, el formulario y la generación de datos está disponible en este repositorio.
