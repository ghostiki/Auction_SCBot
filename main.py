import pyautogui
import time
from PIL import Image
import cv2
import numpy as np
from tesserocr import PyTessBaseAPI, PSM, RIL
import os
import glob
import os
import requests
import keyboard
import threading
import subprocess
import datetime
import random
import pygetwindow
from dotenv import load_dotenv

load_dotenv()

# BOT CONTROL START
# configure settings
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
paths = ["C:/Other/Steam/steam.exe", "D:/Steam/steam.exe",
         "C:/Program Files (x86)/Steam/steam.exe"]
items = ['Продвинутые запчасти']
items_prices = [58500]
item_index = 0
steam_path = paths[2]
auction_button = 'k'
end_button = 'f6'
# the higher, the longer the algorithm will not use updating mechanics
refresh_algorithm_coef = 4

IsUseCache = True
IsSaveImageInCache = False

# DISCORD WEBHOOK

WEBHOOK_URL = f"{os.getenv('YOUR_WEBHOOK_URL')}"
WEBHOOK_USERNAME = "Аукционист"
AVATAR_URL = f"{os.getenv('YOUR_AVATAR_URL')}"

# VARIABLES

prices_list = []
price_per_one_test = 0
start_balance_test = 0
restart_timer = 3600
count_of_page_refreshes_after_buy_lot = 1
clickOK_iterations = 10
pyautogui.PAUSE = 0.0001
pyautogui.FAILSAFE = False

# DELAYS

pre_click_delay = 0.05
pre_mouse_move_delay = 0.05
page_post_load_anim_time = 0.2
delay_after_click_page_when_find_page_and_scroll = 0.6
start_bot_sleep_time = 1
# mouse_move_time = 0.005

# drag mouse delays
before_click_scroll_delay = 0.05
after_drag_scroll_delay = 0.05
mouse_down_sleep_time = 0.01
mouse_drag_delta_time = 0.101

# Restart game delays
delay_after_close_game = 10
delay_load_characters_from_server = 15
delay_join_game_connection = 15
open_game_time = 25
delay_pre_join_game_click = 1

# PDA delays
delay_auction_action = 0.5
delay_open_PDA = 2
delay_open_auction = 1

# Click OK delays
delay_pre_clickOK_position = 0.1
Find_OK_Button_Delay = 0.1
delay_refresh_page_after_clickOK_time = 0.4

# Find page and scroll delays
before_click_scroll_delay_when_find_scroll = 0.1
after_drag_scroll_delay_when_find_scroll = 0.1

# BOT CONTROL END

previous_balance = 0
success_buy_lot_count = 0
fail_buy_lot_count = 0

buyoutprice = items_prices[item_index]
item_name = items[item_index]

lots_count = 10
scroll_offset = [81, 162, 243, 324, 360]

dir = os.path.dirname(os.path.abspath(__file__))

PageButtonCoords = []
current_page = 0
current_scroll = 0
current_lot = 0

steam_app_id = "1818450"
command = [steam_path, "-applaunch", steam_app_id]

ServerRestartTime = datetime.datetime(2024, 7, 10, 2, 0, 0)
isServerRestarted = False

start_time = datetime.datetime.now().strftime("%H:%M:%S")
start_time_diff = datetime.datetime.now()

FAIL_Buy = Image.open(dir + '/Images/Fail_Buy.png')
SUCCESS_Buy = Image.open(dir + '/Images/Success_Buy.png')
OK_Button = Image.open(dir + '/Images/OK_Button.png')
# BuyLot_Button = Image.open(dir + '/Images/BuyLot_Button.png')
AuctionImage = Image.open(dir + '/Images/Auction.png')

x_balance, y_balance, balance_size_x, balance_size_y = 1170, 802, 225, 25
x_screenshot, y_screenshot, screenshot_size_x, screenshot_size_y = 1240, 385, 135, 370
pages_images_screenshot_space = (980, 755, 170, 25)
x_price_offset, y_price_offset, price_size_x, price_size_y = 5, 2, 135, 30
good_line_size_y = 37
good_line_local_coord_y = good_line_size_y / 2
scroller_pos_x, scroller_pos_y = 1395, 335
offsets_in_scroll_for_buy_button = [55, 45.25, 35.5, 25.75, 16, 6.25]
buy_button_pos_x, buy_button_offset_y = 1328, offsets_in_scroll_for_buy_button[0]
ok_button_pos_x, ok_button_pos_y = 961, 570
join_game_button_x, join_game_button_y = 960, 880
# player_button_x, player_button_y = 1540, 310
lot_name_window_x, lot_name_window_y = 1272, 336
sort_lots_button_x, sort_lots_button_y = 1300, 373
auction_button_x, auction_button_y = 560, 406
lot_pos_x = 1272

Page_images = []
Page_images_touched = []

if not IsUseCache:
    IsSaveImageInCache = False

for page_icon in glob.glob(dir + '/Pages/*.png'):
    Page_images.append(Image.open(page_icon))
for page_touched_icon in glob.glob(dir + '/Pages_touched/*.png'):
    Page_images_touched.append(Image.open(page_touched_icon))

cache_prices = []
cache_prices_images = []
if IsUseCache:
    for cache_price in glob.glob(dir + '/cache_prices/*.png'):
        cache_prices_image = Image.open(cache_price)
        cache_prices.append(cache_price)
        cache_prices_images.append(cache_prices_image)


def screenshot():
    return pyautogui.screenshot(region=(x_screenshot, y_screenshot, screenshot_size_x, screenshot_size_y))


def balance_acc():
    return pyautogui.screenshot(region=(x_balance, y_balance, balance_size_x, balance_size_y))


def cut(image, xoffset, yoffset, xsize, ysize):
    images = []
    for i in range(lots_count):
        images.append(image.crop((xoffset, i * good_line_size_y + (yoffset),
                      xoffset + xsize, i * good_line_size_y + (yoffset) + ysize)))
        # im.save("img/test/croptest_"+str(i)+".jpg")
    return images


def preprocess_image(image, target_size=(128, 128)):
    # Чтение изображения в градациях серого
    # image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # Преобразование изображения в оттенки серого
    preprocessed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Изменение размера изображения
    preprocessed_image = cv2.resize(preprocessed_image, target_size)
    # Бинаризация изображения (черно-белое)
    # _, preprocessed_image = cv2.threshold(
    #     preprocessed_image, 128, 255, cv2.THRESH_BINARY)
    # Добавление канала и создание трехканального изображения
    preprocessed_image = np.expand_dims(preprocessed_image, axis=-1)
    preprocessed_image = np.repeat(preprocessed_image, 3, axis=-1)
    return Image.fromarray(preprocessed_image)


def recognize_image(image, psm_config, whitelist):
    # with PyTessBaseAPI(psm=PSM.SINGLE_WORD, lang='rus') as api:
    with PyTessBaseAPI(path='Tesserocr\Models', psm=psm_config, lang='rus') as api:
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

        try:
            PageButtonCoords = pyautogui.center(pyautogui.locateOnScreen(
                Page_images_touched[current_page], pages_images_screenshot_space))
        except:
            PageButtonCoords = pyautogui.center(pyautogui.locateOnScreen(
                Page_images[current_page], pages_images_screenshot_space))

        mouse_move(PageButtonCoords[0] + random.randint(-3, 3),
                   PageButtonCoords[1] + random.randint(-3, 3), False)
        mouse_click()
        time.sleep(page_post_load_anim_time)
        return True
    except:
        return False


def AnalizePage():
    if (current_scroll != 0):
        mouse_move(scroller_pos_x, scroller_pos_y)
        drag_mouse(None, scroller_pos_y + scroll_offset[current_scroll - 1])
        time.sleep(after_drag_scroll_delay)

    screen = screenshot()
    cuttedprices = CutPrices(screen)
    return TryBuyLot(cuttedprices[current_lot])


def DetermineImageValue(Image):
    try:
        index = cache_prices_images.index(Image)
        recognized_price = cache_prices[index]
    except:
        cache_prices_images.append(Image)

        priceicon = preprocess_image(np.array(Image), (512, 150))
        recognized_price = recognize_image(priceicon, 7, '').strip()

        # print("text on image = " + recognized_price)
        # logfile.write("text on image = " + recognized_price + '\n')

        recognized_price = ClearPrice(recognized_price)

        cache_prices.append(recognized_price)
        # price_cache_file.write(str(recognized_price) + '\n')

        SaveImageInCache(Image, recognized_price)
    return recognized_price


def DetermineImageValueBalance(Image):
    try:
        index = cache_prices_images.index(Image)
        recognized_price = cache_prices[index]
    except:
        cache_prices_images.append(Image)

        priceicon = preprocess_image(np.array(Image), (1000, 100))
        recognized_price = recognize_image(priceicon, 7, '').strip()

        # print("text on image = " + recognized_price)
        # logfile.write("text on image = " + recognized_price + '\n')

        recognized_price = ClearPrice(recognized_price)

        cache_prices.append(recognized_price)
        # price_cache_file.write(str(recognized_price) + '\n')

        SaveImageInCache(Image, recognized_price)
    return recognized_price


def TryBuyLot(image):
    recognized_price = DetermineImageValue(image)

    if recognized_price == -1:
        return False
    if recognized_price > buyoutprice:
        return False

    # print()
    # print("!!! LOWER PRICE FOUNDED !!! " + str(recognized_price) + " rub")
    # print()
    # logfile.write('\n' + "!!! LOWER PRICE FOUNDED !!! " + str(recognized_price) + " rub" + '\n' + '\n')
    # founded_pricec_log.write(str(recognized_price) + ' iteration_' + str(iteration) + "_priceicon_" + str(i) + '\n')

    # priceicon.save("priceicons/priceicon_iteration_" + str(iteration) + "_priceicon_" + str(i) + ".jpg")

    BuyLot(current_lot, recognized_price)
    return True


def FindFirstLotWithPrice(prices_images):
    global current_lot

    for i in range(len(prices_images)):
        current_lot = i
        # print("Price number  " + str(i))
        # logfile.write("Price number  " + str(i) + '\n')

        recognized_price = DetermineImageValue(prices_images[i])

        # print("int on image = " + str(recognized_price))
        # logfile.write("int on image = " + str(recognized_price) + '\n' + '\n')

        # priceicon.save("priceicons/priceicon_iteration_" + str(iteration) + "_priceicon_" + str(i) + ".jpg")
        if recognized_price == -1:
            if DetermineImageValue(prices_images[9]) != -1 and DetermineImageValue(prices_images[8]) == -1:
                return False
            continue
        return True
    return False


def SaveImageInCache(image, price):
    if (IsSaveImageInCache):
        image.save('cache_prices/' + str(price) + '.png')


def BuyLot(lot_number, recognized_price):
    global success_buy_lot_count
    global fail_buy_lot_count
    mouse_move(lot_pos_x, (y_screenshot + good_line_local_coord_y +
               lot_number * good_line_size_y), False)
    mouse_click()
    mouse_move(buy_button_pos_x, (y_screenshot + lot_number *
               good_line_size_y + buy_button_offset_y))
    mouse_click()
    time.sleep(0.5)
    if (FindImage(SUCCESS_Buy)):
        success_buy_lot_count += 1
        screen = balance_acc()
        global balance
        balance = DetermineImageValueBalance(screen)
        global formatted_balance
        formatted_balance = "{:,}".format(balance).replace(",", ".")
        buy_to_discord(success_buy_lot_count, fail_buy_lot_count, WEBHOOK_URL)
        global previous_balance
        previous_balance = DetermineImageValueBalance(screen)
        if balance < items_prices[item_index]:
            balance_end_to_discord(WEBHOOK_URL)
            global running
            running = False
            end_to_discord(WEBHOOK_URL)
            os._exit(0)
    elif (FindImage(FAIL_Buy)):
        fail_buy_lot_count += 1
    ClickOK()


def time_diff():
    current_time_diff = datetime.datetime.now()
    time_diff = current_time_diff - start_time_diff
    total_seconds = time_diff.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    formatted_diff = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return formatted_diff


def buy_to_discord(number_success, number_fail, webhook_url):
    global price_per_one_test
    global prices_list
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    time = time_diff()
    losted_money = start_balance - balance
    if price_per_one_test == 1:
        price_per_one = previous_balance - balance
    elif price_per_one_test == 0:
        price_per_one = start_balance - balance
        price_per_one_test += 1
    average_price = int(losted_money / number_success)
    prices_list.append(price_per_one)
    min_price = min(prices_list)
    max_price = max(prices_list)
    formatted_min_price = "{:,}".format(min_price).replace(",", ".")
    formatted_max_price = "{:,}".format(max_price).replace(",", ".")
    formatted_average_price = "{:,}".format(average_price).replace(",", ".")
    formatted_price_per_one = "{:,}".format(price_per_one).replace(",", ".")
    formatted_lost_money = "{:,}".format(losted_money).replace(",", ".")

    data = {
        "username": f"{WEBHOOK_USERNAME}",
        "avatar_url": f"{AVATAR_URL}",
        "embeds": [
            {
                "title": f"**[{current_time}]** Куплено: {items[item_index]} (за `{formatted_price_per_one}₽`)",
                "description": f"⚡ **Начало »** `[{start_time}]`\n⏱️ **Длительность »** `[{time}]`\n💳 **Баланс »** `[{formatted_balance}₽]`",
                "color": 0x00ff00,
                "fields": [
                    {"name": "✅ **Успешных:**",
                        "value": f"`{number_success}`", "inline": True},
                    {"name": "❌ **Неудачных:**",
                        "value": f"`{number_fail}`", "inline": True},
                    {"name": "💰 **Потрачено:**",
                        "value": f"`{formatted_lost_money}₽`", "inline": True}
                ],
                "footer": {"text": f"📊 Статистика:\nСредняя цена: {formatted_average_price}₽\nМакс. цена: {formatted_max_price}₽\nМин. цена: {formatted_min_price}₽"}
            }
        ]
    }

    response = requests.post(webhook_url, json=data)


def restart_to_discord(webhook_url):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    time = time_diff()

    data = {
        "username": f"{WEBHOOK_USERNAME}",
        "avatar_url": f"{AVATAR_URL}",
        "embeds": [
            {
                "title": f"**[{current_time}]** Перезапуск игры 🔄",
                "description": f"⚡ **Начало »** `[{start_time}]`\n⏱️ **Длительность »** `[{time}]`\n💳 **Баланс »** `[{formatted_balance}₽]`",
                "color": 0x0000ff,
                "footer": {"text": f"Производится каждые {restart_timer/60} минут"}
            }
        ]
    }

    response = requests.post(webhook_url, json=data)


def crash_to_discord(webhook_url):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    time = time_diff()

    data = {
        "username": f"{WEBHOOK_USERNAME}",
        "avatar_url": f"{AVATAR_URL}",
        "embeds": [
            {
                "title": f"**[{current_time}]** Краш игры 💥",
                "description": f"⚡ **Начало »** `[{start_time}]`\n⏱️ **Длительность »** `[{time}]`\n💳 **Баланс »** `[{formatted_balance}₽]`",
                "color": 0xff0000,
            }
        ]
    }

    response = requests.post(webhook_url, json=data)


def balance_end_to_discord(webhook_url):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    time = time_diff()

    data = {
        "username": f"{WEBHOOK_USERNAME}",
        "avatar_url": f"{AVATAR_URL}",
        "embeds": [
            {
                "title": f"**[{current_time}]** Баланс закончился 📉",
                "description": f"⚡ **Начало »** `[{start_time}]`\n⏱️ **Длительность »** `[{time}]`\n💳 **Баланс »** `[{formatted_balance}₽]`",
                "color": 0xffff00,
            }
        ]
    }

    response = requests.post(webhook_url, json=data)


def start_to_discord(webhook_url):
    data = {
        "username": f"{WEBHOOK_USERNAME}",
        "avatar_url": f"{AVATAR_URL}",
        "embeds": [
            {
                "title": f"**[{start_time}]** Начало работы {WEBHOOK_USERNAME}(-a) 🟢",
                "description": f"⚡ **Начало »** `[{start_time}]`0",
                "color": 0xffffff,
            }
        ]
    }

    response = requests.post(webhook_url, json=data)


def end_to_discord(webhook_url):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    time = time_diff()

    try:
        data = {
            "username": f"{WEBHOOK_USERNAME}",
            "avatar_url": f"{AVATAR_URL}",
            "embeds": [
                {
                    "title": f"**[{current_time}]** Завершение работы {WEBHOOK_USERNAME}(-a) 🔴",
                    "description": f"⚡ **Начало »** `[{start_time}]`\n⏱️ **Длительность »** `[{time}]`\n💳 **Баланс »** `[{formatted_balance}₽]`",
                    "color": 0xffffff,
                }
            ]
        }

    except:
        data = {
            "username": f"{WEBHOOK_USERNAME}",
            "avatar_url": f"{AVATAR_URL}",
            "embeds": [
                {
                    "title": f"**[{current_time}]** Завершение работы {WEBHOOK_USERNAME}(-a) 🔴",
                    "description": f"⚡ **Начало »** `[{start_time}]`\n⏱️ **Длительность »** `[{time}]`\n💳 **Баланс »** `[{formatted_start_balance}₽]`",
                    "color": 0xffffff,
                }
            ]
        }

    response = requests.post(webhook_url, json=data)


def FindPageAndScroll():
    global buy_button_offset_y
    global current_page
    global current_scroll

    for i in range(len(Page_images)):
        current_page = i
        current_scroll = 0
        buy_button_offset_y = offsets_in_scroll_for_buy_button[0]
        FindAndClickPageButton()
        time.sleep(delay_after_click_page_when_find_page_and_scroll)
        screen = screenshot()
        cuttedprices = CutPrices(screen)
        if FindFirstLotWithPrice(cuttedprices):
            break
        mouse_move(scroller_pos_x, scroller_pos_y, False)
        time.sleep(before_click_scroll_delay_when_find_scroll)
        pyautogui.mouseDown()
        time.sleep(mouse_down_sleep_time)

        for i in range(len(scroll_offset)):
            current_scroll += 1
            buy_button_offset_y = offsets_in_scroll_for_buy_button[i + 1]
            pyautogui.moveTo(None, scroller_pos_y +
                             scroll_offset[i], mouse_drag_delta_time)
            time.sleep(after_drag_scroll_delay_when_find_scroll)
            screen = screenshot()
            cuttedprices = CutPrices(screen)
            if FindFirstLotWithPrice(cuttedprices):
                break
        else:
            continue
        pyautogui.mouseUp()
        time.sleep(mouse_down_sleep_time)
        break

    buy_button_offset_y = offsets_in_scroll_for_buy_button[current_scroll]


def CutPrices(screenshot):
    return cut(screenshot, x_price_offset, y_price_offset, price_size_x, price_size_y)


def ClickOK_Position():
    mouse_move(ok_button_pos_x, ok_button_pos_y)
    time.sleep(delay_pre_clickOK_position)
    mouse_click(False)


def ClickOK():
    _isOKFounded = False
    for i in range(clickOK_iterations):
        if (FindImage(OK_Button)):
            _isOKFounded = True
            break
        time.sleep(Find_OK_Button_Delay)
    if _isOKFounded:
        ClickOK_Position()
        time.sleep(delay_refresh_page_after_clickOK_time)
    MultipleRefreshPage()


def MultipleRefreshPage():
    for i in range(count_of_page_refreshes_after_buy_lot):
        FindAndClickPageButton()


def ClearPrice(priceRaw):
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


def mouse_move(x, y, isNeedInitialDelay=True):
    if isNeedInitialDelay:
        time.sleep(pre_mouse_move_delay)
    pyautogui.moveTo(x, y, _pause=False)
    # pyautogui.moveTo(x, y, _pause = mouse_move_time)


def mouse_click(isNeedInitialDelay=True):
    if isNeedInitialDelay:
        time.sleep(pre_click_delay)
    pyautogui.click()


def drag_mouse(dx, dy, isNeedInitialDelay=True):
    if isNeedInitialDelay:
        time.sleep(before_click_scroll_delay)
    pyautogui.mouseDown()
    time.sleep(mouse_down_sleep_time)
    pyautogui.moveTo(dx, dy, mouse_drag_delta_time)
    time.sleep(after_drag_scroll_delay)
    pyautogui.mouseUp()
    time.sleep(mouse_down_sleep_time)


def OpenAuction():
    keyboard.press_and_release(auction_button)
    time.sleep(delay_open_PDA)
    mouse_move(auction_button_x, auction_button_y)
    time.sleep(delay_auction_action)
    mouse_click()
    time.sleep(delay_open_auction)
    mouse_move(lot_name_window_x, lot_name_window_y)
    time.sleep(delay_auction_action)
    mouse_click()
    time.sleep(delay_auction_action)
    keyboard.write(item_name)
    time.sleep(delay_auction_action)
    mouse_move(sort_lots_button_x, sort_lots_button_y)
    time.sleep(delay_auction_action)
    mouse_click()
    time.sleep(delay_auction_action)
    mouse_click()
    time.sleep(delay_auction_action)
    global start_balance_test
    if start_balance_test == 0:
        screen = balance_acc()
        global start_balance
        start_balance = DetermineImageValueBalance(screen)
        global formatted_start_balance
        formatted_start_balance = "{:,}".format(
            start_balance).replace(",", ".")
        start_balance_test += 1
    # print("Аукцион готов к торгам")


def FindImage(IconImage):
    try:
        pyautogui.locateCenterOnScreen(IconImage)
        return True
    except:
        return False


def CloseGame():
    try:
        # Пытаемся закрыть игру
        result = os.system("taskkill /f /im stalcraftw.exe")

        if result == 0:  # Успешное закрытие
            restart_to_discord(WEBHOOK_URL)
            return True

        else:
            crash_to_discord(WEBHOOK_URL)
            return False

    except Exception as e:
        crash_to_discord(WEBHOOK_URL)
        return False


def OpenGame():
    subprocess.run(command)
    # print("Выполнена команда стима для запуска игры")
    time.sleep(open_game_time)
    # print("Игра запустилась")


def RestartGame():
    # print("Начало перезапуска игры")
    CloseGame()
    time.sleep(delay_after_close_game)
    OpenGame()
    time.sleep(delay_load_characters_from_server)
    # mouse_move(player_button_x, player_button_y)
    # time.sleep(delay_pre_join_game_click)
    mouse_move(join_game_button_x, join_game_button_y)
    time.sleep(delay_pre_join_game_click)
    mouse_click()
    time.sleep(delay_join_game_connection)
    OpenAuction()


def key_listener():
    global running
    keyboard.wait(f'{end_button}')
    running = False
    end_to_discord(WEBHOOK_URL)
    os._exit(0)


def main():
    global running
    iteration = 0
    last_restart_time = time.time()

    try:
        target_window = pygetwindow.getWindowsWithTitle("STALCRAFT")[0]
        target_window.activate()
    except:
        pass

    time.sleep(start_bot_sleep_time)

    OpenAuction()

    # logfile = open("log.txt", "w")
    # founded_pricec_log = open("founded_pricec_log.txt", "w")
    # price_cache_file = open("price_cache_file.txt", "w")

    while running:
        iteration += 1
        current_time = time.time()
        # print("Iteration " + str(iteration))
        # print()
        # logfile.write("Iteration " + str(iteration) + '\n' + '\n')

        if current_time - last_restart_time >= restart_timer:
            RestartGame()
            last_restart_time = time.time()  # Обновляем время последнего перезапуска
            iteration = 0
            continue

        if (iteration) % (100 * refresh_algorithm_coef) == 0:
            if (not FindImage(AuctionImage)):
                RestartGame()
                iteration = 0
                continue

        if (iteration) % (3000 * refresh_algorithm_coef) == 0:
            RestartGame()
            continue

        if (iteration - 1) % (25 * refresh_algorithm_coef) == 0:
            ClickOK_Position()
            FindPageAndScroll()
            continue

        if (not FindAndClickPageButton()):
            continue

        AnalizePage()

        # screenshot().save("priceicons/priceicon_iteration" + str(iteration) + ".jpg")
        # logfile.flush()
        # os.fsync(logfile.fileno())
        # founded_pricec_log.flush()
        # os.fsync(founded_pricec_log.fileno())
        # price_cache_file.flush()
        # os.fsync(price_cache_file.fileno())


if __name__ == "__main__":
    running = True

    start_to_discord(WEBHOOK_URL)

    key_thread = threading.Thread(target=key_listener)
    key_thread.start()

    main()

    key_thread.join()
