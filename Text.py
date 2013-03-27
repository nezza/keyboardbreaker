import pygame, sys
import random

class Text:
	color = pygame.Color(255, 0, 0)
	speed = 25.0
	x = 0
	y_float = 0.0
	direction = 1.0
	def __init__(self, text, width):
		random.seed()
		self.fontObj = pygame.font.Font('./Ubuntu-L.ttf', 20)
		self._update_text(text)
		self.width = width
		self.set_x(random.randrange(self.width-self.textRect.width))
		self.text_in = text
	def __str__(self):
		return "<Text(%s)>" % self.text_in
	def __unicode__(self):
		return "<Text(%s)>" % self.text_in
	def set_x(self, x):
		self.x = x
		self.textRect.topleft = (
			x,
			self.textRect.topleft[1])


	def _update_text(self, text):
		self.text = text
		self.textBuffer = text
		self.textSurfaceObj = self.fontObj.render(self.text, False, self.color)
		self.textRect = self.textSurfaceObj.get_rect()
		self.textRect.topleft = (self.x, self.y_float)

	def set_color(self, col):
		self.color = col
		self._update_text(self.text)

	def update(self, dt):
		self.y_float += self.speed*dt*self.direction
		self.textRect.topleft = (
			self.textRect.topleft[0],
			int(self.y_float))
	
	def draw(self, surface):
		surface.blit(self.textSurfaceObj, self.textRect)

	def handles_key(self, character):
		if(self.is_over()):
			return False

		if(self.text[0] == character):
			self._update_text(self.text[1:])
			return True
		return False
	
	def is_over(self):
		if(len(self.text) == 0):
			return True
		return False
