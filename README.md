## Información de la materia: ST0263
## Estudiante: Pablo Moreno Quintero | Email: pmorenoq@eafit.edu.co
## Profesor: Ediwn Nelson Montoya Munera | Email: emontoya@eafit.edu.co
# Reto 1: Arquitectura P2P y Comunicación entre procesos.
# 1. Descripción
El propósito de la actividad era crear, describir e implementar una red P2P (Peer to Peer) haciendo uso de diferentes formas de comunicación entre cada peer dentro de la misma red que soporte un sistema de compartición de archivos distribuidos y descentralizados.
## 1.1. Aspectos cumplidos 
+ Aspecto 1
+ Aspecto 2
## 1.2. Aspectos no cumplidos
+ Aspecto no cumplido 1
+ Aspecto no cumplido 2

# 2. Información general de diseño
texto sobre esto

# 3. Ambiente de desarrollo
(para información más detallada revisar: requirements.txt)
+ Lenguaje de programación usado: Python v3.10.12
+ Sistema Operativo: Ubuntu v22.04
### Librerías:
+ Flask v2.0.1
+ grpcio v1.66.1
+ grpcio-tools v1.66.1
+ requests v2.32.3
### Instalación de librerías
```
pip install flask grpcio requests
```
### Estructura de directorios
![image](https://github.com/user-attachments/assets/fdddb6b7-bb3f-4633-b3d6-4d19ee1a4192)

# 4. Configuración de ejecución
Desde la consola ejecutar:
```
python3 peer.py --port <puerto1> --grpc_port <puerto2>
```
