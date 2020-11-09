from flask import Flask, render_template, url_for, request, make_response, session, redirect, jsonify
from Datos.usuario import Usuario
from Datos.receta import Receta
from Datos.comentario import Comentario
from os import environ
from datetime import datetime
import json
import base64
import csv
import subprocess
import os

app = Flask(__name__)
app.secret_key = 'macfffgdgma'

master=Usuario("admin", "Usuario", "Maestro", "admin")

usuarios=[master]
recetas=[]



def validar_login(user, contrasena):
    for usuario in usuarios:
        if usuario.user == user and usuario.contrasena == contrasena:
            return usuario
    return None

def buscar_receta(titulo):
    print('aaaaaaaaa')
    for receta in recetas:
        if receta.titulo == titulo:
            print(receta.ingredientes)
            return receta
    return None   
    
def crear_usuario(user, nombre, apeliido, contrasena):
    usuarios.append(Usuario(user, nombre, apeliido, contrasena))

def registar_receta(autor, titulo, resumen, ingredientes, preparacion, tiempo, imagen):
    recetas.append(Receta(autor, titulo, resumen, ingredientes, preparacion, tiempo, imagen))


@app.route('/home/usuario')
def usuario_home():
    if 'usuario_logeado' in session:
        return render_template('homeUsuario.html',usuario=session['usuario_logeado'], recetas=recetas)
    else:
        return redirect(url_for('home'))


@app.route('/login', methods=["GET","POST"])
def login():
    error=None
    if  request.method == "POST":
      
      req= request.form
      user =req.get("usuario")
      contraseña= req.get("contrasena")

      usuario = validar_login(user, contraseña)
      
      if usuario!=None:
              session['usuario_logeado']=usuario.nombre
              return redirect(url_for('usuario_home'))
      else:
          error='invalido'
          return render_template('login.html', error=error)  
    if 'usuario_logeado' in session:
        return redirect(url_for('usuario_home'))  
    return render_template('login.html',error=None)


@app.route('/registro',methods=["GET","POST"])
def registro():
    if  request.method == "POST":
     
      req= request.form
      user =req.get("usuario")
      contrasena= req.get("contrasena")
      confrimacion = req.get("confirmarContrasena")
      nombre = req.get("nombre")
      apellido = req.get("apellido")

      crear_usuario(user,nombre,apellido,contrasena)
      if contrasena == confrimacion:
              return render_template('login.html')
      else:
            return render_template('crearCuenta.html')

    
    return render_template("crearCuenta.html")

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('usuario_logeado', None)
    return redirect(url_for('home'))

@app.route('/registroReceta',methods=["GET","POST"])
def registrarReceta():
    if  request.method == "POST":
     
      req= request.form
      titulo =req.get("titulo")
      resumen= req.get("resumen")
      ingredientes = req.get("ingredientes")
      preparacion = req.get("preparacion")
      tiempo = req.get("tiempo")
      imagen = req.get("imagen")
      autor = session['usuario_logeado']
      registar_receta(autor, titulo, resumen, ingredientes, preparacion, tiempo, imagen)
      return redirect(url_for('usuario_home'))  
    return render_template('registroRecetas.html')

@app.route('/cargarArchivo', methods=['POST'])
def agregarRecetas():
    datos = request.get_json()

    if datos['data'] == '':
        return {"msg": 'Error en contenido'}

    contenido = base64.b64decode(datos['data']).decode('utf-8')

    filas = contenido.splitlines()
    reader = csv.reader(filas, delimiter=',')
    for row in reader:
        receta = Receta(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        recetas.append(receta)

    return {"msg": 'Receta agregada'}

@app.route('/receta/<titulo>', methods=['POST','GET'])
def mostrar_receta(titulo):
    tamaño=0
    receta = buscar_receta(titulo)
    tamaño = len(receta.comentarios)
    if  request.method == "POST":
     
      req= request.form
      contenido =req.get("comentario")
      now = datetime.now()
      fecha = now.strftime("%m-%d-%Y, %H:%M:%S")
      comentario= Comentario(session['usuario_logeado'],contenido,fecha)
      

      receta.comentarios.append(comentario)
      tamaño = len(receta.comentarios)
      return render_template('receta.html', usuario=session['usuario_logeado'], receta= receta, tamaño=tamaño)  
    return render_template('receta.html', usuario=session['usuario_logeado'], receta= receta, tamaño=tamaño)

    

@app.route('/home')
def  home():
    return render_template('home.html', recetas=recetas)

if __name__ =='__main__':
    app.run(debug=True)