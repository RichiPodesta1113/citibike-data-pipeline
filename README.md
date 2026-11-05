# Citi Bike Data Pipeline

Pipeline de viajes de bicicletas compartidas de Nueva York para enero de 2024. Python descarga el [archivo oficial](https://s3.amazonaws.com/tripdata/202401-citibike-tripdata.zip) publicado por [Citi Bike](https://citibikenyc.com/system-data). DuckDB carga los CSV y dbt construye las tablas de viajes válidos y actividad. El dashboard HTML muestra conteos, salidas por día y hora y las diez estaciones con más salidas.

El almacenamiento del proyecto es local durante la compilación y el despliegue se realiza en GitHub Pages. El proveedor de datos aloja su archivo original en S3. El proyecto no requiere cuenta ni recursos en AWS.

## Ejecutar

Con Python 3.12, desde la raíz:

```sh
python -m pip install -r requirements.txt
python pipeline.py
```

Abra `site/index.html` en el navegador. Para usar una copia local del archivo, ejecute `python pipeline.py --archive ruta/al/archivo.zip`. Se regeneran la tabla de origen, los modelos y el dashboard en cada ejecución.

Se descartan identificadores vacíos, fechas inválidas, intervalos no positivos y registros duplicados por identificador. Se conservan los viajes válidos sin estación para los conteos generales. Las pruebas de dbt validan unicidad, valores obligatorios, duración positiva y presencia de datos.

## Despliegue

En el repositorio público, seleccione **Settings → Pages → Source → GitHub Actions**. Ejecute **Actions → Build and deploy Citi Bike → Run workflow** para el primer despliegue. Cada cambio en `main` genera una nueva versión. El workflow publica el HTML únicamente cuando la compilación y las pruebas finalizan correctamente.
