import board
import displayio
import busio
from digitalio import DigitalInOut
from analogio import AnalogIn
import neopixel
import adafruit_adt7410
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_button import Button
import adafruit_touchscreen
from adafruit_minimqtt import MQTT
#from adafruit_pyportal import PyPortal



# ------------- Screen eliments ------------- #

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


# Load and setup Background image
bitmap_file = open("/BGimage.bmp", "rb")
color_bitmap = displayio.OnDiskBitmap(bitmap_file)
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=displayio.ColorConverter())

# ---------- Set the font and preload letters ----------
# Be sure to put your font into a folder named "fonts".
font = bitmap_font.load_font("/fonts/Helvetica-Bold-16.bdf")
# This will preload the text images.
font.load_glyphs(b'abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()')

# ------------- User Inretface Eliments ------------- #

# Make the display context
splash = displayio.Group(max_size=15)
view1 = displayio.Group(max_size=15)
view2 = displayio.Group(max_size=15)
view3 = displayio.Group(max_size=15)

splash.append(bg_sprite)



buttons = []
# Default button styling:
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 100
BUTTON_MARGIN = 10

# Button Objects
# 320x240

button_1 = Button(x=0, y=220,
                  width=120, height=BUTTON_HEIGHT,
                  label="Button 1", label_font=font, label_color=0x505050,
                  fill_color=0x9e9e9e, outline_color=0x464646)
buttons.append(button_1)

button_2 = Button(x=120, y=220,
                  width=120, height=BUTTON_HEIGHT,
                  label="Button 2", label_font=font, label_color=0x505050,
                  fill_color=0x9e9e9e, outline_color=0x464646)
buttons.append(button_2)

button_3 = Button(x=0, y=0,
                  width=80, height=40,
                  label="Feed1", label_font=font, label_color=0x505050,
                  fill_color=0x9e9e9e, outline_color=0x464646,selected_outline=0x838383,  selected_label=0x838383)
buttons.append(button_3)

button_4 = Button(x=80, y=0,
                  width=80, height=40,
                  label="Feed2", label_font=font, label_color=0x505050,
                  fill_color=0x9e9e9e, outline_color=0x464646,selected_outline=0x838383, selected_label=0x838383)
buttons.append(button_4)

button_5 = Button(x=160, y=0,
                  width=80, height=40,
                  label="Data", label_font=font, label_color=0x505050,
                  fill_color=0x9e9e9e, outline_color=0x464646,selected_outline=0x838383, selected_label=0x838383)
buttons.append(button_5)

button_6 = Button(x=150, y=170,
                  width=80, height=40,
                  label="Serial", label_font=font, label_color=0x505050,
                  fill_color=0x9e9e9e, outline_color=0x464646)
buttons.append(button_6)

for b in buttons:
    if b.label == "Serial":
        view3.append(b.group)
    else:
        splash.append(b.group)

# Text Label Objects
feed1_label = Label(font, text="Text Wondow 1", color=0xE39300, max_glyphs=200)
feed1_label.x = 5
feed1_label.y = 60
view1.append(feed1_label)

feed2_label = Label(font, text="Text Wondow 2", color=0x7433FF, max_glyphs=200)
feed2_label.x = 5
feed2_label.y = 60
view2.append(feed2_label)

sensors_label = Label(font, text="Data View", color=0x03AD31, max_glyphs=200)
sensors_label.x = 5
sensors_label.y = 60
view3.append(sensors_label)

touch_data = Label(font, text="Data View", color=0x03AD31, max_glyphs=200)
touch_data.x = 8
touch_data.y = 130
view3.append(touch_data)


def hideLayer(i):
    try:
        splash.remove(i)
    except ValueError:
        pass

def showLayer(i):
    try:
        splash.append(i)
    except ValueError:
        pass

# return a reformatted string with wordwrapping
#@staticmethod
def wrap_nicely(string, max_chars):
    """A helper that will return the string with word-break wrapping.
    :param str string: The text to be wrapped.
    :param int max_chars: The maximum number of characters on a line before wrapping.
    """
    string = string.replace('\n', '').replace('\r', '') # strip confusing newlines
    words = string.split(' ')
    the_lines = []
    the_line = ""
    for w in words:
        if len(the_line+' '+w) <= max_chars:
            the_line += ' '+w
        else:
            the_lines.append(the_line)
            the_line = w
    if the_line:
        the_lines.append(the_line)
    the_lines[0] = the_lines[0][1:]
    the_newline = ""
    for w in the_lines:
        the_newline += '\n'+w
    return the_newline

# Function for moving the Label text to a position that keeps the top in the same place.
glyph_box = font.get_bounding_box()
glyph_h = glyph_box[1]+abs(glyph_box[3])
def text_box_top(string):
    return round(string.count("\n")*glyph_h/2)-glyph_box[1]

board.DISPLAY.show(splash)
set_backlight(0.3)
button_3.selected = False
button_4.selected = True
button_5.selected = True
showLayer(view1)
hideLayer(view2)
hideLayer(view3)
view_live = 1

button1_state = 0
button_1.label = "OFF"
button_1.selected = True

feed1_text = wrap_nicely('The text on this screen is wrapped so that it fits it all nicely in the text box. Each text line is {}px tall and the font is {}px tall.'.format(glyph_h, glyph_box[1]), 30)
feed1_label.y = text_box_top(feed1_text)+60
feed1_label.text = feed1_text

feed2_text = wrap_nicely('The screen can be rotated via the code and this screen is currently rotated by {}°'.format(display.rotation), 33)
feed2_label.y = text_box_top(feed2_text)+60
feed2_label.text = feed2_text

feed3_text = wrap_nicely("We can also display touchscreen cowordinates:", 33)
sensors_label.y = text_box_top(feed3_text)+60
sensors_label.text = feed3_text

# ------------- Code Loop ------------- #
while True:

    touch = ts.touch_point

    touch_data.text = '{}'.format(touch)



    #feed1_label.text = '{}x{}'.format(ts._size[0], ts._size[1])
    #sensors_label.text = 'Touch={}'.format(touch)
    if touch:
        for i, b in enumerate(buttons):
            if b.contains(touch):
                print('Sending button%d pressed' % i)
                if i == 0:
                    # Toggle switch button type
                    if button1_state == 0:
                        button1_state = 1
                        b.label = "ON"
                        b.selected = False
                        print("Button 1 ON")
                    else:
                        button1_state = 0
                        b.label = "OFF"
                        b.selected = True
                        print("Button 1 OFF")
                    # for debounce
                    while ts.touch_point:
                        pass
                    print("Button 1 Pressed")
                if i == 1:
                    # Momentary button type
                    b.selected = True
                    print('Button 2 Pressed')
                    # for debounce
                    while ts.touch_point:
                        pass
                    print("Button 2 released")
                    b.selected = False
                if i == 2:
                    button_3.selected = False
                    button_4.selected = True
                    button_5.selected = True
                    showLayer(view1)
                    hideLayer(view2)
                    hideLayer(view3)
                    view_live = 1
                    while ts.touch_point:
                        pass
                    print("View1 On")
                    b.selected = False
                if i == 3:
                    button_3.selected = True
                    button_4.selected = False
                    button_5.selected = True
                    hideLayer(view1)
                    showLayer(view2)
                    hideLayer(view3)
                    view_live = 2
                    while ts.touch_point:
                        pass
                    print("View2 On")
                    b.selected = False
                if i == 4:
                    button_3.selected = True
                    button_4.selected = True
                    button_5.selected = False
                    hideLayer(view1)
                    hideLayer(view2)
                    showLayer(view3)
                    view_live = 3
                    while ts.touch_point:
                        pass
                    print("View3 On")
                if i == 5 and view_live == 3:
                    b.selected = True
                    while ts.touch_point:
                        pass
                    print("Serial Button Pressed")
                    b.selected = False

#print(dir(ts))
#board.DISPLAY.show()