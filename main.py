import pyautogui
import time
from PIL import Image
import cv2
import numpy as np
from tesserocr import PyTessBaseAPI, PSM, RIL
import os

items = ['Продвинутые запчасти', 'Перун', 'Тактический запас']
items_prices = [46000, 28000, 29000]

buyoutprice = items_prices[2]
page = 2

lots_count = 10

x_screenshot, y_screenshot, screenshot_size_x, screenshot_size_y = 889, 385, 513, 369
x_price_offset, y_price_offset, price_size_x, price_size_y = 355, 2, 135, 30
good_line_size_y = 36
good_line_loxal_coord_x, good_line_local_coord_y = screenshot_size_x / 2, good_line_size_y / 2
search_button_position_x, search_button_position_y = 1337, 337
scroller_pos_x, scroller_pos_y = 1395, 335
buy_button_pos_x, buy_button_offset_y = 1328, 55
ok_button_pos_x, ok_button_pos_y = 961, 570
cache_price_icons_list = []
cache_price_recognized = []

search_sleep_time = 0.4
OK_time_sleep = 0.7
move_mouse_time_sleep = 0.02
click_sleep_time = 0.02
buy_lot_button_anim_time = 0
page_swap_anim_time = 0.4

distance_between_page_numbers = 24

First_page_image = Image.open("page1.png")
First_page_image_untouch = Image.open("page1_untouch.png")
First_page_coords = (980, 765, 170, 18)
First_page_image_touched = True

FirstPageButtonCoords = []

page -= 1

def Search():
    global First_page_image_touched
    move_mouse(search_button_position_x, search_button_position_y)
    pyautogui.click()
    time.sleep(search_sleep_time)
    First_page_image_touched = True

def screenshot():
    return pyautogui.screenshot(region=(x_screenshot, y_screenshot, screenshot_size_x, screenshot_size_y))

def cut(image, xoffset, yoffset, xsize, ysize):
    images = []
    for i in range(lots_count):
        images.append(image.crop((xoffset, i * good_line_size_y + (yoffset), xoffset + xsize, i * good_line_size_y + (yoffset) + ysize)))
        #im.save("img/test/croptest_"+str(i)+".jpg")
    return images

def preprocess_image(image, target_size=(128, 128)):
    # Чтение изображения в градациях серого
    #image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # Преобразование изображения в оттенки серого
    preprocessed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Изменение размера изображения
    preprocessed_image = cv2.resize(preprocessed_image, target_size)
    # Бинаризация изображения (черно-белое)
    _, preprocessed_image = cv2.threshold(preprocessed_image, 128, 255, cv2.THRESH_BINARY)
    # Добавление канала и создание трехканального изображения
    preprocessed_image = np.expand_dims(preprocessed_image, axis=-1)
    preprocessed_image = np.repeat(preprocessed_image, 3, axis=-1)
    return Image.fromarray(preprocessed_image)

def recognize_image(image, psm_config, whitelist):
    #starttime = time.time()
    #with PyTessBaseAPI(psm=PSM.SINGLE_WORD, lang='rus') as api:
    with PyTessBaseAPI(psm = psm_config, lang = 'rus') as api:
        api.SetImage(image)
        api.SetVariable('tessedit_char_whitelist', whitelist)
        api.SetVariable("debug_file", "/dev/null")

        cache = api.GetUTF8Text()
        if len(cache) > 0:
            return cache
        return "None"
    
def FindAndClickFirstPageButton():
    try:
        global First_page_image_touched
        global FirstPageButtonCoords
        #FirstPageButtonCoords = pyautogui.locateCenterOnScreen('page1.png')
        
        if (First_page_image_touched):
            FirstPageButtonCoords = pyautogui.center(pyautogui.locateOnScreen(First_page_image, First_page_coords))
            First_page_image_touched = False
        else: FirstPageButtonCoords = pyautogui.center(pyautogui.locateOnScreen(First_page_image_untouch, First_page_coords))

        ClickPageButton(FirstPageButtonCoords[0] + distance_between_page_numbers * page, FirstPageButtonCoords[1])
        return True

    except:
        return False
    
def ClickPageButton(x, y):
    move_mouse(x, y)
    mouse_click()
    time.sleep(page_swap_anim_time)

def AnalizePage():
    screen = screenshot()
    cuttedprices = cut(screen, x_price_offset, y_price_offset, price_size_x, price_size_y )
    #screen.save("screens/screen_" + str(iteration) + ".jpg")
    if FindLowerPrice(cuttedprices):
        #print()
        #print('PRICE FOUNDED')
        #print()
        #logfile.write('\n' + 'PRICE FOUNDED' + '\n' + '\n')    
        return(True)
    #print()
    #print('!!! PAGE IS EMPTY !!!')
    #print()
    #logfile.write('\n' + "!!! PAGE IS EMPTY !!!" + '\n' + '\n')
    #founded_pricec_log.write('\n' + "!!! PAGE IS EMPTY !!!" + '\n' + '\n')
    return False

def FindLowerPrice(prices_images):
    for i in range(len(prices_images)):
        #print("Price number  " + str(i))
        #logfile.write("Price number  " + str(i) + '\n')

        try:
            index = cache_price_icons_list.index(prices_images[i])
            recognized_price = cache_price_recognized[index]
        except:
            cache_price_icons_list.append(prices_images[i])

            priceicon = preprocess_image(np.array(prices_images[i]), (512, 150))
            recognized_price = recognize_image(priceicon, 7, '').strip()
        
            #print("text on image = " + recognized_price)
            #logfile.write("text on image = " + recognized_price + '\n')

            recognized_price = clearprice(recognized_price)

            cache_price_recognized.append(recognized_price)
            #price_cache_file.write(str(recognized_price) + '\n')

        #print("int on image = " + str(recognized_price))
        #logfile.write("int on image = " + str(recognized_price) + '\n' + '\n')

        #priceicon.save("priceicons/priceicon_iteration_" + str(iteration) + "_priceicon_" + str(i) + ".jpg")
        if recognized_price == -1: continue

        if recognized_price > buyoutprice: return(True)

        #print()
        #print("!!! LOWER PRICE FOUNDED !!! " + str(recognized_price) + " rub")
        #print()
        #logfile.write('\n' + "!!! LOWER PRICE FOUNDED !!! " + str(recognized_price) + " rub" + '\n' + '\n')
        #founded_pricec_log.write(str(recognized_price) + ' iteration_' + str(iteration) + "_priceicon_" + str(i) + '\n')

        #priceicon.save("priceicons/priceicon_iteration_" + str(iteration) + "_priceicon_" + str(i) + ".jpg")

        BuyLot(i, recognized_price)
        return(True)
    return False

def BuyLot(lot_number, recognized_price):
    move_mouse(x_screenshot + good_line_loxal_coord_x, (y_screenshot + good_line_local_coord_y + lot_number * good_line_size_y))
    mouse_click()
    move_mouse(buy_button_pos_x, (y_screenshot + lot_number * good_line_size_y + buy_button_offset_y))
    time.sleep(buy_lot_button_anim_time)
    mouse_click()
    #PurchaseCheck(recognized_price)
    ClickOK()
    Search()

    
def PurchaseCheck(recognized_price):
    try:
        _coords = pyautogui.locateCenterOnScreen('Lot_Purchased.png')
        #founded_pricec_log.write(str(recognized_price) + '\n')
        #founded_pricec_log.write('Purchased' + '\n' + '\n')
        #logfile.write('Purchased' + '\n' + '\n')
    except:
        #logfile.write('Purchase FAILED' + '\n' + '\n')
        pass

def ClickOK():
    move_mouse(ok_button_pos_x, ok_button_pos_y)
    time.sleep(OK_time_sleep)
    mouse_click()
    

def clearprice(priceRaw):
        price = ""
        for i in priceRaw:
            try:
                c = int(i)
                price += i
            except:
                continue
        try:
            return int(price)
        except:
            return (-1)


def move_mouse(x, y):
    pyautogui.moveTo(x, y)
    time.sleep(move_mouse_time_sleep)

def mouse_click():
    pyautogui.click()
    time.sleep(click_sleep_time)

def mouse_down():
    pyautogui.mouseDown()

def mouse_up():
    pyautogui.mouseUp()

def drag_mouse(dx, dy):
    sleeptime = 0.05
    dragtime = 0.2

    pyautogui.mouseDown()
    time.sleep(sleeptime)
    pyautogui.mouseDown()
    time.sleep(sleeptime)
    pyautogui.mouseDown()
    time.sleep(sleeptime)
    
    pyautogui.moveTo(dx, dy, dragtime)

    pyautogui.mouseUp()
    time.sleep(sleeptime)
    pyautogui.mouseUp()
    time.sleep(sleeptime)
    pyautogui.mouseUp()
    time.sleep(sleeptime)


time_start = time.time()
time.sleep(3)
iteration = 1

Search()

#logfile = open("log.txt", "w")
#founded_pricec_log = open("founded_pricec_log.txt", "w")
#price_cache_file = open("price_cache_file.txt", "w")

while True:
    #print("Iteration " + str(iteration))
    #print()
    #logfile.write("Iteration " + str(iteration) + '\n' + '\n')

    if iteration % 50 == 0:
        ClickOK()
        Search()
    iteration += 1  

    if (not FindAndClickFirstPageButton()) : continue

    AnalizePage()

    #ClickPageButton(FirstPageButtonCoords[0], FirstPageButtonCoords[1])

    #screenshot().save("priceicons/priceicon_iteration" + str(iteration) + ".jpg")
    #logfile.flush()
    #os.fsync(logfile.fileno())
    #founded_pricec_log.flush()
    #os.fsync(founded_pricec_log.fileno())
    #price_cache_file.flush()
    #os.fsync(price_cache_file.fileno())