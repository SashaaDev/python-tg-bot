import os
import random
import sys

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

import strings as st

def getToken():
    token = ''
    if os.path.isfile(st.BOT_TOKEN_FILENAME):
        with open(st.BOT_TOKEN_FILENAME, "r") as f:
            token = f.read()
    else:
        print("Пожалуйста, создайте в папке проекта файл 'token.txt' и поместите туда токен для работы телеграм бота  и запустите скрипт заново")
        sys.exit()
    return token

def isWin(arr, who):
    if (((arr[0] == who) and (arr[4] == who) and (arr[8] == who)) or
            ((arr[2] == who) and (arr[4] == who) and (arr[6] == who)) or
            ((arr[0] == who) and (arr[1] == who) and (arr[2] == who)) or
            ((arr[3] == who) and (arr[4] == who) and (arr[5] == who)) or
            ((arr[6] == who) and (arr[7] == who) and (arr[8] == who)) or
            ((arr[0] == who) and (arr[3] == who) and (arr[6] == who)) or
            ((arr[1] == who) and (arr[4] == who) and (arr[7] == who)) or
            ((arr[2] == who) and (arr[5] == who) and (arr[8] == who))):
        return True
    return False

def countUndefinedCells(cellArray):
    counter = 0
    for i in cellArray:
        if i == st.SYMBOL_UNDEF:
            counter += 1
    return counter

def game(callBackData):
    message = st.ANSW_YOUR_TURN
    alert = None

    buttonNumber = int(callBackData[0])
    if not buttonNumber == 9:
        charList = list(callBackData)
        charList.pop(0)
        if charList[buttonNumber] == st.SYMBOL_UNDEF:
            charList[buttonNumber] = st.SYMBOL_X
            if isWin(charList, st.SYMBOL_X):
                message = st.ANSW_YOU_WIN
            else:
                if countUndefinedCells(charList) != 0:
                    isCycleContinue = True
                    while (isCycleContinue):
                        rand = random.randint(0, 8)
                        if charList[rand] == st.SYMBOL_UNDEF:
                            charList[rand] = st.SYMBOL_O
                            isCycleContinue = False
                            if isWin(charList, st.SYMBOL_O):
                                message = st.ANSW_BOT_WIN

        else:
            alert = st.ALERT_CANNOT_MOVE_TO_THIS_CELL

        if countUndefinedCells(charList) == 0 and message == st.ANSW_YOUR_TURN:
            message = st.ANSW_DRAW

        callBackData = ''
        for c in charList:
            callBackData += c

    if message == st.ANSW_YOU_WIN or message == st.ANSW_BOT_WIN or message == st.ANSW_DRAW:
        message += '\n'
        for i in range(0, 3):
            message += '\n | '
            for j in range(0, 3):
                message += callBackData[j + i * 3] + ' | '
        callBackData = None

    return message, callBackData, alert

def getKeyboard(callBackData):
    keyboard = [[], [], []]

    if callBackData is not None:
        for i in range(0, 3):
            for j in range(0, 3):
                keyboard[i].append(InlineKeyboardButton(callBackData[j + i * 3], callback_data=str(j + i * 3) + callBackData))

    return keyboard

async def newGame(update: Update, context):
    data = ''.join([st.SYMBOL_UNDEF for _ in range(9)])

    await update.message.reply_text(st.ANSW_YOUR_TURN, reply_markup=InlineKeyboardMarkup(getKeyboard(data)))

async def button(update: Update, context):
    query = update.callback_query
    callbackData = query.data

    message, callbackData, alert = game(callbackData)
    if alert is None:
        await query.answer()
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(getKeyboard(callbackData)))
    else:
        await query.answer(text=alert, show_alert=True)

async def help_command(update: Update, context):
    await update.message.reply_text(st.ANSW_HELP)

if __name__ == '__main__':
    print('Бот запущен. Нажмите Ctrl+C для завершения')

    application = Application.builder().token(getToken()).build()

    application.add_handler(CommandHandler('start', newGame))
    application.add_handler(CommandHandler('new_game', newGame))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT, help_command))

    application.run_polling()
