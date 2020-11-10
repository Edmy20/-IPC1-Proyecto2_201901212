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
    for receta in recetas:
        if receta.titulo == titulo:
            return receta
    return None

def buscar_usuario():
    print('e')
    for user in usuarios:
        if user.nombre == session['usuario_logeado']:
            print('2')
            return user
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

@app.route('/perfil/<usuario>',methods=["GET","POST"])
def perfil(usuario):
    user= buscar_usuario()
    if  request.method == "POST":
      id= usuarios.index(user)
     
      req= request.form
      user2 =req.get("usuario")
      contrasena= req.get("contrasena")
      nombre = req.get("nombre")
      apellido = req.get("apellido")

      user_temp = Usuario(user2,nombre,apellido,contrasena)
      usuarios[id]=user_temp

      session['usuario_logeado']=usuarios[id].nombre
      return render_template('perfil.html', user = usuarios[id], recetas = recetas)

    return render_template('perfil.html', user=user, recetas= recetas)


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

@app.route('/eliminar/<titulo>')
def eliminar_receta(titulo):
    receta = buscar_receta(titulo)
    recetas.remove(receta)
    return redirect(url_for('perfil', usuario=session['usuario_logeado']))

@app.route('/comentarios/<titulo>')
def tabla_comentarios(titulo):
    receta = buscar_receta(titulo)
    return render_template('tablaCom.html', receta=receta, usuario=session['usuario_logeado'])

@app.route('/modificar/<titulo>',methods=["GET","POST"])
def modificar(titulo):
    receta = buscar_receta(titulo)
    if  request.method == "POST":
      id= recetas.index(receta)
     
      req= request.form
      titulo =req.get("titulo")
      resumen= req.get("resumen")
      ingredientes = req.get("ingredientes")
      preparacion = req.get("preparacion")
      tiempo = req.get("tiempo")
      imagen = req.get("imagen")
      autor = session['usuario_logeado']
      rec_temp = Receta(autor, titulo, resumen, ingredientes, preparacion, tiempo, imagen)
      recetas[id]=rec_temp
      return redirect(url_for('usuario_home'))  
    return render_template('modificar.html',receta=receta)

@app.route('/home')
def  home():
    return render_template('home.html', recetas=recetas)

if __name__ =='__main__':
    app.run(threaded=True, host="0.0.0.0", port=5000, debug=True)