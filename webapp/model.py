#! /usr/bin/env/python3

from webapp import db


class Image_Base(db.Model):

	__tablename__='Images'

	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(64))
	image_name = db.Column(db.String(64))
	image = db.Column(db.Text)
	width = db.Column(db.Integer)
	height = db.Column(db.Integer)
	color = db.Column(db.Integer)

	def __init__(self,username,name,image,w,h,c):
		self.image_name=name
		self.username=username
		self.image=image
		self.width=w
		self.height=h
		self.color=c

class Audio_Base(db.Model):

	__tablename__='audio'

	id = db.Column(db.Integer,primary_key=True,autoincrement=True)
	username = db.Column(db.String(64))
	name = db.Column(db.String(64))
	uname = db.Column(db.String(32),unique=True)


	def __init__(self,username,name,uname):
		self.name=name
		self.username=username
		self.uname = uname
