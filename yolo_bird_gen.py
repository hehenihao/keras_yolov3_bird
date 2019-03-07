import pygame                   # 导入pygame库
from pygame.locals import *     # 导入pygame库中的一些常量
from sys import exit            # 导入sys库中的exit函数
import os
import random
import math
import xml.etree.ElementTree as ET
from xml.dom import minidom
import shutil


os.chdir(os.path.abspath(os.path.dirname(__file__)))

# 定义窗口的分辨率
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 416
# 一个程序运行周期可以生成的数据量
SHOOTS = 180
# 是否生成带有标注框的图片，设为True会在AnnPics文件夹下生成带有标注框的图片
ANNOTATION_PIC = True
# 截图间隔，调节此选项来改变截图的时间间隔
INTERVAL = 20

if os.path.exists('JPGs'):
    shutil.rmtree('JPGs')
os.mkdir('JPGs')
if os.path.exists('AnnPics'):
    shutil.rmtree('AnnPics')
os.mkdir('AnnPics')
if os.path.exists('Annotations'):
    shutil.rmtree('Annotations')
os.mkdir('Annotations')

ticks = 0
offset = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0,
          pygame.K_UP: 0, pygame.K_DOWN: 0}
score = 0
gameStart = False
gameOver = False

# 初始化游戏
pygame.init()                   # 初始化pygame
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])     # 初始化窗口
pygame.display.set_caption('FlapPY Bird')       # 设置窗口标题

# 载入图片
bg_sky = pygame.image.load('src/bg_day.png')

# birds
yellow2 = pygame.image.load('src/bird0_1.png')
yellow1 = pygame.image.load('src/bird0_2.png')
yellow0 = pygame.image.load('src/bird0_0.png')
blue2 = pygame.image.load('src/bird1_1.png')
blue1 = pygame.image.load('src/bird1_2.png')
blue0 = pygame.image.load('src/bird1_0.png')
red2 = pygame.image.load('src/bird2_1.png')
red1 = pygame.image.load('src/bird2_2.png')
red0 = pygame.image.load('src/bird2_0.png')
# pipes
upPipe = pygame.image.load('src/pipe_up.png')
downPipe = pygame.image.load('src/pipe_down.png')
# btns
ready_pic = pygame.image.load('src/text_ready.png')
title_pic = pygame.image.load('src/title.png')
over_pic = pygame.image.load('src/text_game_over.png')
# score
score_pic = []
for i in range(10):
    score_pic.append(pygame.image.load('src/number_score_0{0}.png'.format(i)))

delta_x = 3
pipe_gap = 110
pipe_speed = 0.5

yellow = [yellow0, yellow1, yellow2]
red = [red0, red1, red2]
blue = [blue0, blue1, blue2]
kindOfBird = [yellow, red, blue]
num = []

pipes = pygame.sprite.Group()
birds = pygame.sprite.Group()
clock = pygame.time.Clock()
flappyBird = None


class BackgroundImg():
    def __init__(self, screen, img, x: float, y: float, delta_x: float, delta_y=0.):
        '''背景类初始化定义
        
        Arguments:
            screen {pygame window} -- 绘制背景图片的pygame窗口
            img {img} -- 背景图片
            x {float} -- position x
            y {float} -- position y
            delta_x {float} -- 背景图片x方向移动速度
        
        Keyword Arguments:
            delta_y {float} -- 背景图片y方向移动速度 (default: {0})
        '''

        self.screen = screen
        self.img = img
        self.x = x
        self.y = y
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.offset_x = 0

    def draw(self):
        if self.offset_x > self.x:
            self.offset_x = 0
        else:
            self.offset_x += self.delta_x
        self.screen.blit(self.img, (0.-self.offset_x, self.y))
        self.screen.blit(self.img, (self.x-self.offset_x, self.y))


class Score():
    def __init__(self, screen, x, y):
        '''分数初始化
        
        Arguments:
            x {float} -- 分数最右端位置
            y {float} -- 分数顶端位置
        '''

        self.screen = screen
        self.x = x
        self.y = y
        self.score = 0

    def draw(self):
        nums = list(str(self.score))
        cnt = len(nums)
        for i in range(cnt-1, -1, -1):
            img = score_pic[int(nums[i])]
            self.screen.blit(img, (self.x-(cnt-i)*16, self.y))


class Bird(pygame.sprite.Sprite):
    def __init__(self, imgs: list, x: float, y: float, speed_x=0, rotate=0):
        super().__init__()
        self.imgs = imgs
        self.image = self.imgs[0]
        self.current = 0
        self.speed = speed_x
        self.drop = 0
        self.rect = self.imgs[0].get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rotate = rotate
        self.degree = 0
        self.alive = True
        self.birdUp = False  # 鸟往上飞
        self.tick = 0  # 更换鸟图片计时器

    def update(self):
        if self.alive:
            self.tick += 1
            if self.tick > 10:
                self.tick = 0
                self.current += 1
                if self.current > 2:
                    self.current = 0
            self.image = self.imgs[self.current]
            self.rect.x += self.speed
            if not self.birdUp:
                self.drop += 0.15
                if self.drop > 10:
                    self.drop = 10
                if self.degree < -90:
                    self.degree = -90
                self.rect.y += self.drop
                self.degree -= self.rotate
                # self.degree = 60
            else:
                self.drop = -2.5
                self.rect.y += self.drop
                self.degree = 30
            self.image = pygame.transform.rotate(self.image, self.degree)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, img, x: float, y: float, speed=0, pass_x=0):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.passed = False
        self.pass_x = pass_x
        self.counted = False

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < self.pass_x:
            self.passed = True


class Button(pygame.sprite.Sprite):
    def __init__(self, img, x: float, y: float, speed=0):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def PipePair(x=0, up_y=0, gap=100, speed=0, pass_x=150):
    up = Pipe(upPipe, x, up_y, speed, pass_x)
    down = Pipe(downPipe, x, up_y-320-gap, speed, pass_x)
    return up, down


def InitNewBird():
    global flappyBird
    if flappyBird is None:
        birdimg = random.randint(0, 2)
        flappyBird = Bird(kindOfBird[birdimg], 70, 100, 0, 1)

def writeXml(filename, birds, pipes):
    root = ET.Element('annotation')
    foldernode = ET.SubElement(root, 'folder')
    foldernode.text = 'birds'
    filenode = ET.SubElement(root, 'filename')
    filenode.text = filename
    sizenode = ET.SubElement(root, 'size')
    widthnode = ET.SubElement(sizenode, 'width')
    widthnode.text = '288'
    heightnode = ET.SubElement(sizenode, 'height')
    heightnode.text = '512'
    depthnode = ET.SubElement(sizenode, 'depth')
    depthnode.text = '3'
    segmentednode = ET.SubElement(root, 'segmented')
    segmentednode.text = '0'
    for _b in birds:
        addObj(root, 'bird', _b)
    for _p in pipes:
        addObj(root, 'pipe', _p)
    
    # tree = ET.ElementTree(root)
    # tree.write('Annotation\\'+filename+'.xml')
    xml_string = ET.tostring(root)
    xml_write = minidom.parseString(xml_string)
    with open('Annotations\\'+filename+'.xml', 'w') as handle:
        xml_write.writexml(handle, indent='', addindent='\t', newl='\n', encoding='utf-8')

def addObj(rootnode, classname, data):
    objdnode = ET.SubElement(rootnode, 'object')
    namenode = ET.SubElement(objdnode, 'name')
    namenode.text = classname
    posenode = ET.SubElement(objdnode, 'pose')
    posenode.text = 'Left'
    truncatednode = ET.SubElement(objdnode, 'truncated')
    truncatednode.text = '0'
    difficultnode = ET.SubElement(objdnode, 'difficult')
    difficultnode.text = '0'
    bndboxnode = ET.SubElement(objdnode, 'bndbox')
    xminnode = ET.SubElement(bndboxnode, 'xmin')
    xminnode.text = str(data[0])
    yminnode = ET.SubElement(bndboxnode, 'ymin')
    yminnode.text = str(data[1])
    xmaxnode = ET.SubElement(bndboxnode, 'xmax')
    xmaxnode.text = str(data[2])
    ymaxnode = ET.SubElement(bndboxnode, 'ymax')
    ymaxnode.text = str(data[3])


sky = BackgroundImg(screen, bg_sky, 1022., 0., 0.0)
# grass_up = BackgroundImg(screen, bg_grass, 1005., 350., 0.25, 0)
# grass_down = BackgroundImg(screen, bg_grass1, 1005., 460., 0.3, 0)
# tree = BackgroundImg(screen, bg_tree, 1000., 230., 0.2, 0)

title = Button(title_pic, 144-89., 150., 0.)
ready = Button(ready_pic, 144-98., 210., 0.)
over = Button(over_pic, 144-98., 190., 0.)

score = Score(screen, 270, 395)
ticker = 0
fileIndex = 0

while True:
    # 60帧
    clock.tick(60)
    # 绘制背景
    sky.draw()

    if not gameStart:
        screen.blit(title.image, title.rect)
        screen.blit(ready.image, ready.rect)
        ticker = 0
    else:
        # birds.update()
        # birds.draw(screen)
        if not gameOver:
            flappyBird.update()
            screen.blit(flappyBird.image, flappyBird.rect)

        neednew = False
        for _p in pipes.sprites():
            if _p.rect.x <= 0:
                pipes.remove(_p)
                neednew = True
        if neednew:
            up_y = 280 + 100*random.random()
            _up, _down = PipePair(
                pipes.sprites()[-1].rect.x+200, up_y=up_y, gap=pipe_gap, speed=pipe_speed)
            pipes.add(_up)
            pipes.add(_down)

        pipes.update()
        pipes.draw(screen)

        if not gameOver:
            for _pipe in pipes.sprites()[:4]:
                # if pygame.sprite.spritecollide(flappyBird, pipes, False):
                if pygame.sprite.collide_rect_ratio(0.91)(flappyBird, _pipe):
                    gameOver = True
                    break
                # 计分
                if _pipe.passed is True and _pipe.counted is False:
                    score.score += 0.5  # 上下两个pipe
                    _pipe.counted = True

            ticker += 1
            if ticker > INTERVAL:
                # 20帧截图一次
                if fileIndex < SHOOTS:
                    fname = 'AnnPics\\{0:0>6}.jpg'.format(fileIndex)
                    fnameSrc = 'JPGs\\{0:0>6}.jpg'.format(fileIndex)
                    pygame.image.save(screen, fnameSrc)
                    offsetx = 0
                    offsety = 0
                    birdinfo = []
                    pipeinfo = []
                    if flappyBird.degree != 0 or flappyBird.degree != -90:
                        offsetx = 5
                        offsety = 5
                    pygame.draw.rect(screen, (255, 0, 0),
                                     (flappyBird.rect.x+offsetx, flappyBird.rect.y+offsetx,
                                      flappyBird.rect.w, flappyBird.rect.h), 1)
                    xmin = flappyBird.rect.x+offsetx
                    ymin = flappyBird.rect.y+offsetx
                    xmax = flappyBird.rect.x+offsetx + flappyBird.rect.w
                    ymax = flappyBird.rect.y+offsetx + flappyBird.rect.h
                    birdinfo.append((xmin, ymin, xmax, ymax))
                    for _pipe in pipes.sprites()[:4]:
                        x, y, w, h = _pipe.rect
                        if x + w/2 < SCREEN_WIDTH:
                            if y < 0:
                                h = h + y - 2
                                y = 2
                            if x + w > SCREEN_WIDTH:
                                w = SCREEN_WIDTH - x - 2
                            if y + h > SCREEN_HEIGHT:
                                h = SCREEN_HEIGHT - y - 2
                            pygame.draw.rect(screen, (255, 0, 0), (x, y, w, h), 1)
                            pipeinfo.append((x, y, x+w, y+h))
                            
                    if ANNOTATION_PIC:
                        pygame.image.save(screen, fname)
                    ticker = 0
                    writeXml('{0:0>6}'.format(fileIndex), birdinfo, pipeinfo)
                    fileIndex += 1


            score.score = math.ceil(score.score)
            score.draw()

        if gameOver:
            screen.blit(over.image, over.rect)

    # 更新屏幕
    pygame.display.update()

    if flappyBird is not None:
        # 鸟默认下降
        flappyBird.birdUp = False

        if flappyBird.rect.y > 460:
            gameOver = True
            flappyBird = None

    # 处理游戏退出
    # 从消息队列中循环取
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # Python中没有switch-case 多用字典类型替代
        # 控制方向
        if event.type == pygame.KEYDOWN:
            if event.key in offset:
                offset[event.key] = 3
        elif event.type == pygame.KEYUP:
            if event.key in offset:
                offset[event.key] = 0
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pressed_array = pygame.mouse.get_pressed()
            for index in range(len(pressed_array)):
                if pressed_array[index]:
                    if index == 0:
                        # print('Pressed LEFT Button!')
                        if not gameStart:
                            gameStart = True
                            # 初始化游戏
                            birds.empty()
                            pipes.empty()
                            InitNewBird()
                            score.score = 0
                            # birds.add(flappyBird)
                            for i in range(3):
                                up_y = 230 + 100*random.random()
                                _up, _down = PipePair(
                                    250+i*200, up_y=up_y, gap=pipe_gap, speed=pipe_speed)
                                pipes.add(_up)
                                pipes.add(_down)
                        elif gameStart and not gameOver:
                            if flappyBird is not None:
                                flappyBird.birdUp = True
                        elif gameStart and gameOver:
                            gameStart = False
                            gameOver = False
                    elif index == 1:
                        # print('The mouse wheel Pressed!')
                        pass
                    elif index == 2:
                        # print('Pressed RIGHT Button!')
                        pass
        elif event.type == pygame.MOUSEMOTION:
            # return the X and Y position of the mouse cursor
            pos = pygame.mouse.get_pos()
            mouse_x = pos[0]
            mouse_y = pos[1]
