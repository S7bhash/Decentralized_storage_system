from flask import render_template,url_for,flash,redirect,request,Blueprint,current_app
from flask_login import login_user, current_user, logout_user , login_required
from webapp import db
from webapp.model import Image_Base,Audio_Base
from flask_wtf.file import FileField
import os
from webapp.image_processing import *
from webapp.wlan_security import sniff
from webapp.forms import Upload
import numpy as np
import base64
from PIL import Image
from webapp.tunnel import reliable_recv,reliable_send,server
import json
from webapp.client import client
import socket
from .audio_processing import *
from PIL import Image
from .audio_processing import split_audio
from .ip_sorter import ip_sorted
from pydub import AudioSegment
import random,string

users = Blueprint('users',__name__)

@users.route("/",methods=['GET'])
def init():
	return render_template("redirecter.html")

@users.route("/home",methods=['GET','POST'])
def index():
	conn ,addr = server()
	data=reliable_recv(conn)
	print(data['name'])
	if data['name'].split('.')[-1]!='mp3':
		if data['command']!="send":
			shape = data["shape"]
			image = Image_Base(username="S7bhash",name=data["name"],image=data["image"],w=shape[0],h=shape[1],c=shape[2])
			db.session.add(image)
			db.session.commit()
			return redirect(url_for('users.uploaded'))
		else:
			image = Image_Base.query.filter_by(image_name=data['name'])
			dict = {"image":image}
			reliable_send(data['ip'],dict)
			return redirect(url_for('users.init'))
	else:
		if data['command']!="send":
			rand = ''.join([random.choice(string.ascii_letters) for i in range(32)])
			filename  = rand+'.mp3'
			filepath = os.path.join(current_app.root_path,'static/music',filename)
			data['image'].export(filepath,format="mp3")
			audio = Audio_Base(username="S7bhash",name=data["name"],image=filepath)
			db.session.add(audio)
			db.session.commit()
			return redirect(url_for('users.uploaded'))
		else:
			audio = Audio_Base.query.filter_by(uname=data['name'])
			sound = AudioSegment.from_mp3(audio.uname)
			dict = {"audio":sound}
			reliable_send(data['ip'],dict)
			return redirect(url_for('users.init'))


	return render_template('welcome.html')

import requests
@users.route('/files',methods=['GET','POST'])
def files():
	files = Image_Base.query.filter_by(username="S7bhash")
	return render_template('files_list.html',results=files)

@users.route('/audio',methods=['GET'])
def audio():
	r = requests.get("http://192.168.43.238/Shape_Of_You.mp3")
	f = open('shape_of_you.mp3','wb')
	f.write(r.content)
	return "GOT MUSIC"

@users.route('/upload',methods = ['GET','POST'])
def upload():
	upload = Upload()
	hostnames = ["192.168.43.238","192.168.43.237","192.168.43.114","192.168.43.185"]
	if upload.validate_on_submit():
		if upload.file.data:
			if upload.file.data.filename.split('.')[-1]!='mp3':
				peer_images = crop_image(upload.file.data)
				i=0
				for ip in hostnames:
					if ip != "192.168.43.238":
						print(ip)
						image_data=peer_images[i]
						shape = image_data.shape
						command="scjhhsacjbds"
						dict = {'name':upload.name.data,"command":command,"image":image_data,"shape":shape}
						reliable_send(ip,dict)
					else:
						image_data = peer_images[i]
						shape = image_data.shape
						image = Image_Base(name=upload.name.data,username="S7bhash",image=image_data,w=shape[0],h=shape[1],c=shape[2])
						db.session.add(image)
						db.session.commit()
					i+=1
				return redirect(url_for('users.shower'))
			else:
				peer_audio = split_audio(upload.file.data)
				i=0
				for ip in hostnames:
					print(ip)
					if ip != "192.168.43.238":
						#image_data = img2arr(peer_images[i])
						command="scjhhsacjbds"
						dict = {'name':upload.name.data,"command":command,"image":peer_audio[i]}
						reliable_send(ip,dict)
					else:
						rand = ''.join([random.choice(string.ascii_letters) for i in range(32)])
						filename  = rand+'.mp3'
						filepath = os.path.join(current_app.root_path,'static/music',filename)
						peer_audio[i].export(filepath,format="mp3")
						image = Audio_Base(username = "S7bhash",name=upload.name.data,uname=filepath)
						db.session.add(image)
						db.session.commit()
					i+=1
				return redirect(url_for('users.shower'))

	return render_template('image_upload.html',upload=upload)

@users.route('/uploaded',methods=['GET','POST'])
def uploaded():
	return "<h1>Uploaded</h1>"

@users.route('/signup',methods=['GET','POST'])
def signup():
	form = SignUp()
	if form.validate_on_submit():
		f = open('data.txt','w+')
		f.writelines(form.email.data)
		f.writeline("\n")
		f.writeline(form.username.data)
		f.writeline(form.password.data)
		return redirect(url_for('users.home'))
	return render_template('signup.html')


@users.route('/image/<name>',methods=['GET'])
def image(name):
	hostnames = ["192.168.43.238","192.168.43.237","192.168.43.114","192.168.43.185"]
	i=0
	images = []
	width=0
	height=0
	for ip in hostnames:
		if ip != "192.168.43.238":
			print(ip)
			command="send"
			dict = {'name':name,"command":"send",'ip':"192.168.43.238"}
			reliable_send(ip,dict)
			conn,addr = server()
			data=reliable_recv(conn)
			data['image']
			img = arr2img(data['image'],data['width'],data['height'],data['color'],data['image_name'])
			width+=data['width']
			height=data['height']
			images.append(img)
			img.show()

		else:
			image = Image_Base.query.filter_by(image_name=name).first()
			img = arr2img(image.image,image.width,image.height,image.color,image.image_name)
			width+=image.width
			height=image.height
			images.append(img)
			img.show()
		i+=1
	final_image = join_image(images,1920,1080)
	final_image.show()

	return redirect(url_for('users.files'))
@users.route('/show',methods=['GET','POST'])
def shower():
	image = Image_Base.query.filter_by(image_name='final-test-01').first()
	img = arr2img(image.image,image.width,image.height,image.color,image.image_name)
	w=img.width * 2
	h = img.height * 2
	print(w,h)
	images = [img,img,img,img]
	final_image = join_image(images,w,h)
	final_image.show()
	return "<h1>nothing</h1>"
