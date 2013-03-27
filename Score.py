import pygame, sys

class Score:
	def __init__(self, position):
		self.color = pygame.Color(255,255,255)
		self.fontObj = pygame.font.Font('./Ubuntu-L.ttf', 30)
		self.score = 0
		self.position = position
		self._update()
	
	def add_points(self, points):
		self.score += points
		self._update()
	
	def _update(self):
		self.text = "Score: %05d" % self.score
		self.textSurfaceObj = self.fontObj.render(self.text, False, self.color)
		self.textRect = self.textSurfaceObj.get_rect()
		self.textRect.topleft = self.position
	
	def draw(self, surface):
		surface.blit(self.textSurfaceObj, self.textRect)
