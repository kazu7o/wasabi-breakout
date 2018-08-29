# -*- coding:utf-8 -*-
import pygame
from pygame.locals import *
import sys
import math
import re

SCREEN = Rect(0,0,400,400)

#スプライトクラス(pygame.sprite.Spriteを継承)
class Paddle(pygame.sprite.Sprite):
	#スプライトを作成(画像ファイル名, 位置(x，y), 速さ(vx,vy),回転angle)
	def __init__(self, filename):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = pygame.image.load(filename).convert_alpha()
		self.rect = self.image.get_rect()
		self.rect.bottom = SCREEN.bottom - 20
		self.rect.centerx = SCREEN.width / 2

	def update(self):
		#self.rect.centerx = pygame.mouse.get_pos()[0]
		key_pressed = pygame.key.get_pressed()
		if key_pressed[K_LEFT]:
			self.rect.left -= 7
		if key_pressed[K_RIGHT]:
			self.rect.right += 7
		self.rect.clamp_ip(SCREEN)

class Block(pygame.sprite.Sprite):
	def __init__(self, filename, x, y):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = pygame.image.load(filename).convert()
		self.rect = self.image.get_rect()
		self.rect.left = SCREEN.left + x * self.rect.width
		self.rect.top = SCREEN.top + y * self.rect.height

class Ball(pygame.sprite.Sprite):
	speed = 5
	angle_left = 135
	angle_right = 45

	def __init__(self, filename, paddle, blocks):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = pygame.image.load(filename).convert_alpha()
		self.rect = self.image.get_rect()
		self.hassya_sound = pygame.mixer.Sound("./sound/hassya.ogg")
		self.break_sound = pygame.mixer.Sound("./sound/break.ogg")
		self.wall_sound = pygame.mixer.Sound("./sound/wall.ogg")
		self.dx = self.dy = 0	# ボールの速度
		self.paddle = paddle 	# パドルへの参照
		self.blocks = blocks	# ブロックグループへの参照
		self.update = self.start
		self.hit = 0			#　連続でブロックを壊した回数

	def start(self):
		# ボールの初期位置（パドルの上）
		self.rect.centerx = self.paddle.rect.centerx
		self.rect.bottom = self.paddle.rect.top
		# スペースでボール射出
		if pygame.key.get_pressed()[K_SPACE]:
			self.dx = 0
			self.dy = -self.speed
			self.update = self.move
			self.hassya_sound.play()
	def move(self):
		self.rect.centerx += self.dx
		self.rect.centery += self.dy
		# 壁との反射
		if self.rect.left < SCREEN.left:
			self.rect.left = SCREEN.left
			self.dx = -self.dx					# 速度を反転
			self.wall_sound.play()
		if self.rect.right > SCREEN.right:
			self.rect.right = SCREEN.right
			self.dx = -self.dx
			self.wall_sound.play()
		if self.rect.top < SCREEN.top:
			self.rect.top = SCREEN.top
			self.dy = -self.dy
			self.wall_sound.play()
		if self.rect.bottom > SCREEN.bottom:
			self.rect.bottom = SCREEN.bottom
			self.dy = -self.dy
			self.wall_sound.play()
		# パドルとの反射(左端：135度方向, 右端:45度方向, それ以外：線形補間)
		if self.rect.colliderect(self.paddle.rect) and self.dy > 0:
			#self.hit = 0								# 連続ヒットをゼロに戻す
			(x1, y1) = (self.paddle.rect.left - self.rect.width, self.angle_left)
			(x2, y2) = (self.paddle.rect.right, self.angle_right)
			x = self.rect.left								# ボールが当たった位置
			y = (float(y2 - y1)/(x2 - x1) * (x - x1) + y1)	# 線形補間
			angle = math.radians(y)							# 反射角度
			self.dx = self.speed * math.cos(angle)
			self.dy = -self.speed * math.sin(angle)
			self.wall_sound.play()
		# ボールを落とした場合
		if self.rect.bottom >= SCREEN.bottom:
			self.update = self.start						# ボールを初期位置に戻す
			self.hit = 0

		# ボールと衝突したブロックリストを取得
		blocks_collided = pygame.sprite.spritecollide(self, self.blocks, True)
		if blocks_collided:		# 衝突ブロックがある場合
			oldrect = self.rect
			for block in blocks_collided:
				# ボールが左から衝突
				if oldrect.left < block.rect.left < oldrect.right < block.rect.right:
					self.rect.right = block.rect.left
					self.dx = -self.dx
					self.break_sound.play()
				# ボールが右から衝突
				if block.rect.left < oldrect.left < block.rect.right < oldrect.right:
					self.rect.left = block.rect.right
					self.dx = -self.dx
					self.break_sound.play()
				# ボールが上から衝突
				if oldrect.top < block.rect.top < oldrect.bottom < block.rect.bottom:
					self.rect.bottom = block.rect.top
					self.dy = -self.dy
					self.break_sound.play()
				# ボールが下から衝突
				if block.rect.top < oldrect.top < block.rect.bottom < oldrect.bottom:
					self.rect.top = block.rect.bottom
					self.dy = -self.dy
					self.break_sound.play()
				self.hit += 1

# メイン
def main():
	pygame.init()
	pygame.mixer.init()
	screen = pygame.display.set_mode(SCREEN.size)
	pygame.display.set_icon(pygame.image.load("./image/icon.png").convert_alpha())
	pygame.display.set_caption("ブロック崩し")
	font = pygame.font.SysFont("Arial", 13, bold=True)
	group = pygame.sprite.RenderUpdates()	# 描画用のスプライトグループ
	blocks = pygame.sprite.Group()	# 衝突判定用のスプライトグループ
	Paddle.containers = group
	Ball.containers = group
	Block.containers = group, blocks
	# パドルを作成
	paddle = Paddle("./image/wasabi.jpg")
	# ブロックの作成（14 * 10）
	for x in range(1, 14):
		for y in range(1, 11):
			Block("./image/block.png", x, y)
	# ボールの作成
	ball = Ball("./image/ball.png", paddle, blocks)

	# マウス位置・非表示
	pygame.mouse.set_pos([320,paddle.rect.bottom])
	pygame.mouse.set_visible(False)
	# FPS
	clock = pygame.time.Clock()

	while(1):
		clock.tick(60) #　フレームレート(60fps)
		screen.fill((0, 20, 0, 0))
		text = font.render("SCORE : " + str(ball.hit), True, (243,213,26))
		screen.blit(text, [0, 0])
		# スプライトグループを更新
		group.update()
		# スプライトグループを描画
		group.draw(screen)
		# 画面更新
		pygame.display.update()
		if len(blocks) == 0:
			pygame.quit()
			sys.exit()
		# イベント処理
		for event in pygame.event.get():
			# 終了用のイベント処理
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()

if __name__ == "__main__":
	main()
