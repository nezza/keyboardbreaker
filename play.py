#!/usr/bin/env python

import pygame, sys
import random
from pygame.locals import *
import socket, select
import json

from Text import Text
from Score import Score

import Words

VERSION = "0.0.1"
WIDTH = 1280
HEIGHT = 800

PORT = 50008              # Arbitrary non-privileged port


speed = HEIGHT/25
GO = False
pygame.init()
random.seed()

time_in = 0.0
shooted_objects = 0

active_go = None
active_so = None

gameobjects = []
shootingobjects = []
data_in = None

fpsClock = pygame.time.Clock()

windowsSurfaceObj = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('keyboardbreaker ' + VERSION)

mousex, mousey  = 0, 0

blackColor = pygame.Color(0, 0, 0)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = None

score_me = Score((0,5))
score_op = Score((800, 5))

def send_data(data):
	conn.sendall(data + "\n")


if(sys.argv[1] == "listen"):
	HOST = ''                 # Symbolic name meaning all available interfaces
	PORT = int(sys.argv[2])
	s.bind((HOST, PORT))
	s.listen(1)
	conn, addr = s.accept()
	conn.setblocking(0)
	print 'Connected by', addr
	msg = json.dumps({"type": "go"})
	GO = True
	send_data(msg)
elif(sys.argv[1] == "connect"):
	HOST = sys.argv[2]
	PORT = int(sys.argv[3])
	s.connect((HOST, PORT))
	s.setblocking(0)
	print "Connected!"
	conn = s
else:
	print "Either listen or connect!"
	sys.exit(0)

def send_data(data):
	conn.sendall(data + "\n")

def data_available():
	global data_in
	data = None
	data_in = []
	try:
		data = conn.recv(1024)
	except:
		return False
	if data:
		#print "----DATA----"
		#print data
		#print "----JSON----"
		for line in data.split("\n"):
			if(len(line) > 0):
				data_in.append(json.loads(line))
		#print data_in
		#print "----DONE----"
		return True
	return False

def get_word():
	return Words.WORDS_10[random.randrange(Words.WORDS_10_LEN-1)]

def is_word_available(word):
	for so in shootingobjects:
		if so.text == word:
			return False
	return True

def get_word_index(listx, word):
	for idx, val in enumerate(listx):
		if(val.text_in == word):
			return idx
	return None

def delete_word(listx, word):
	idx = get_word_index(listx, word)
	if idx != None:
		listx.pop(idx)
	else:
		print "Tried to unsuccesful remove " + word

def create_shooted():
	word = get_word()
	while not is_word_available(word):
		word = get_word()
	
	ob = Text(word, WIDTH)
	ob.speed = speed
	ob.direction = -1.0
	ob.y_float = HEIGHT
	shootingobjects.append(ob)
	send_bullet = {"type": "bullet", "word": word}
	print "shooting %s" % word
	send_data(json.dumps(send_bullet))


def destroyed_word():
	print "SCORE"
	score_me.add_points(50)
	send_score = {"type": "score", "points": 50}
	send_data(json.dumps(send_score))
	create_shooted()

def handle_key(key):
	global active_go

	word = None
	send_key = {"type": "key", "key": key}
	send_data(json.dumps(send_key))

	if active_go:
		if not (active_go.handles_key(key)):
			# TODO: Error pling or sth
			pass

		if(active_go.is_over()):
			delete_word(gameobjects, active_go.text_in)
			send_destroy = {"type": "destroy", "word": active_go.text_in}
			send_data(json.dumps(send_destroy))
			active_go = None
			destroyed_word()
			return

	if not active_go:
		for go in gameobjects:
			if(go.handles_key(key)):
				active_go = go
				active_go.set_color(pygame.Color(0, 255, 0))
				active_go.draw(windowsSurfaceObj)
				break;

def handle_opponent_key(key):
	global active_so

	if active_so:
		if not (active_so.handles_key(key)):
			pass
		if(active_so.is_over()):
			delete_word(shootingobjects, active_so.text_in)
			active_so = None
			return
	if not active_so:
		for so in shootingobjects:
			if(so.handles_key(key)):
				active_so = so
				active_so.set_color(pygame.Color(0,0,255))
				active_so.draw(windowsSurfaceObj)
				break


	
while True:
	windowsSurfaceObj.fill(blackColor)

	dt = 1.0/float(fpsClock.tick(30))

	if GO:
		time_in += dt
		if(time_in > 1.0):
			if(shooted_objects < 5):
				time_in -= 1.0
				shooted_objects += 1
				create_shooted()

	if(data_available()):
		for data in data_in:
			if(data["type"] == "key"):
				handle_opponent_key(data["key"])
			elif(data["type"] == "bullet"):
				ob = Text(data["word"], WIDTH)
				ob.speed = speed
				gameobjects.append(ob)
			elif(data["type"] == "score"):
				score_op.add_points(data["points"])
			elif(data["type"] == "destroy"):
				delete_word(shootingobjects, data["word"])
			elif(data["type"] == "go"):
				GO = True
				create_shooted()
			print "DATA"

	score_me.draw(windowsSurfaceObj)
	score_op.draw(windowsSurfaceObj)

	for go in gameobjects:
		go.update(dt)
		go.draw(windowsSurfaceObj)
		if(go.y_float >= HEIGHT):
			if(active_go == go):
				active_go = None
			delete_word(gameobjects, go.text_in)
			score_me.add_points(-100)
			send_destroy = {"type": "destroy", "word": go.text_in}
			send_data(json.dumps(send_destroy))
			send_score = {"type": "score", "points": -100}
			send_data(json.dumps(send_score))

	for so in shootingobjects:
		so.update(dt)
		so.draw(windowsSurfaceObj)

	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()

		elif event.type == KEYDOWN:
			key_in = event.key
			if((key_in >= ord('a')) and (key_in <= ord('z'))):
				handle_key(chr(event.key))
			else:
				print "NOT COOL"

	pygame.display.update()
