import time
import board
import displayio
import busio
from digitalio import DigitalInOut
from analogio import AnalogIn
import neopixel
import adafruit_adt7410
#from adafruit_esp32spi import adafruit_esp32spi
#from adafruit_esp32spi import adafruit_esp32spi_wifimanager
#import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_button import Button
import adafruit_touchscreen
from adafruit_pyportal import PyPortal

# ------------- Inputs and Outputs Setup ------------- #
# init. the temperature sensor
i2c_bus = busio.I2C(board.SCL, board.SDA)
adt = adafruit_adt7410.ADT7410(i2c_bus, address=0x48)
adt.high_resolution = True

# init. the light sensor
light_sensor = AnalogIn(board.LIGHT)

# Helper for cycoling through a number set.
def numberUP(i, max_val):
    i += 1
    if i <= max_val:
        return i
    else:
        return 1


# ------------- Screen Setup ------------- #
pyportal = PyPortal()
display = board.DISPLAY
display.rotation=270

# Backlight function
# Value between 0 and 1 where 0 is OFF, 0.5 is 50% and 1 is 100% brightness.
def set_backlight(val):
    val = max(0, min(1.0, val))
    board.DISPLAY.auto_brightness = False
    board.DISPLAY.brightness = val

# Touchscreen setup
# ------Rotate 270:
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_YD, board.TOUCH_YU,
                                      board.TOUCH_XR, board.TOUCH_XL,
                                      calibration=((5200, 59000), (5800, 57000)),
                                      size=(240, 320))


# ------------- Display Groups ------------- #
splash = displayio.Group(max_size=10) # The Main Display Group
view1 = displayio.Group(max_size=15) # Group for View 1 objects
view2 = displayio.Group(max_size=15) # Group for View 2 objects
view3 = displayio.Group(max_size=15) # Group for View 3 objects

def hideLayer(i):
    try:
        splash.remove(i)
    except ValueError:
        pass

def showLayer(i):
    try:
        time.sleep(0.1)
        splash.append(i)
    except ValueError:
        pass

## ------------- Setup for Images ------------- #

# Display an image until the loop starts
pyportal.set_background('/images/loading.bmp')


bg_group = displayio.Group(max_size=1)
splash.append(bg_group)


icon_group = displayio.Group(max_size=1)
icon_group.x = 180
icon_group.y = 120
icon_group.scale = 1
view2.append(icon_group)

# This will handel switching Images and Icons
def set_image(group, filename):
    """Set the image file for a given goup for display.
    This is most useful for Icons or image slideshows.
        :param group: The chosen group
        :param filename: The filename of the chosen image
    """
    print("Set image to ", filename)
    if group:
        group.pop()

    if not filename:
        return  # we're done, no icon desired
    try:
        if image_file:
            image_file.close
    except NameError:
        pass
    image_file = open(filename, "rb")
    image = displayio.OnDiskBitmap(image_file)
    try:
        image_sprite = displayio.TileGrid(image, pixel_shader=displayio.ColorConverter())
    except TypeError:
        image_sprite = displayio.TileGrid(image, pixel_shader=displayio.ColorConverter(), position=(0,0))
    group.append(image_sprite)

#set_image(start_image,"/images/STRimage.bmp")
set_image(bg_group,"/images/BGimage.bmp")

# ---------- Text Boxes ------------- #
# Set the font and preload letters
font = bitmap_font.load_font("/fonts/Helvetica-Bold-16.bdf")
font.load_glyphs(b'abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()')

# Text Label Objects
feed1_label = Label(font, text="Text Wondow 1", color=0xE39300, max_glyphs=200)
feed1_label.x = 5
feed1_label.y = 60
view1.append(feed1_label)

feed2_label = Label(font, text="Text Wondow 2", color=0xFFFFFF, max_glyphs=200)
feed2_label.x = 5
feed2_label.y = 60
view2.append(feed2_label)

sensors_label = Label(font, text="Data View", color=0x03AD31, max_glyphs=200)
sensors_label.x = 5
sensors_label.y = 60
view3.append(sensors_label)

sensor_data = Label(font, text="Data View", color=0x03AD31, max_glyphs=100)
sensor_data.x = 8
sensor_data.y = 170
view3.append(sensor_data)

# return a reformatted string with wordwrapping
#@staticmethod
def wrap_words(string, max_chars):
    text = pyportal.wrap_nicely(string, max_chars)
    new_text = ""
    for w in text:
        new_text += '\n'+w
    return new_text

# Function for moving the Label text to a position that keeps the top in the same place.
glyph_box = font.get_bounding_box()
glyph_h = glyph_box[1]+abs(glyph_box[3])
def text_box_top(string):
    return round(string.count("\n")*glyph_h/2)-glyph_box[1]

# ---------- Display Buttons ------------- #
buttons = []
# Default button styling:
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 100
BUTTON_MARGIN = 10

# Button Objects
# 320x240
button_view1 = Button(x=0, y=0,
                  width=80, height=40,
                  label="View1", label_font=font, label_color=0xff7e00,
                  fill_color=0x5c5b5c, outline_color=0x767676,
                  selected_fill=0x1a1a1a, selected_outline=0x2e2e2e,
                  selected_label=0x525252)
buttons.append(button_view1)

button_view2 = Button(x=80, y=0,
                  width=80, height=40,
                  label="View2", label_font=font, label_color=0xff7e00,
                  fill_color=0x5c5b5c, outline_color=0x767676,
                  selected_fill=0x1a1a1a, selected_outline=0x2e2e2e,
                  selected_label=0x525252)
buttons.append(button_view2)

button_view3 = Button(x=160, y=0,
                  width=80, height=40,
                  label="View3", label_font=font, label_color=0xff7e00,
                  fill_color=0x5c5b5c, outline_color=0x767676,
                  selected_fill=0x1a1a1a, selected_outline=0x2e2e2e,
                  selected_label=0x525252)
buttons.append(button_view3)

button_switch = Button(x=0, y=220,
                  width=120, height=BUTTON_HEIGHT,
                  label="Switch", label_font=font, label_color=0xff7e00,
                  fill_color=0x5c5b5c, outline_color=0x767676,
                  selected_fill=0x1a1a1a, selected_outline=0x2e2e2e,
                  selected_label=0x525252)
buttons.append(button_switch)

button_2 = Button(x=120, y=220,
                  width=120, height=BUTTON_HEIGHT,
                  label="Button", label_font=font, label_color=0xff7e00,
                  fill_color=0x5c5b5c, outline_color=0x767676,
                  selected_fill=0x1a1a1a, selected_outline=0x2e2e2e,
                  selected_label=0x525252)
buttons.append(button_2)

button_icon = Button(x=150, y=60,
                  width=80, height=40,
                  label="Icon", label_font=font, label_color=0xffffff,
                  fill_color=0x8900ff, outline_color=0xbc55fd,
                  selected_fill=0x5a5a5a, selected_outline=0xff6600,
                  selected_label=0x525252, style=Button.ROUNDRECT)
buttons.append(button_icon)
view2.append(button_icon.group)

button_buzzer = Button(x=150, y=170,
                  width=80, height=40,
                  label="Sound", label_font=font, label_color=0xffffff,
                  fill_color=0x8900ff, outline_color=0xbc55fd,
                  selected_fill=0x5a5a5a, selected_outline=0xff6600,
                  selected_label=0x525252, style=Button.ROUNDRECT)
buttons.append(button_buzzer)
view3.append(button_buzzer.group)

for b in buttons:
    try:
        splash.append(b.group)
    except ValueError:
        pass




# ---------- Sound Effects ------------- #

soundDemo = '/sounds/sound.wav'
soundBeep = '/sounds/beep.wav'
soundTab = '/sounds/tab.wav'




pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=1)
WHITE = 0xffffff
RED = 0xff0000
YELLOW = 0xffff00
GREEN = 0x00ff00
BLUE = 0x0000ff
PURPLE = 0xff00ff
BLACK = 0x000000





set_backlight(0.3)
button_view1.selected = False
button_view2.selected = True
button_view3.selected = True
showLayer(view1)
hideLayer(view2)
hideLayer(view3)

button_mode = 1
switch_state = 0
button_switch.label = "OFF"
button_switch.selected = True




def switch_view(i):
    global view_live
    if i == 1:
        hideLayer(view2)
        hideLayer(view3)
        button_view1.selected = False
        button_view2.selected = True
        button_view3.selected = True
        showLayer(view1)
        view_live = 1
        print("View1 On")
    elif i == 2:
        #global icon
        hideLayer(view1)
        hideLayer(view3)
        button_view1.selected = True
        button_view2.selected = False
        button_view3.selected = True
        showLayer(view2)
        view_live = 2
        print("View2 On")
    else:
        hideLayer(view1)
        hideLayer(view2)
        button_view1.selected = True
        button_view2.selected = True
        button_view3.selected = False
        showLayer(view3)
        view_live = 3
        print("View3 On")


view_live = 1
icon = 1
icon_name = "Ruby"


feed1_text = wrap_words('The text on this screen is wrapped so that it fits it all nicely in the text box. Each text line is {}px tall and the font is {}px tall.'.format(glyph_h, glyph_box[1]), 30)
feed1_label.y = text_box_top(feed1_text)+60
feed1_label.text = feed1_text

feed2_text = wrap_words('Tap on the Icon button to meet a new friend.', 18)
feed2_label.y = text_box_top(feed2_text)+60
feed2_label.text = feed2_text

feed3_text = wrap_words("This screen can display sensor readings and tap Sound to play a WAV file.", 28)
sensors_label.y = text_box_top(feed3_text)+60
sensors_label.text = feed3_text


board.DISPLAY.show(splash)
#start_image.pop() # now that the UI is loaded remove the startup screen.

# ------------- Code Loop ------------- #
while True:

    touch = ts.touch_point

    #light_sensor = AnalogIn(board.LIGHT)

    tempC = round(adt.temperature)
    tempF = tempC * 1.8 + 32

    sensor_data.text = 'Touch: {}\nLight: {}\nTemp: {}°F'.format(touch,light_sensor.value,tempF)



    #feed1_label.text = '{}x{}'.format(ts._size[0], ts._size[1])
    #sensors_label.text = 'Touch={}'.format(touch)
    if touch:
        for i, b in enumerate(buttons):
            if b.contains(touch):
                print('Sending button%d pressed' % i)
                if i == 0 and view_live != 1:
                    pyportal.play_file(soundTab)
                    switch_view(1)
                    while ts.touch_point:
                        pass
                if i == 1 and view_live != 2:
                    pyportal.play_file(soundTab)
                    switch_view(2)
                    while ts.touch_point:
                        pass
                if i == 2 and view_live != 3:
                    pyportal.play_file(soundTab)
                    switch_view(3)
                    while ts.touch_point:
                        pass
                if i == 3:
                    pyportal.play_file(soundBeep)
                    # Toggle switch button type
                    if switch_state == 0:
                        switch_state = 1
                        b.label = "ON"
                        b.selected = False
                        pixel.fill(WHITE)
                        print("Swith ON")
                    else:
                        switch_state = 0
                        b.label = "OFF"
                        b.selected = True
                        pixel.fill(BLACK)
                        print("Swith OFF")
                    # for debounce
                    while ts.touch_point:
                        pass
                    print("Swith Pressed")
                if i == 4:
                    pyportal.play_file(soundBeep)
                    # Momentary button type
                    b.selected = True
                    print('Button Pressed')
                    button_mode
                    button_mode = numberUP(button_mode, 5)
                    if button_mode == 1:
                        pixel.fill(RED)
                    elif button_mode == 2:
                        pixel.fill(YELLOW)
                    elif button_mode == 3:
                        pixel.fill(GREEN)
                    elif button_mode == 4:
                        pixel.fill(BLUE)
                    elif button_mode == 5:
                        pixel.fill(PURPLE)
                    switch_state = 1
                    button_switch.label = "ON"
                    button_switch.selected = False
                    # for debounce
                    while ts.touch_point:
                        pass
                    print("Button released")
                    b.selected = False
                if i == 5 and view_live == 2:
                    pyportal.play_file(soundBeep)
                    b.selected = True
                    while ts.touch_point:
                        pass
                    print("Icon Button Pressed")
                    icon = numberUP(icon, 3)
                    if icon == 1:
                        icon_name = "Ruby"
                    elif icon == 2:
                        icon_name = "Gus"
                    elif icon == 3:
                        icon_name = "Billie"
                    b.selected = False
                    feed2_text = wrap_words('Every time you tap the Icon button the icon image will change. Say hi to {}!'.format(icon_name), 18)
                    feed2_label.y = text_box_top(feed2_text)+60
                    feed2_label.text = "" # Clear out text to fix possible re-draw errors.
                    feed2_label.text = feed2_text
                    set_image(icon_group,"/images/"+icon_name+".bmp")
                if i == 6 and view_live == 3:
                    b.selected = True
                    while ts.touch_point:
                        pass
                    print("Sound Button Pressed")
                    pyportal.play_file(soundDemo)
                    b.selected = False


#print(dir(ts))
#board.DISPLAY.show()