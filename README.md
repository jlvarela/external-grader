#external-grader

Para instalar el external grader, es necesario clonar el repositorio:

*git clone https://github.com/morsoinferno/external-grader.git

Sin embargo lo anterior solo copia el repositorio principal, y no los submodulos (codejail). Para lograrlo, es posible usar lo siguiente:

*git clone --recursive https://github.com/morsoinferno/external-grader.git

Para instalar codejail, es necesario instalar apparmor. Para ello se puede seguir la guía de [instalación de codejail](https://github.com/edx/codejail)

Una vez instalado y configurado apparmor, instalamos codejail:

*python setup.py install

El programa debería quedar instalado en:

_/usr/local/lib/python2.7/dist-packages/codejail-0.1-py2.7.egg

Ahora es posible utilizar grade_engine:

*python -m grade_engine

Para indicar la dirección del servidor de xqueue (y la queue particular) hay que crear un archivo de configuración o modificar el archivo json por defecto. grade_engine intentará conectarse a la queue, y si lo logra, lo hará cada un segundo. Si encuentra una tarea que calificar, califica.
