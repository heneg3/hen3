import turtle
import time
import random
import math

## Global variables
# These store the current state of the game

# List of tuples: (x, y, size) giving position and current size of explosion
# sig: list(tuple(float, float, int))
explosions = []

# List of tuples: (x, y, initialx, initialy, vx, vy) giving current and initial
# position of each missile, as well as its velocity
# sig: list(tuple(float, float, float, float, float, float))
missiles = []

# List of tuples (x,y) giving position of lower-left corner of each surviving house
# sig: list(tuple(float, float))
houses = []

# Count the number of frames since the game started. Used for issuing time-based
# events, such as when to launch more missiles
# sig: int
ticks = 0

# How many explosions you have left
# sig: int
ammo = 0

# Your current score. You get five points for killing a missile, plus 1 point
# for surviving every few seconds
# sig: int
score = 0

# When all your houses are dead, this becomes True
# sig: bool
gameover = False


## Constant values
# These are "tuneable" values that never change
# during the course of the game, but the programmer
# can easily adjust them to determine how the game
# is played. They are in UPPER_CASE to indicate
# that they are constants and shouldn't be changed
# by the code
HOUSE_WIDTH = 50
HOUSE_HEIGHT = 70
NUM_HOUSES = 5
MISSILE_SPEED = 3
MORE_EXPLOSION_REWARD_FREQUENCY = 15
EXPLOSION_SIZE = 85
EXPLOSION_LINGER = 15
MISSILE_MIN_FREQ = 5
MISSILE_MAX_FREQ = 85

def draw_explosions():
    """
    sig: () -> NoneType
    Draw all the explosions on the screen.
    Each circular explosion is caused by
    clicking on the screen.
    It grows to a particular radius and changes color.
    The explosion destroys any missiles it hits.
    """
    for (x, y, size) in explosions:
        turtle.up()
        size = min(size, EXPLOSION_SIZE)
        turtle.goto(x, y - size)
        turtle.down()
        exptotal = EXPLOSION_SIZE+EXPLOSION_LINGER

        # The colors of the explosion change with time.
        # We calculate the fill color and the edge color
        # separately. Here, we give the color as an RGB
        # (red, green, blue) tuple, and we vary only the
        # red value.
        fillcolor = (size / (exptotal*2) + 0.5 , 0.5, 0.0)
        edgecolor = ((exptotal-size) / (exptotal*2) + 0.5, 0.5, 0.0)
        turtle.color(edgecolor, fillcolor)
        turtle.width(10)
        turtle.begin_fill()
        turtle.circle(size)
        turtle.end_fill()

def draw_status():
    """
    sig: () -> NoneType
    Draw the status info in the screen.
    It displays how many shots you have, how many
    houses you have, and your score.
    turtle.write is very slow, so using it frequently
    may degrade the smoothness of animation (especially
    on a Mac), therefore we call it only once per frame,
    using \n to display multiple lines at once.
    """
    turtle.up()
    turtle.color("black")
    turtle.goto(-turtle.window_width()/2 + 10, turtle.window_height()/2 - 100)
    turtle.down()
    msg1 = "Shots left: " + str(ammo)
    msg2 = "Houses left: " + str(len(houses))
    msg3 = "Score: " + str(score)
    msg = "\n".join([msg1, msg2, msg3])
    turtle.write(msg, font=("Arial", 20, "normal"))

def draw_houses():
    """
    sig: () -> NoneType
    Draw all the blue houses on the screen
    """
    turtle.color("black", "blue")
    turtle.width(5)
    for (x,y) in houses:
        turtle.up()
        turtle.goto(x,y)
        turtle.down()
        turtle.seth(0)

        # draw a filled rectangle
        turtle.begin_fill()
        for _ in range(2):
            turtle.forward(HOUSE_WIDTH)
            turtle.left(90)
            turtle.forward(HOUSE_HEIGHT)
            turtle.left(90)
        turtle.end_fill()

def draw_missiles():
    """
    sig: () -> NoneType
    Draw all the currently in-flight missiles
    """
    turtle.width(5)
    turtle.color("black")

    # We just draw a thick line from the point where
    # the missile started to its current position
    for (x, y, startx, starty, vx, vy) in missiles:
        turtle.up()
        turtle.goto(startx, starty)
        turtle.down()
        turtle.goto(x,y)

def draw_frame():
    """
    signature: () -> NoneType
    Given the current state of the game in
    the global variables, draw all visual
    elements on the screen.
    """
    draw_houses()
    draw_missiles()
    draw_explosions()
    draw_status()

def key_space():
    """
    signature: () -> NoneType
    This function is called by turtle whenever
    the user press the space key. It resets the game.
    """
    reset()

def update_explosions():
    """
    sig: () -> NoneType
    Checks to see if any explosions have hit a missile,
    and if so, destroy the missile. Enlarges the explosion
    with time, until it runs out.
    """
    new_explosions = []
    for (x, y, size) in explosions:
        effectivesizesquared = min(size, EXPLOSION_SIZE)*min(size, EXPLOSION_SIZE)
        for imissile in range(len(missiles)):
            (mx, my, _, _, _, _) = missiles[imissile]

            # See if the explosion hit a missile. If so, remove
            # the missile
            if (x-mx)*(x-mx) + (y-my)*(y-my) < effectivesizesquared:
                reward(5)
                missiles.pop(imissile)
                break

        # If the explosion still exists, make it a little
        # bit bigger, until it reaches its maximum size
        if size < EXPLOSION_SIZE+EXPLOSION_LINGER:
            new_explosions.append((x, y, size + 5))
    explosions.clear()
    explosions.extend(new_explosions)

def inhouse(pos, house):
    """
    sig: (int, int), (int, int) -> bool
    Determines if the house, located at position house,
    contains the point pos. This is useful for checking
    if a missile has destroyed one of your houses.
    """
    (x,y) = pos
    (hx,hy) = house
    return hx <= x <= hx+HOUSE_WIDTH and hy <= y <= hy + HOUSE_HEIGHT

def update_missiles():
    """
    sig: () -> NoneType
    Move the missiles to their new position, and determine
    if they've hit a house. If so, remove both the missile
    and the house.
    """
    global missiles
    new_missiles = []
    width = turtle.window_width()
    height = turtle.window_height()
    for (x, y, startx, starty, vx, vy) in missiles:
        for ihouse in range(len(houses)):
            house = houses[ihouse]

            # See if a missile hit a house. If so,
            # remove them both
            if inhouse((x,y), house):
                houses.pop(ihouse)
                break
        else:
            # if a missile did not hit a house, then update its
            # position using its current vert and horiz velocity
            if -width/2 <= x <= width/2 and -height/2 <= y <= height/2:
                new_missiles.append((x+vx, y+vy, startx, starty, vx, vy))
    missiles = new_missiles 

def reward(n):
    """
    sig: int -> NoneType
    Update the player's score by n points.
    In addition, every 15 points, give the user
    a bonus explosion
    """
    global score
    global ammo
    oldscore = score
    score += n
    point_inc = MORE_EXPLOSION_REWARD_FREQUENCY
    if oldscore // point_inc < score // point_inc:
        ammo += 1

def update_score():
    """
    sig: () -> NoneType
    This function rewards the player with a point
    for staying alive longer, and also checks if
    all the houses have been destroyed, and so the game is over
    """
    global gameover
    if len(houses) == 0:
        gameover = True
    if ticks % 50 == 49:
        reward(1)

def physics():
    """
    signature: () -> NoneType
    Update the state of the game world, as
    stored in the global variables. Here, you
    should check the positions of the physical
    objects in the game: explosions, missiles,
    houses etc. No drawing is done in this function,
    we're just calculating the state for the next
    frame.
    """
    update_explosions()
    update_missiles()
    update_score()

def ai():
    """
    signature: () -> NoneType
    Perform the 'artificial intelligence' of
    the game. Concretely, this function launches
    missiles in a random direction at somewhat
    regular (but increasingly small) time intervals
    """
    global ticks

    # Here we decide if it's time to launch a new missile
    # We launch missiles more frequently as the game progresess,
    # and we use the ticks variable to keep track of how long
    # the game has been so far
    rate =  min(max(85-ticks//20, MISSILE_MIN_FREQ),MISSILE_MAX_FREQ)
    if ticks % rate == 0:
        width = turtle.window_width()

        # Choose a position for the missile randomly
        # basically, somewhere in the middle top of the screen
        xpos = random.randint(-width//3, width//3)
        ypos = turtle.window_height()/2 - 30

        # choose an angle for the missile randomly
        angle = random.randint(135, 225)

        # Now, convert the angle into vertical and horizontal
        # velocity, assuming that all missiles have the same
        # speed
        speed = MISSILE_SPEED
        xinc = math.sin(math.radians(angle)) * speed
        yinc = math.cos(math.radians(angle)) * speed

        # Add a tuple containing missile information to the
        # global variable
        missiles.append((xpos, ypos, xpos, ypos, xinc, yinc))
    ticks += 1

def house_pos(n):
    """
    sig: int -> (int, int)
    Each numbered house in the game has a position.
    Given a houses number, this function returns
    the x,y location of its lower-left corner
    """
    width = turtle.window_width()
    height = turtle.window_height()
    x = (((n+1) // 2) * (-1)**(n%2))*(HOUSE_WIDTH*2)
    y = -height/2 + 50
    return (x,y) 

def reset():
    """
    signature: () -> NoneType
    This function is called when your game starts.
    It should set initial value for all the
    global variables. Basically, this sets up
    everything for a "new game" state.
    """
    global explosions
    global ammo
    global ticks
    global gameover
    global missiles
    global houses
    global score
    gameover = False
    missiles = []
    ticks = 0
    ammo = 20
    explosions = []
    score = 0
    houses = [house_pos(x) for x in range(NUM_HOUSES)]

def click_handler(x, y):
    """
    int, int -> NoneType
    This function is called by turtle when the user
    clicks on the screen. It should check to see
    if the user has enough explosions left, and if so,
    start a new explosion at the clicked-on location
    """
    global ammo
    if ammo > 0:
        ammo -= 1
        explosions.append((x, y, 0))

def main():
    """
    signature: () -> NoneType
    Run the game's main animation loop
    """

    # One-time setup stuff as follows:

    # Make the turtle move faster; needed for
    # animation
    turtle.tracer(0,0)

    # Set the title of the window
    turtle.title("Missile Command")

    # Don't show the turtle
    turtle.hideturtle()

    # Ask to be notified when the user clicks the mouse
    turtle.onscreenclick(click_handler)

    # Ask to be notified when the user presses the space key
    turtle.onkey(key_space, "space")
    turtle.listen()

    # Set up the world to its initial state
    reset()

    # Here is the main animation loop
    while not gameover:
        # Step 1: calculate the new position of
        # everything currently in play
        physics()

        # Step 2: let the enemy add more missiles
        ai()

        # Step 3: erase everything on the screen
        turtle.clear()

        # Step 4: draw everything where it is now
        draw_frame()
        turtle.update()

        # Step 5: wait for the next frame
        time.sleep(0.05)

main()
