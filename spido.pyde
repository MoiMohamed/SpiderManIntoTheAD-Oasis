# Import necessary libraries
import math
import random, os
PATH = os.getcwd() # Get the current working directory
add_library('minim') # Add the minim library for audio processing
player = Minim(this) # Minim audio player object

# Define Sprite class for the player character
class Sprite:
    def __init__(self):
        # Initialize sprite properties
        self.radius = 50
        
        #position
        self.x = 100
        self.y = 720 - 30
        
        #angular motion
        self.theta = 0
        self.delta_theta = 0
        
        #linear velocity
        self.vx = 0
        self.vy = 0
        
        #attached hook
        self.hook = None
        
        self.collidedWithSpike = False
        
        # Load images and sounds
        self.spriteImg = loadImage(PATH + "/images/spido.png")
        self.swipingSpriteImage = loadImage(PATH + "/images/swiping_spido.png")
        self.webImg = loadImage(PATH + "/images/webb.png")
        self.wallhitSound = player.loadFile(PATH + "/sounds/wall_hit.mp3")
        self.deathSound = player.loadFile(PATH + "/sounds/Death_Sound.mp3")

        # Sprite jumps in the start 
        self.jump()
        
    def display(self):
        # Display sprite swinging when attached to a hook 
        if self.hook:
            
            pushMatrix()  
            translate(self.x - g.x_shift, self.y)
            
            angle = atan2(self.hook.y - self.y, self.hook.x - g.x_shift - (self.x - g.x_shift))
            rotate(angle)  # Rotate the character
            
            image(self.swipingSpriteImage, -25, -25, 50, 50)
    
            popMatrix() 
    
        else:
            # Display sprite when not attached to a hook
            image(self.spriteImg, self.x - g.x_shift - 25, self.y - 25, 50, 50)
    
    # Make the sprite jump at the start
    def jump(self):
        self.vy = -15
    
    # Apply gravity & air resistance to the sprite
    def gravity(self):
            if self.vx > 0:
                self.vx -= 0.1
            elif self.vx < 0:
                self.vx += 0.1
                
            self.vy += 0.3
    
    # Update sprite position and movement
    def update(self):
        # Shift view for parallax effect
        if self.x >= g.w//2:
            g.x_shift = int(self.x - g.w//2)
        elif self.x < g.w//2:
            g.x_shift = 0
            
        # Apply gravity and update position when not attached to a hook
        if self.hook == None:
            self.gravity()
            
     
            self.x += self.vx
            self.y += self.vy
             
        else:
            # Update position and movement when attached to a hook
            
            # Show web image based on orientaion
            pushMatrix()  
            translate(self.x - g.x_shift, self.y) 
            angle = atan2(self.hook.y - self.y, self.hook.x - g.x_shift - (self.x - g.x_shift))
            rotate(angle)  
            
            image(self.webImg, 0, 0, dist(self.x - g.x_shift, self.y, self.hook.x - g.x_shift, self.hook.y), 4)  # Width
    
            popMatrix()  

            # Calculate new position based on hook
            self.vx = (self.hook.x - math.sin(self.theta) * self.hook.webLength) - self.x
            self.vy = (self.hook.y + math.cos(self.theta) * self.hook.webLength) - self.y
            
            self.x = self.hook.x - math.sin(self.theta) * self.hook.webLength
            self.y = self.hook.y + math.cos(self.theta) * self.hook.webLength
          
            
            # Update swinging angular motion
            if self.dirFlg == 1:
                self.theta -= self.delta_theta
                if abs(self.delta_theta) <= 0.1 * (1/(self.hook.webLength/150)):
                    self.delta_theta += 0.0004
            else:
                self.theta -= self.delta_theta
                if abs(self.delta_theta) <= 0.1 * (1/(self.hook.webLength/150)):
                    self.delta_theta -= 0.0004
   
    # Attach the sprite to a hook
    def attachHook(self, hook):
        if self.hook == None:
            self.hook = hook
            
            # Calculate web length
            self.hook.webLength = ((self.x - self.hook.x)**2  + (self.y - self.hook.y)**2)**(0.5)
            # Calculate initial angle
            self.hook.theta = math.asin((self.hook.x - self.x) / self.hook.webLength)
            
            # Calculate initial angle and swing direction
            if self.hook.y <= self.y:
                self.theta = math.asin((self.hook.x - self.x) / self.hook.webLength)
            else:
                self.theta = 2 * (math.asin(1) - math.asin((self.hook.x - self.x) / self.hook.webLength)) + math.asin((self.hook.x - self.x) / self.hook.webLength)
            
            # Set initial angular speed
            if self.x <= self.hook.x:
                self.delta_theta = 3 / self.hook.webLength
                self.dirFlg = 1
            else: 
                self.delta_theta = -3 / self.hook.webLength
                self.dirFlg = 0
    
    # Detach the sprite from a hook
    def deAttachHook(self):
        # Calculate release velocities
        self.vx = (self.hook.x - math.sin(self.theta) * self.hook.webLength) - self.x
        self.vy = (self.hook.y + math.cos(self.theta) * self.hook.webLength) - self.y
        
        self.hook = None
    
    # Check for collisions with obstacles/spikes
    def check_collision_obstacles(self, obstacles):
        for o in obstacles:
            
            # Obstacle rectangular coordinates
            rect_left = o.x
            rect_right = o.x + 20  
            rect_top = o.y
            rect_bottom = o.y + o.sizeY
    
            # Find the closest point on the rectangle to the sprites's center
            closest_x = max(rect_left, min(self.x, rect_right))
            closest_y = max(rect_top, min(self.y, rect_bottom))
    
            # Calculate the distance from the circle's center to this point
            distance = math.sqrt((closest_x - (self.x))**2 + (closest_y - (self.y))**2)
    
            # Check if the distance is less than or equal to the radius
            if distance <= self.radius / 2:
                
                # Dies if collides with a spike
                if o.isSpike == True:
                    self.collidedWithSpike = True
                    break
                
                # Detach from hook if collided while swinging
                if self.hook != None:
                    self.deAttachHook()
   
                
                if self.y <= rect_top:  # Collision from above
                    self.y = rect_top - self.radius / 2  # Place player on top
                    self.vy = o.vy  # Match obstacle's vertical velocity
                elif self.y >= rect_bottom:  # Collision from below
                    self.vy = o.vy  # Stop vertical movement (gravity will act)
                elif self.x  <= rect_left:  # Collision from the left
                    self.x = rect_left - self.radius / 2  # Push player to the left
                    self.vx = 0  # Stop horizontal movement
                elif self.x  >= rect_right:  # Collision from the right
                    self.x = rect_right + self.radius / 2  # Push player to the right
                    self.vx = 0  # Stop horizontal movement
                
                # Play wall hit sound
                self.wallhitSound.setGain(10)
                self.wallhitSound.rewind()
                self.wallhitSound.play()
                                
                break
    
    # Check for collisions with criminals on platforms
    def check_collision_criminals(self, platforms):
        global g
        for p in platforms:

            if p.criminal == None:
                continue
                
            if dist(self.x, self.y, p.criminal.x, p.criminal.y) <= 25 + 25:
                if p.criminal.bigCriminal:
                    g.score += 250 # Add 250 points for catching big criminal
                else:
                    g.score += 50 # Add 50 points for catching regular criminal
                
                p.criminal = None
                
                # Play death sound for criminal
                self.deathSound.setGain(5)
                self.deathSound.play()
                self.deathSound.rewind()
                
                break

# Define Monster class for the chasing the Spider
class Monster:
    def __init__(self):
        # Initialize monster properties
        self.vx = 1
        self.x = 0
        
       
        
        # Set maximum horizontal velocity
        self.maxvx = 7.5
        
        
        # Load Images and Sounds
        self.img = loadImage(PATH + "/images/moni.png")
        self.sound = player.loadFile(PATH + "/sounds/we_are_venom.mp3")
    
    # Display the monster
    def display(self):
        image(self.img, self.x - g.x_shift - 400, 0, 400, 720)       
        
        # Check if the monster has caught the player
        self.checkloss()
        
        # Gradually increase velocity
        if self.vx < self.maxvx:
            self.vx += 0.005
        elif self.vx == self.maxvx: # Cap velocity at maximum
            self.vx = self.maxvx
        self.x += self.vx
        
    # Check if the monster has caught up to the player
    def checkloss(self):
        if self.x - 60 >= g.sprite.x:
            global gameStatus
            
            
            # Play monster killing sound
            self.sound.setGain(6)
            self.sound.play()
            self.sound.rewind()
            
            gameStatus = "End"    

# Define Criminal class for enemies on platforms
class Criminal:
    def __init__(self,x, y, sizex):
        # Initialize criminal properties
        self.x = x
        self.y = y - 25
        self.vx = random.randint(1, 4)
        self.direction = 1
        self.platfX = x
        self.platY = y
        self.platSizeX = sizex
        
        # For smooth motion by swapping images
        self.alternating_img = 0
        
        # Randomly determine if it's a big criminal (boss)
        randCrim = random.randint(1, 4)
        
        # Load image based on criminal type
        if randCrim == 1:
            self.bigCriminal = True
            self.crim1Img = loadImage(PATH + "/images/boss1.png")
            self.crim2Img = loadImage(PATH + "/images/boss2.png")
        else:
            self.bigCriminal = False
            self.crim1Img = loadImage(PATH + "/images/crim1.png")
            self.crim2Img = loadImage(PATH + "/images/crim2.png")
            
    # Display the criminal
    def display(self):
        
        # Switch image every 15 frames
        if frameCount % 15 == 0:
            self.alternating_img = not self.alternating_img
            
        # Display alternating images for animation
        if not self.alternating_img:
            if self.direction == 1:
                image(self.crim1Img, self.x - g.x_shift - 25, self.y - 20, 50, 50)
            else:
                image(self.crim1Img, self.x - g.x_shift - 25, self.y - 20, 50, 50, self.crim1Img.width, 0, 0, self.crim1Img.height)
        else:
            if self.direction == 1:
                image(self.crim2Img, self.x - g.x_shift - 25, self.y - 20, 50, 50)
            else:
                image(self.crim2Img, self.x - g.x_shift - 25, self.y - 20, 50, 50, self.crim2Img.width, 0, 0, self.crim2Img.height)
        
        # Update criminal's position
        self.move()
        
    # Move the criminal back and forth on the platform while changing direction
    def move(self):
        
        if self.x <= self.platfX:
            self.direction = 1
        elif self.x >= self.platfX + self.platSizeX:
            self.direction = -1
            
        self.x += self.direction * self.vx
        
        
# Define Platform class for platforms with criminals 
class Platform:
    def __init__(self,x,y):
        # Initialize platform properties
        self.x = x
        self.y = y
        self.sizeX = random.randint(50, 200) # Height
        
        # Create a criminal on this platform
        self.criminal = Criminal(x, y, self.sizeX) 
        
        # Load platform image
        self.img = loadImage(PATH + "/images/platform.png")
    
    # Display the platform and its criminal
    def display(self):
        image(self.img, self.x - g.x_shift, self.y, self.sizeX, 20)
        if self.criminal:
            self.criminal.display()
            
            
# Define Obstacle class for obstacles in the game
class Obstacle:

    def __init__(self, x, y, hook1, hook2):
        # Initialize obstacle properties
        self.x = x
        self.y = y
        self.vy = 1
        self.sizeY = random.randint(100, 200) # Random Height
        
        # Storing the two Hooks that the obstacle will move in between
        self.hook1 = hook1
        self.hook2 = hook2
        
        # Set initial direction (1 for down, -1 for up)
        self.direction = 1
        
        self.non_deadlyImg = loadImage(PATH + "/images/brick2.jpg") # Load non-deadly obstacle image
        self.spikeImg = loadImage(PATH + "/images/two_sided_spike.png") # Load spike image
    
        
        # Randomly determine if the obstacle is a spike
        randSpike = random.randint(1,4)

        if randSpike == 1:
            self.isSpike = True
        else:
            self.isSpike = False
    
    # Display the obstacle
    def display(self):
        
        if self.isSpike:
            image(self.spikeImg, self.x - g.x_shift, self.y, 20, self.sizeY)
           # fill(255,0,255)
        else:
            image(self.non_deadlyImg, self.x - g.x_shift, self.y, 20, self.sizeY)
        
        # Update position
        self.move()
        
    # Move the obstacle up and down between two corrosponding hooks
    def move(self):
        if self.y <= min(self.hook1.y, self.hook2.y):
            self.direction = 1
        elif self.y >= 500:
            self.direction = -1
            
        self.y += self.direction * self.vy

# Define Hook class for swing points in the game
class Hook:
    def __init__(self, x, y):
        # Initialize hook properties
        self.radius = 50
        self.x = x
        self.y = y
        
        
        # Initialize web length and theta (set when sprite attaches)
        self.webLength = None
        self.theta = None
        
        # Associated Platform or Obstacle/Spike after each Hook
        self.platform = None
        self.obstacle = None
        
        # Load hook image
        self.img = loadImage(PATH + "/images/hook.png")

        
    # Display the hook
    def display(self):
        
        # Display associated platform if present
        if self.platform != None:
            self.platform.display()
        
        # Display associated obstacle if present
        if self.obstacle != None:
            self.obstacle.display()
            
        # Display hook image
        image(self.img, self.x - g.x_shift - 25, self.y - 25, 50, 50)
    
    
    # Generate the game level Randomly
    def generate_hooks(self, start, no):
        start -= 200 # Adjust starting position
        hooks = [] # Initialize list to store hooks
        for i in range(no):
            # Create new hook at random position
            hooks += [Hook(start + random.randint(300, 400), random.randint(100, 500))]
            
            # Update start position for next hook
            start = hooks[len(hooks) - 1].x
        
        # Randomly add obstacle/spikes or platforms with criminals between hooks
        for i in range(len(hooks)-1):
            if random.randint(1, 3) == 2:
                hooks[i].obstacle = Obstacle(random.randint(hooks[i].x + 30, (hooks[i+1].x - hooks[i].x) + hooks[i].x - 30), random.randint(100, 500), hooks[i], hooks[i+1])
                continue
            
            if random.randint(1, 5) == 3:
                hooks[i].platform = Platform(random.randint(hooks[i].x + 40, (hooks[i+1].x - hooks[i].x) + hooks[i].x - 40), random.randint(min(500,min(hooks[i].y +30, hooks[i+1].y + 30)), 500))
                continue
        
        # Return the list of generated hooks     
        return hooks
    
    # For debugging 
    def __str__(self):
        return "x " +  str(self.x) +  "y "  + str(self.y)

# Define Game class to manage overall game state
class Game:
    def __init__(self, w, h):
        # Initialize game properties
        self.w = w # Set game width
        self.h = h # Set game height
        self.x_shift = 0 # Parallax shift
        self.score = 0

        
        # Game elements 
        self.sprite = Sprite()
        self.hooks = Hook(0, 0).generate_hooks(200, 20)
        self.monster = Monster()
        
            
        # Load sounds and images
        self.fall = player.loadFile(PATH + "/sounds/fall.mp3")
        self.bg_imgs = [loadImage(PATH + "/images/prev.png")]
    
    # Main game display method
    def display(self):
        
        # Increase score every 6 frames if sprite is above ground (10 points per second)
        if frameCount % (60/10) == 0:
            if self.sprite.y <= 720:
                self.score += 1
        
        # Generate new 5 hooks when player passes 10th hook
        if self.sprite.x > self.hooks[9].x:
            self.hooks = self.hooks + Hook(0, 0).generate_hooks(self.hooks[len(self.hooks) - 1].x + 200, 5)
            self.hooks = self.hooks[5:] # Remove first 5 hooks

        x_local_shift = 0
        cnt = 1
        
        # Display background with parallax effect
        for img in self.bg_imgs:
            
            if cnt == 1:
                x_local_shift = self.x_shift//4
            elif cnt == 2:
                x_local_shift = self.x_shift//3
            elif cnt == 3:
                x_local_shift = self.x_shift//2
            else:
                x_local_shift = self.x_shift        
            
            width_right = x_local_shift % self.w
            width_left = self.w - width_right
            
            #make the image wrap around
            image(img, 0, 0, width_left, self.h, width_right, 0, self.w, self.h)
            image(img, width_left, 0, width_right, self.h, 0, 0, width_right, self.h)
            
            cnt += 1 


        
        # Display, Update game elements, and Check for Collisions/Actions
        self.sprite.display()
        self.sprite.update()
        
        for h in self.hooks:
            h.display()
            
        self.monster.display()
        
        obstacles = [hook.obstacle for hook in self.hooks if hook.obstacle]
        platforms = [hook.platform for hook in self.hooks if hook.platform]
        
        self.sprite.check_collision_obstacles(obstacles)
        self.sprite.check_collision_criminals(platforms)
        
        # Keep monster within 700 pixels of player
        if self.monster.x + 700 < self.sprite.x:
            self.monster.x = self.sprite.x - 700
        
        # End game if player falls off screen or hits spike
        if (self.sprite.y - self.sprite.radius // 2 >= self.h and self.sprite.hook == None and self.sprite.vy > 0) or self.sprite.collidedWithSpike == True:
            global gameStatus
            gameStatus = "End"
            self.fall.play() # Play fall sound
        
        
        # Display score
        fill(0)
        textSize(20)
        text("Score: " + str(self.score), 1200, 30)

# Define StartScreen class for the game's main menu and Instructions screen
class StartScreen:
    def __init__(self):
        # Initialize StartScreen properties
        self.state = gameStatus
        self.w = 1280
        self.h = 720
        
        self.spike_img = loadImage(PATH + "/images/two_sided_spike.png")
        self.menu_img = loadImage(PATH + "/images/menu.jpg")
        self.instructions_img = loadImage(PATH + "/images/controls2.jpg")
        self.brick_img = loadImage(PATH + "/images/brick2.jpg")
        self.bossImg = loadImage(PATH + "/images/boss1.png")
        self.crimImg = loadImage(PATH + "/images/crim1.png")
        
    def display_start(self):
        # Display appropriate screen based on game state
        if self.state == "Menu":
            self.display_menu()
        elif self.state == "Instructions":
            self.display_instructions()
        
    def display_instructions(self):
        # Display the Instructions screen
        image(self.instructions_img, 0, 0)
        textSize(23)
        fill(255)
        
        # Display game instructions
        textAlign(CENTER, CENTER)
        text("Press and hold a hook to swing. Release the button to let go.", self.w // 2, self.h - 670)
        text("Outrun the monster for as long as possible while dodging spikes scattered across the map.", self.w // 2, self.h - 610)
        text("Deadly spikes will kill you instantly. Non-deadly spikes slow you down.", self.w//2, self.h - 550)
        text("Survive longer to earn more points.", self.w//2, self.h - 490)
        text("Passing through criminals earns bonus points. Boss criminals are worth 5x the points.", self.w//2, self.h - 430)
        text("The longer you survive, the faster the game speeds up, making it increasingly challenging.", self.w//2, self.h - 370)
        text("The game ends if the monster catches you, you hit a deadly spike, or fall below the map boundaries.", self.w//2, self.h - 310)
        text("Swiping below the boundaries will stop the score increase.", self.w//2, self.h - 250)
        text("Deadly Spike", 350, self.h - 60)
        text("Non-deadly Obstacle", 950, self.h - 60)
        text("Criminal Boss", 550, self.h - 80)
        text("Criminal", 750, self.h - 80)

        
        self.spike_img.resize(100, 150)
        image(self.spike_img, 300, self.h - 230)
        
        self.brick_img.resize(100, 150)
        image(self.brick_img, 900, self.h - 230)
        
        image(self.bossImg, 475, self.h - 230)
        
        self.crimImg.resize(100, 100)
        image(self.crimImg, 700, self.h - 210)
        
        
        # Display "Back" button, changing color when mouse hovers over it
        if mouseX > g.w//3 and mouseX < g.w*2 // 3 and mouseY > g.h - 50 and mouseY < g.h - 25:
            fill(60, 179, 113)
            textSize(55)
        else:
            textSize(40)
        
        text("Back", self.w // 2, self. h - 40)
    
    
    # Display the main menu
    def display_menu(self):
        image(self.menu_img, 0, 0)
        
        
        
        # Display game title with shadow effect
        textAlign(CENTER, CENTER)
        textSize(80)

        fill(0)
        for offset in range(1, 4):
            text("Spider Man", self.w // 2 + offset, self.h // 4 + offset)
        fill(255, 0, 0)  # Spider-Man red
        text("Spider Man", self.w // 2, self.h // 4)
        
        textSize(45)
        fill(0)
        for offset in range(1, 3):
            text("Into the AD-verse", self.w // 2 + offset, self.h // 4 + 70 + offset)
        fill(0, 191, 255)  # Deep sky blue
        text("Into the AD-Oasis", self.w // 2, self.h // 4 + 70)
        
        
        # Display "Start Game" button & "Instructions" buttons, changing color and size when mouse hovers over it
        if mouseX > g.w // 3 and mouseX < g.w * 2 // 3 and mouseY > g.h // 2 - 30 and mouseY < g.h // 2 + 30:
            fill(60, 179, 113)
            textSize(75)
        else:
            fill(255)
            textSize(50)
        text("Start Game", self.w // 2, self.h // 2)
        
        if mouseX > g.w // 3 and mouseX < g.w * 2 // 3 and mouseY > g.h * 2 // 3 - 30 and mouseY < g.h * 2 // 3 + 30:
            textSize(75)
            fill(60, 179, 113)
        else:
            textSize(50)
            fill(255)
        text("Instructions", self.w // 2, self.h * 2 // 3)

# Define EndScreen class for the game over screen
class EndScreen:
    def __init__(self):
        # Initialize EndScreen properties
        self.w = 1280
        self.h = 720
        self.state = "End"
        self.end_img = loadImage(PATH + "/images/menu3.jpg")

    def display(self):
        # Display the end screen
        global g
        # Read the highest score from file
        with open(PATH + "/highest_score.txt", "r") as file:
            high_score = int(file.readline())
        
        # If no previous high score, use current
        if high_score == -1:
            high_score = g.score
        
        
        # Display End Screen Elements
        image(self.end_img, 0, 0)
        textSize(50)
        fill(255)
        textAlign(CENTER, CENTER)
        text("Game Over", self.w // 2, self.h // 3 - 50)
        textSize(40)
        text("Score: " + str(g.score), self.w // 2, self.h // 3 + 50)
        text("Highest Score: " + str(high_score), self.w // 2, self.h // 3 + 100)

        if mouseX > self.w // 3 and mouseX < self.w * 2 // 3 and mouseY > self.h // 1.5 - 30 and mouseY < self.h // 1.5 + 30:
            textSize(55)
            fill(60, 179, 113)
        else:
            textSize(40)
            fill(255)
        text("Main Menu", self.w // 2, self.h // 1.5)

        if mouseX > self.w // 3 and mouseX < self.w * 2 // 3 and mouseY > self.h // 1.3 - 30 and mouseY < self.h // 1.3 + 30:
            
            textSize(55)
            fill(60, 179, 113)
        else:
            fill(255)
            textSize(40)
        text("New Game", self.w // 2, self.h // 1.3)
        
        # Update the highest score file
        with open(PATH + "/highest_score.txt", "w") as file:
            file.write(str(max(high_score, g.score)))


# Initialize global variables and objects
g = Game(1280, 720) # Create main game object
gameStatus = "Menu" #Menu => Menu Page, Instructions => Instructions Page, Game => Gameplay, End => End of Game Screen
music = player.loadFile(PATH + "/sounds/spido_music.mp3") # Load background music
web = player.loadFile(PATH + "/sounds/Web_Sound.mp3") # Load web sound

def setup():
    # Set up the game window and frame rate
    size(1280, 720)
    frameRate(60)
    
    
def draw():
    # Running background music
    if not music.isPlaying():
        music.setGain(-15)
        music.rewind()
        music.play()
    
    background(255)
    
    # Display start or instructions screen
    if gameStatus == "Menu" or gameStatus == "Instructions":
        StartScreen().display_start()
    elif gameStatus == "Game":
        g.display() # Display main game
    else:
        if music.isPlaying():
            music.rewind()
            music.pause() # Pause music when game ends
        EndScreen().display() # Display end screen

# Handle mouse click events (Buttons)
def mouseClicked():
    global g
    global gameStatus
    
    if gameStatus == "Menu":
        if mouseX > g.w // 3 and mouseX < g.w * 2 // 3 and mouseY  > g.h // 2 - 30 and mouseY < g.h // 2 + 30:
            gameStatus = "Game"
            g = Game(1280, 720)
        
        elif mouseX > g.w // 3 and mouseX < g.w * 2 // 3 and mouseY > g.h * 2 // 3 - 30 and mouseY < g.h * 2 // 3 + 30:
            gameStatus = "Instructions"
            
    elif gameStatus == "End":
        if mouseX > g.w // 3 and mouseX < g.w * 2 // 3 and mouseY > g.h // 1.5 - 30 and mouseY < g.h // 1.5 + 30:
            gameStatus = "Menu"
        
        elif mouseX > g.w // 3 and mouseX < g.w * 2 // 3 and mouseY > g.h // 1.3 - 30 and mouseY < g.h // 1.3 + 30:
            gameStatus = "Game"
            g = Game(1280, 720)

    else:
        if mouseX > g.w//3 and mouseX < g.w*2 // 3 and mouseY > g.h - 50 and mouseY < g.h - 30:
            gameStatus = "Menu"
        
            
            
    if gameStatus == "END":
        g = Game(1280, 720)
        
# Handle mouse press events (for swinging)
def mousePressed():
    if gameStatus == "Game":
        
        # Play web sound
        web.setGain(-12)
        web.play()
        web.rewind()
        nearest_hook = None
        min_distance = float('inf')
        
        # Find the nearest hook to pressed x position to attach to
        for hook in g.hooks:
            distance = abs(mouseX + g.x_shift - hook.x)  # Compare mouseX with hook.x
            if distance < min_distance:
                min_distance = distance
                nearest_hook = hook
        
        # Attach sprite to nearest hook
        if nearest_hook:
            g.sprite.attachHook(nearest_hook)
            
 # Handle mouse release events (for detaching from hook
def mouseReleased():
    if g.sprite.hook != None:
        g.sprite.deAttachHook()
