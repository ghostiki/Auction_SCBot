import pyautogui
import time
from PIL import Image
import cv2
import numpy as np
from tesserocr import PyTessBaseAPI, PSM, RIL
import os
import glob
import os
import keyboard

# BOT CONTROL START
items = ['продвинутые зап', 'запас']
items_prices = [50000, 26000]
item_index = 0
IsSaveImageInCache = False
refresh_algorithm_coef = 2
# BOT CONTROL END   

buyoutprice = items_prices[item_index]
item_name = items[item_index]

lots_count = 10
scroll_offset = [90, 180, 269, 360]

dir = os.path.dirname(os.path.abspath(__file__))

#OLD Version
#x_screenshot, y_screenshot, screenshot_size_x, screenshot_size_y = 889, 385, 513, 369
#x_price_offset, y_price_offset, price_size_x, price_size_y = 355, 2, 135, 30
#good_line_size_y = 36
x_screenshot, y_screenshot, screenshot_size_x, screenshot_size_y = 1240, 385, 135, 370
x_price_offset, y_price_offset, price_size_x, price_size_y = 0, 2, 135, 30
good_line_size_y = 37
good_line_local_coord_x, good_line_local_coord_y = screenshot_size_x / 2, good_line_size_y / 2
search_button_position_x, search_button_position_y = 1337, 337
scroller_pos_x, scroller_pos_y = 1395, 335
offsets_in_scroll_for_buy_button = [55, 45.25, 35.5, 25.75, 16]
buy_button_pos_x, buy_button_offset_y = 1328, offsets_in_scroll_for_buy_button[0]
ok_button_pos_x, ok_button_pos_y = 961, 570
exit_game_button_x, exit_game_button_y = 1640, 70
socket_exception_button_x, socket_exception_button_y = 960, 100
join_game_button_x, join_game_button_y = 960, 860
lot_name_window_x, lot_name_window_y = 1200, 336
sort_lots_button_x, sort_lots_button_y = 1300, 373
auction_button_x, auction_button_y = 560, 406

# PC
search_sleep_time = 0.4
OK_time_sleep = 0.7
move_mouse_sleep_time = 0.01
click_sleep_time = 0.01
buy_lot_button_anim_time = 0.02
page_pre_load_anim_time = 0
page_post_load_anim_time = 0.3
refresh_page_after_click_OK_time = 0.1
mouse_down_sleep_time = 0.01
mouse_drag_down_sleep_time = 0.03

# SLOW HARDWARE
# search_sleep_time = 0.4
# OK_time_sleep = 0.7
# move_mouse_sleep_time = 0.02
# click_sleep_time = 0.02
# buy_lot_button_anim_time = 0.05
# page_pre_load_anim_time = 0
# page_post_load_anim_time = 0.3
# refresh_page_after_click_OK_time = 0.3
# mouse_down_sleep_time = 0.02
# mouse_drag_down_sleep_time = 0.05

Page_images = []
Page_images_touched = []

for page_icon in glob.glob(dir + '/Pages/*.png'):
    Page_images.append(Image.open(page_icon))
for page_touched_icon in glob.glob(dir + '/Pages_touched/*.png'):
    Page_images_touched.append(Image.open(page_touched_icon))

First_page_coords = (980, 755, 170, 25)

cache_prices = []
cache_prices_images = []
for cache_price in glob.glob(dir + '/cache_prices/*.png'):
    cache_prices_image = Image.open(cache_price)
    cache_prices.append(cache_price)
    cache_prices_images.append(cache_prices_image)

PageButtonCoords = []
page = 0
current_scroll = 0

def Search():
    move_mouse(search_button_position_x, search_button_position_y)
    pyautogui.click()
    time.sleep(search_sleep_time)

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
    
def FindAndClickPageButton():
    try:
        global PageButtonCoords
        #PageButtonCoords = pyautogui.locateCenterOnScreen('page1.png')

        time.sleep(page_pre_load_anim_time)

        try:
            PageButtonCoords = pyautogui.center(pyautogui.locateOnScreen(Page_images_touched[page], First_page_coords))
        except:
            PageButtonCoords = pyautogui.center(pyautogui.locateOnScreen(Page_images[page], First_page_coords))

        move_mouse(PageButtonCoords[0], PageButtonCoords[1])
        mouse_click()

        time.sleep(page_post_load_anim_time)

        return True
    except:
        return False

def AnalizePage():
    if (current_scroll != 0):
        move_mouse(scroller_pos_x, scroller_pos_y)
        drag_mouse(None, scroller_pos_y + scroll_offset[current_scroll - 1])

    screen = screenshot()
    cuttedprices = CutPrices(screen)
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
            index = cache_prices_images.index(prices_images[i])
            recognized_price = cache_prices[index]
        except:
            cache_prices_images.append(prices_images[i])

            priceicon = preprocess_image(np.array(prices_images[i]), (512, 150))
            recognized_price = recognize_image(priceicon, 7, '').strip()
        
            #print("text on image = " + recognized_price)
            #logfile.write("text on image = " + recognized_price + '\n')

            recognized_price = clearprice(recognized_price)

            cache_prices.append(recognized_price)
            #price_cache_file.write(str(recognized_price) + '\n')

            SaveImageInCache(prices_images[i], recognized_price)

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

def SaveImageInCache(image, price):
    if (IsSaveImageInCache):
        image.save('cache_prices/' + str(price) + '.png')

def BuyLot(lot_number, recognized_price):
    move_mouse(x_screenshot + good_line_local_coord_x, (y_screenshot + good_line_local_coord_y + lot_number * good_line_size_y))
    mouse_click()
    move_mouse(buy_button_pos_x, (y_screenshot + lot_number * good_line_size_y + buy_button_offset_y))
    time.sleep(buy_lot_button_anim_time)
    mouse_click()
    #PurchaseCheck(recognized_price)
    ClickOK()
    #Search()
    time.sleep(refresh_page_after_click_OK_time)
    
def PurchaseCheck(recognized_price):
    try:
        _coords = pyautogui.locateCenterOnScreen('Lot_Purchased.png')
        #founded_pricec_log.write(str(recognized_price) + '\n')
        #founded_pricec_log.write('Purchased' + '\n' + '\n')
        #logfile.write('Purchased' + '\n' + '\n')
    except:
        #logfile.write('Purchase FAILED' + '\n' + '\n')
        pass

def AnalizeLastScroll():
    move_mouse(scroller_pos_x, scroller_pos_y)
    drag_mouse(None, scroller_pos_y + scroll_offset[-1])
    screen = screenshot()
    cuttedprices = CutPrices(screen)
    if FindLowerPrice(cuttedprices):
        #print()
        #print('PRICE FOUNDED')
        #print()
        #logfile.write('\n' + 'PRICE FOUNDED' + '\n' + '\n')    
        return(True)
    return False

def FindPageAndScroll():
    global buy_button_offset_y
    global page
    global current_scroll

    for i in range(len(Page_images)):
        page = i
        current_scroll = 0
        buy_button_offset_y = offsets_in_scroll_for_buy_button[0]
        FindAndClickPageButton()
        time.sleep(1)
        screen = screenshot()
        cuttedprices = CutPrices(screen)
        if FindLowerPrice(cuttedprices): 
            break
        move_mouse(scroller_pos_x, scroller_pos_y)
        for i in range(len(scroll_offset)):
            current_scroll += 1
            buy_button_offset_y = offsets_in_scroll_for_buy_button[i + 1]
            drag_mouse(None, scroller_pos_y + scroll_offset[i])
            screen = screenshot()
            cuttedprices = CutPrices(screen)
            if FindLowerPrice(cuttedprices): 
                break
        else:
            continue
        break

    buy_button_offset_y = offsets_in_scroll_for_buy_button[current_scroll]

def CutPrices(screenshot):
    return cut(screenshot, x_price_offset, y_price_offset, price_size_x, price_size_y)

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
    time.sleep(move_mouse_sleep_time)

def mouse_click():
    pyautogui.click()
    time.sleep(click_sleep_time)

def mouse_down():
    pyautogui.mouseDown()

def mouse_up():
    pyautogui.mouseUp()

def drag_mouse(dx, dy):

    pyautogui.mouseDown()
    time.sleep(mouse_down_sleep_time)
    #pyautogui.mouseDown()
    #time.sleep(mouse_down_sleep_time)
    #pyautogui.mouseDown()
    #time.sleep(mouse_down_sleep_time)
    
    pyautogui.moveTo(dx, dy, mouse_drag_down_sleep_time)

    pyautogui.mouseUp()
    time.sleep(mouse_down_sleep_time)
    #pyautogui.mouseUp()
    #time.sleep(mouse_down_sleep_time)
    #pyautogui.mouseUp()
    #time.sleep(mouse_down_sleep_time)

def ReloadGame():
    keyboard.press_and_release('esc')
    time.sleep(5)
    keyboard.press_and_release('esc')
    time.sleep(5)
    move_mouse(exit_game_button_x, exit_game_button_y)
    time.sleep(1)
    mouse_click()
    time.sleep(5)
    move_mouse(socket_exception_button_x, socket_exception_button_y)
    time.sleep(1)
    mouse_click()
    time.sleep(5)
    move_mouse(join_game_button_x, join_game_button_y)
    time.sleep(1)
    mouse_click()
    time.sleep(15)
    OpenAuction()
    
def OpenAuction():
    keyboard.press_and_release('h')
    time.sleep(3)
    move_mouse(auction_button_x, auction_button_y)
    time.sleep(1)
    mouse_click()
    time.sleep(1)
    move_mouse(lot_name_window_x, lot_name_window_y)
    time.sleep(1)
    mouse_click()
    time.sleep(1)
    keyboard.write(item_name)
    time.sleep(1)
    move_mouse(sort_lots_button_x, sort_lots_button_y)
    time.sleep(1)
    mouse_click()
    time.sleep(1)
    mouse_click()
    time.sleep(1)

time_start = time.time()
time.sleep(0)
iteration = 0

OpenAuction()

#logfile = open("log.txt", "w")
#founded_pricec_log = open("founded_pricec_log.txt", "w")
#price_cache_file = open("price_cache_file.txt", "w")

while True:
    iteration += 1
    #print("Iteration " + str(iteration))
    #print()
    #logfile.write("Iteration " + str(iteration) + '\n' + '\n')

    if (iteration) % (3000 * refresh_algorithm_coef) == 0:
        ReloadGame()
        continue

    if (iteration - 1) % (100 * refresh_algorithm_coef) == 0:
        FindPageAndScroll()
        continue

    if iteration % (50 * refresh_algorithm_coef) == 0:
        ClickOK()
        Search()
        continue
    
    if (not FindAndClickPageButton()) : continue

    AnalizePage()

    #ClickPageButton(PageButtonCoords[0], PageButtonCoords[1])

    #screenshot().save("priceicons/priceicon_iteration" + str(iteration) + ".jpg")
    #logfile.flush()
    #os.fsync(logfile.fileno())
    #founded_pricec_log.flush()
    #os.fsync(founded_pricec_log.fileno())
    #price_cache_file.flush()
    #os.fsync(price_cache_file.fileno())