import sys, pygame, socket
from pygame.locals import *
import time
import datetime
import calendar
import subprocess
from subprocess import *
import os
import RPi.GPIO as GPIO

os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
os.environ["SDL_MOUSEDRV"] = "TSLIB"

# Init variables
SCREEN_HEIGHT = 240
SCREEN_WIDTH = 320
BUTTON_GAP = 20
BUTTON_BUFFER = 20
SYM_BUFFER = 30
SYM_GAP = SCREEN_HEIGHT/5
BUTTON_LEN = ((SCREEN_WIDTH-SYM_BUFFER) - (3*BUTTON_BUFFER)) / 3
BUTTON_HEIGHT = 50

# Fonts
BUTTON_FONT_SIZE = 36
LABEL_FONT_SIZE = 38
SYM_FONT_SIZE = 30

# COLORS
BG_COLOR = (255,255,255)
BOX_COLOR = (0,0,255)
BUTTON_TEXT_COLOR = (0,0,255)
BUTTON_OUTLINE_COLOR = (0,0,255)
BUTTON_SELECT_COLOR = (0,255,0)
SYM_TEXT_COLOR = (0,0,255)
LABEL_TEXT_COLOR = (0,0,255)


# Initialize pygame and hide mouse
pygame.init()
screen_size = width, heigh = SCREEN_WIDTH, SCREEN_HEIGHT
screen = pygame.display.set_mode(screen_size)
#pygame.mouse.set_visible(0)

# Helpers
class Button:
    def __init__(self, label, startx, starty):
        self.is_active = False
        self.label = label
        self.x = startx
        self.y = starty
        self.draw_button()

    def set_active(self, active_flag=True):
        self.is_active = active_flag

    def set_label(self, newlabel):
        self.label = newlabel

    def draw_button(self):
        # Clear button area
        pygame.draw.rect(screen, BG_COLOR, (self.x-10, self.y-10, BUTTON_LEN, BUTTON_HEIGHT), 0)

        font = pygame.font.Font(None, BUTTON_FONT_SIZE)
        label = font.render(str(self.label), 1, BUTTON_TEXT_COLOR)
        screen.blit(label, (self.x, self.y))
        if self.is_active:
            pygame.draw.rect(screen, BUTTON_SELECT_COLOR, (self.x-10, self.y-10, BUTTON_LEN, BUTTON_HEIGHT),2)
        else:
            pygame.draw.rect(screen, BUTTON_OUTLINE_COLOR, (self.x-10, self.y-10, BUTTON_LEN, BUTTON_HEIGHT), 2)

    def in_bound(self, xtouch, ytouch):
        # Check if in X
        if self.x-10 <= xtouch <= self.x-10+BUTTON_LEN:
            # Check if in Y
            if self.y-10 <= ytouch <= self.y-10+BUTTON_HEIGHT:
                return True
        return False

class DatePicker:
    def __init__(self, startx, starty):
        self.x = startx
        self.y = starty
        self.date = datetime.datetime.now()
        self.month_button = Button(self.date.strftime("%b"), self.x+BUTTON_BUFFER, self.y+10)
        self.day_button = Button(self.date.strftime("%d"), self.x+2*BUTTON_BUFFER+BUTTON_LEN, self.y+10)
        self.year_button = Button(self.date.strftime("%y"), self.x+3*BUTTON_BUFFER+2*BUTTON_LEN, self.y+10)

    def redraw_buttons(self):
        self.month_button.draw_button()
        self.day_button.draw_button()
        self.year_button.draw_button()

    def touch_event(self, x, y):
        # deactivate all the buttons first
        # check buttons for touch and activate
        if self.month_button.in_bound(x, y):
            self.month_button.set_active(True)
            self.day_button.set_active(False)
            self.year_button.set_active(False)
        elif self.day_button.in_bound(x,y):
            self.day_button.set_active(True)
            self.month_button.set_active(False)
            self.year_button.set_active(False)
        elif self.year_button.in_bound(x,y):
            self.year_button.set_active(True)
            self.day_button.set_active(False)
            self.month_button.set_active(False)
        # redraw all buttons
        self.redraw_buttons()

    def add_month(self, months):
        month = self.date.month-1
        month += months
        month = month % 12 + 1
        day = min(self.date.day, calendar.monthrange(self.date.year, month)[1])
        self.date = datetime.date(self.date.year, month, day)
        print month

    def add_day(self, days_to_add):
        delta = datetime.timedelta(days=days_to_add)
        self.date = self.date + delta
        print self.date.day

    def add_year(self, years):
        month = self.date.month
        year = self.date.year
        print year
        day = min(self.date.day, calendar.monthrange(self.date.year, month)[1])
        self.date = datetime.date(year, month, day)

    def increment(self, delta=1):
        # Check which box is active
        if self.month_button.is_active:
            self.add_month(delta)
        elif self.day_button.is_active:
            self.add_day(delta)
        elif self.year_button.is_active:
            self.add_year(delta)
        # Re-draw
        self.year_button.set_label(self.date.strftime("%y"))
        self.day_button.set_label(self.date.strftime("%d"))
        self.month_button.set_label(self.date.strftime("%b"))
        self.redraw_buttons()

def make_label(text, xpo, ypo, fontsize, colour):
    font=pygame.font.Font(None,fontsize)
    label=font.render(str(text), 1, (colour))
    screen.blit(label,(xpo,ypo))

# define function for finding and handeling touch events
def on_touch():
    # Get the touch position
    touch_x = pygame.mouse.get_pos()[0]
    touch_y= pygame.mouse.get_pos()[1]

    # Notify date_picker
    date_picker.touch_event(touch_x, touch_y)

    # Check exit
    if exit_button.in_bound(touch_x, touch_y):
        # exit
        screen.fill((0,0,0))
        font=pygame.font.Font(None,72)
        label=font.render("Exiting to Terminal", 1, (255,255,255))
        screen.blit(label,(10,120))
        pygame.display.flip()
        pygame.quit()
        sys.exit()

# Set Background color and border
screen.fill(BG_COLOR)
pygame.draw.rect(screen, BOX_COLOR, (0,0,SCREEN_WIDTH, SCREEN_HEIGHT), 4)

# Make Top Label
make_label("Cynthia's NYT Printer", 5, 30, LABEL_FONT_SIZE, LABEL_TEXT_COLOR)

# Make Date Picker
date_picker = DatePicker(0,90)

# Make Side Labels
make_label("T", SCREEN_WIDTH-SYM_BUFFER+5, SYM_GAP, SYM_FONT_SIZE, SYM_TEXT_COLOR)
make_label("P", SCREEN_WIDTH-SYM_BUFFER+5, 2*SYM_GAP, SYM_FONT_SIZE, SYM_TEXT_COLOR)
make_label("+", SCREEN_WIDTH-SYM_BUFFER+5, 3*SYM_GAP, SYM_FONT_SIZE, SYM_TEXT_COLOR)
make_label("-", SCREEN_WIDTH-SYM_BUFFER+5, 4*SYM_GAP, SYM_FONT_SIZE, SYM_TEXT_COLOR)

exit_button = Button("Exit", 10, 200)


# Set up gpio pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)




# While loop to manage touch screen inputs
while 1:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            on_touch()

        #ensure there is always a safe way to end the program if the touch screen fails
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit()
    pygame.display.update()


    # Check for side button presses
    if GPIO.input(17) == GPIO.LOW:
        # Print Top button
        time.sleep(200)
    elif GPIO.input(22) == GPIO.LOW:
        # Print secont buttion
        time.sleep(200)
    elif GPIO.input(23) == GPIO.LOW:
        date_picker.increment(1)
	time.sleep(200)
    elif GPIO.input(27) == GPIO.LOW:
        date_picker.increment(-1)
	time.sleep(200)

