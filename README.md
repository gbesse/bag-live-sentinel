# Bag Live Sentinel

## Français

Surveillance en lecture seule de la **progression d’un bag pendant qu’un sujet ROS 2 publie encore**. Un abonné indépendant met à jour un fichier de battement ; le moniteur compare ses changements à l’augmentation de la taille des fichiers MCAP ou SQLite. Il signale un arrêt prolongé de l’écriture uniquement si le sujet continue de publier. L’absence de battement ou une fenêtre trop courte donne `inconclusive`.

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests
```

Sur une machine avec ROS 2 chargé, lancer `bag-live-heartbeat /camera/image_raw sensor_msgs/msg/Image /tmp/robot-bag-topic.heartbeat --locale=fr` pendant l’enregistrement. Copier `fixtures/config.example.json`, adapter les chemins et seuils, puis lancer `bag-live-sentinel config.json --locale=fr`. `bag_glob` peut être `*.mcap` ou `*.db3`. Le délai maximal doit tenir compte de la mise en tampon de l’enregistreur. L’abonné utilise la QoS capteur ROS 2 ; vérifier sa compatibilité avec le sujet. Une croissance du bag peut provenir d’un autre sujet : ce moniteur ne prouve pas que le sujet surveillé y figure. Il ne répare pas le bag et ne garantit pas son intégrité ; compléter par une analyse après enregistrement. Aucun robot n’est commandé.

Codes de sortie : 0 `pass`, 1 `fail`, 2 entrée invalide, 3 `inconclusive`.

## English

Read-only monitor for **bag progress while a ROS 2 topic is still publishing**. An independent subscriber updates a heartbeat file; the monitor compares its changes with growth of MCAP or SQLite files. It flags a sustained writing stall only while the topic remains active. Missing heartbeats or a short window yield `inconclusive`.

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests
```

On a machine with ROS 2 sourced, run `bag-live-heartbeat /camera/image_raw sensor_msgs/msg/Image /tmp/robot-bag-topic.heartbeat --locale=en` while recording. Copy `fixtures/config.example.json`, adjust paths and thresholds, then run `bag-live-sentinel config.json --locale=en`. `bag_glob` can be `*.mcap` or `*.db3`. Set maximum stall time above the recorder’s buffering interval. The subscriber uses ROS 2 sensor QoS; check compatibility with the topic. Bag growth may come from another topic: this monitor does not prove the watched topic is present in the bag. It does not repair the bag or guarantee its integrity; follow with a post-recording audit. It commands no robot.

Exit codes: 0 `pass`, 1 `fail`, 2 invalid input, 3 `inconclusive`.

## Español

Monitor de solo lectura del **avance del bag mientras un tema ROS 2 sigue publicando**. Un suscriptor independiente actualiza un archivo de latido; el monitor compara sus cambios con el crecimiento de archivos MCAP o SQLite. Señala una interrupción prolongada de la escritura solo si el tema sigue activo. Si faltan latidos o la ventana es corta, el resultado es `inconclusive`.

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests
```

En una máquina con ROS 2 configurado, ejecuta `bag-live-heartbeat /camera/image_raw sensor_msgs/msg/Image /tmp/robot-bag-topic.heartbeat --locale=es` durante la grabación. Copia `fixtures/config.example.json`, ajusta rutas y límites y ejecuta `bag-live-sentinel config.json --locale=es`. `bag_glob` puede ser `*.mcap` o `*.db3`. Ajusta el tiempo máximo de inactividad por encima del intervalo de búfer del grabador. El suscriptor usa QoS de sensor ROS 2; comprueba la compatibilidad con el tema. El crecimiento del bag puede proceder de otro tema: este monitor no demuestra que el tema vigilado esté grabado. No repara el bag ni garantiza su integridad; complétalo con una auditoría posterior. No controla ningún robot.

Códigos de salida: 0 `pass`, 1 `fail`, 2 entrada no válida, 3 `inconclusive`.

MIT — [LICENSE](LICENSE).
