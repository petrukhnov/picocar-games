from machine import Pin, I2C, Timer
from pico_car_mod import SSD1306_I2C, ultrasonic
import time
import utime
import urandom

# Sensor
ultrasonic = ultrasonic()

# OLED CODE
i2c=I2C(1, scl=Pin(15),sda=Pin(14), freq=100000)
oled = SSD1306_I2C(128, 32, i2c)
oled.fill(0)

SCREEN_HEIGHT = 32
SCREEN_WIDTH = 128
pixelSize = 4

segmentsY = 8 #SCREEN_HEIGHT/pixelSize
segmentsX = 32 #SCREEN_WIDTH/pixelSize
VALID_RANGE = [[int(i /segmentsY), i % segmentsY] for i in range(segmentsX * segmentsY -1)]

# Game code
game_timer = Timer()
SPEED = 2 # frequency of updates per second, higher - faster
player = None
food = None

class Snake:
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3
    
    def __init__(self, x=int(segmentsX/2), y=int(segmentsY/2) + 1):
        self.segments = [[x, y]]
        self.x = x
        self.y = y
        self.dir = urandom.randint(0,3)
        self.state = True
        
    def reset(self, x=int(segmentsX/2), y=int(segmentsY/2) + 1):
        self.segments = [[x, y]]
        self.x = x
        self.y = y
        self.dir = urandom.randint(0,3)
        self.state = True
        
    def move(self):
        new_x = self.x
        new_y = self.y
        
        distance = ultrasonic.Distance_accurate()
        if distance < 10:
            self.change_dir()
        
        if self.dir == Snake.UP:
            new_y -= 1
        elif self.dir == Snake.DOWN:
            new_y += 1
        elif self.dir == Snake.LEFT:
            new_x -= 1
        elif self.dir == Snake.RIGHT:
            new_x += 1
        
        for i, _ in enumerate(self.segments):
            if i != len(self.segments) - 1:
                self.segments[i][0] = self.segments[i+1][0]
                self.segments[i][1] = self.segments[i+1][1]
        
        if self._check_crash(new_x, new_y):
            # Oh no, we killed the snake :C
            self.state = False
        
        self.x = new_x
        self.y = new_y
        
        self.segments[-1][0] = self.x
        self.segments[-1][1] = self.y
        
    def eat(self):
        oled.fill_rect(self.x * pixelSize, self.y * pixelSize, pixelSize, pixelSize, 0)
        oled.rect(self.x * pixelSize, self.y * pixelSize, pixelSize, pixelSize, 1)
        self.segments.append([self.x, self.y])
        
    def change_dir(self):
        self.dir = self.dir + 1
        if self.dir > 3:
            self.dir = 0
        
    def _check_crash(self, new_x, new_y):
        if new_y >= segmentsY or new_y < 0 or new_x >= segmentsX or new_x < 0 or [new_x, new_y] in self.segments:
           return True
        else:
            return False
    
    def draw(self):
        oled.rect(self.segments[-1][0] * pixelSize, self.segments[-1][1] * pixelSize, pixelSize, pixelSize, 1)


def main():
    global player
    global food
    
    player = Snake()
    food = urandom.choice([coord for coord in VALID_RANGE if coord not in player.segments])
    oled.fill_rect(food[0] * pixelSize , food[1] * pixelSize, pixelSize, pixelSize, 1)
    
    # Playing around with this cool timer.
    game_timer.init(freq=SPEED, mode=Timer.PERIODIC, callback=update_game)
    

    while True:
        if player.state != True:
            # If the snake is dead
            # Revive our snake friend
            oled.fill(0)
            player.reset()
            food = urandom.choice([coord for coord in VALID_RANGE if coord not in player.segments])
            oled.fill_rect(food[0] * pixelSize , food[1] * pixelSize, pixelSize, pixelSize, 1)
                
                
def update_game(timer):
    global food
    global player
    
    # Remove the previous tail of the snake (more effecient than clearing the entire screen and redrawing everything)
    oled.fill_rect(player.segments[0][0] * pixelSize, player.segments[0][1] * pixelSize, pixelSize, pixelSize, 0)
    
    # Move the snake
    player.move()
    
    if player.state == False:
        # I think he's dead now :/
        oled.fill(0)
        oled.text("Game Over!", int(SCREEN_WIDTH/2) - int(len("Game Over!")/2 * 8), int(SCREEN_HEIGHT/2) - 8)
        oled.text("Snake length:" + str(len(player.segments)), 0, int(SCREEN_HEIGHT/2) + 8)
    
    else:
        # Our snake is still alive and moving
        if food[0] == player.x and food[1] == player.y:
            # Our snake reached the food
            player.eat()
            food = urandom.choice([coord for coord in VALID_RANGE if coord not in player.segments])
            oled.fill_rect(food[0] * pixelSize , food[1] * pixelSize, pixelSize, pixelSize, 1)
        
        player.draw()
        
    # Show the new frame
    oled.show()
    

if __name__ == "__main__":
    main()
