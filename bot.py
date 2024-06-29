import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters, ContextTypes
from db import Database
from bs4 import BeautifulSoup
from telegram.constants import ParseMode
from html2image import Html2Image
import os
import asyncio
import nest_asyncio
import json
import datetime
import pytz

SECRET_KEY, USERNAME, QUANTITY = range(3)

def read_credentials():
    credentials = {}
    with open('credentials.txt', 'r') as file:
        for line in file:
            key, value = line.strip().split('-->')
            credentials[key] = value
    return credentials

async def myusername_command(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return  
    await update.message.reply_text(f'Username anda adalah :\n\n <code>{username}</code>', parse_mode=ParseMode.HTML) 
    
async def start_command(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    # Menambahkan deskripsi di bawah perintah-perintah bot
    commands_description = [
        "/notes - Untuk menampilkan perintah BOT",
        "/myusername - Untuk menampilkan username anda",
        "/cekquota - Untuk mengecek saldo OTP anda",
        "/beliquota - Topup Saldo OTP",
        "/morinaga - Untuk order nomor OTP MORINAGA",
        "/prenagen - Untuk order nomor OTP PRENAGEN",
        "/sgm - Untuk order nomor OTP SGM",
        "/nutriclub - Untuk order nomor OTP Nutriclub",
        "/entrasol - Untuk order nomor OTP Entrasol / Benecol",
        "/pricelist - Untuk melihat harga layanan",
        "/otpcode - Untuk minta Kode OTP setelah order MORINAGA, PRENAGEN ataupun SGM",
        "/cancelorder - Untuk membatalkan orderan nomor OTP terakhir"
    ]    
    await update.message.reply_text('Halo, selamat datang di OTP BOT, silahkan akses menu berikut untuk memulai\n\n' + '\n'.join(commands_description))

async def notes_command(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    # Menambahkan deskripsi di bawah perintah-perintah bot
    commands_description = [
        "/notes - Untuk menampilkan perintah BOT",
        "/myusername - Untuk menampilkan username anda",
        "/cekquota - Untuk mengecek saldo OTP anda",
        "/beliquota - Topup Saldo OTP",
        "/morinaga - Untuk order nomor OTP MORINAGA",
        "/prenagen - Untuk order nomor OTP PRENAGEN",
        "/sgm - Untuk order nomor OTP SGM",
        "/nutriclub - Untuk order nomor OTP Nutriclub",
        "/entrasol - Untuk order nomor OTP Entrasol / Benecol",
        "/pricelist - Untuk melihat harga layanan",
        "/otpcode - Untuk minta Kode OTP setelah order MORINAGA, PRENAGEN ataupun SGM",
        "/cancelorder - Untuk membatalkan orderan nomor OTP terakhir"
    ]    
    await update.message.reply_text('Halo, selamat datang di OTP BOT, silahkan akses menu berikut untuk memulai\n\n' + '\n'.join(commands_description))

async def notes_admin(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    # Menambahkan deskripsi di bawah perintah-perintah bot
    commands_description = [
        "/notes_admin - Untuk menampilkan perintah BOT Admin",
        "/addquota  - Untuk menambah quota/mendaftarkan ke user terpilih",
        "/deletequota  - Untuk menghapus semua quota user terpilih",
        "/ceksisakartu - Untuk mengecek berapa sisa saldo anda dan kartu anda",
        "/topupsaldokartu - Untuk melakukan topup saldo kartu",
        "/getuser - Untuk melihat username, email dan password"
    ]    
    await update.message.reply_text('Halo, selamat datang di OTP BOT, silahkan akses menu berikut untuk memulai\n\n' + '\n'.join(commands_description))

async def cek_quota(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    await update.message.reply_text('Mohon tunggu sebentar...')
    Database.get_instance().clean_order_user(username)
    quota = Database.get_instance().get_quota(username)
    sisa_saldo = format(quota, ",").replace(",", ".")
    if quota is not None:
        await update.message.reply_text(f'Saldo Anda adalah {sisa_saldo}')
    else:
        await update.message.reply_text('Saldo Anda adalah 0')

async def beli_quota(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    config = Database.get_instance().get_config() 
    if not config:
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti')
        return
        
    whatsapp_number, sec_conf = config[0]
    Database.get_instance().clean_order_user(username)
    await update.message.reply_text(f'Untuk pembelian silahkan kontak ke https://wa.me/{whatsapp_number}')
    

async def cek_harga(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
        
    await update.message.reply_text('Mohon tunggu sebentar...')
    config = Database.get_instance().get_config() 
    if not config:
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti...')
        return
    
    application_data = Database.get_instance().get_application() 
    if application_data:
        response = ""
        for app in application_data:
            response += f"""- "{app[0]}"\nHarga: {format(app[1], ",").replace(",", ".")}\n\n\n"""    
        
        await update.message.reply_text(response)


async def order_morinaga(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    
    quota = Database.get_instance().get_quota(username)
    onOrder = Database.get_instance().check_on_order(username)
    credentials = read_credentials()
    apikey = credentials.get('apikey')
    config = Database.get_instance().get_config() 
    if not config:
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti err : 404 morinaga')
        return
    
    whatsapp_number, sec_conf = config[0]
    #morinaga 538
    
    app_id = 538
    price = Database.get_instance().get_app_price(app_id)
    if quota is None or quota < 1:
        await update.message.reply_text('Saldo Anda 0.')
        return
    
    if quota < price:
        await update.message.reply_text('Saldo Anda tidak mencukupi untuk melakukan order.')
        return
    
    calculate = quota-price
    sisa_saldo = format(calculate, ",").replace(",", ".")
    
    
    if onOrder:
        await update.message.reply_text('Order anda sedang berlangsung, mohon selesaikan orderan terlebih dahulu atau lakukan /cancelorder untuk order nomer baru.')
        return
    
    await update.message.reply_text('Mohon tunggu sebentar...')
    Database.get_instance().clean_order_user(username)
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(f'https://siotp.com/api/order?apikey={apikey}&service={app_id}&operator=any&country=0') as response:
            try:
                text = await response.text()
                data = json.loads(text)
                if response.status == 200:
                    await upsert_data()
                    if data.get('status') == 'success':
                        order_id = data.get('id')
                        sms_number = data.get('number')
                        order_time = datetime.datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Prepare data for insertion
                        order_data = {
                            'id': order_id,
                            'application': 'MORINAGA',
                            'order_time': order_time,
                            'number': sms_number,
                            'message': '',
                            'status': 'Waiting Sms',
                            'order_status': 'Ongoing'
                        }                        
                        # Insert into database
                        Database.get_instance().add_order(order_data, username)
                        print(f'{username} melakukan order "MORINAGA", nomer {sms_number}')
                        await update.message.reply_text(f'Order Nomor "MORINAGA" berhasil, Nomer akan expired jika OTP tidak diterima selama 15 Menit dan Quota akan kembali sesuai dengan harga aplikasi. berikut nomor anda:\n\n <code>{sms_number}</code> \nSisa saldo anda : {sisa_saldo}', parse_mode=ParseMode.HTML) 
                    else:
                        error_message = data.get('message', 'Terjadi kesalahan yang tidak diketahui')
                        if 'saldo tidak mencukupi' in error_message:                            
                            await update.message.reply_text(f'Gagal Memesan Nomer, Saldo Kartu tidak cukup, mohon kontak admin dan jelaskan terkait masalah ini \n https://wa.me/{whatsapp_number}')
                        else:
                            await update.message.reply_text(f'Gagal Memesan Nomer, {error_message}, silahkan coba lagi nanti')
                else:
                    await update.message.reply_text(f'Gagal Memesan Nomer, silahkan coba beberapa saat lagi, jika masih belum bisa mohon kontak ke https://wa.me/{whatsapp_number}')
            except Exception as e:
                print(f'order "MORINAGA" ERROR {e}')
                await update.message.reply_text(f'Gagal Memesan Nomer, silahkan coba beberapa saat lagi, jika masih belum bisa mohon kontak ke https://wa.me/{whatsapp_number}')

async def order_prenagen(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    quota = Database.get_instance().get_quota(username)
    onOrder = Database.get_instance().check_on_order(username)
    credentials = read_credentials()
    apikey = credentials.get('apikey')
    config = Database.get_instance().get_config() 
    if not config:
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti err : 404 morinaga')
        return
        
    whatsapp_number, sec_conf = config[0]
    app_id = 534
    
    price = Database.get_instance().get_app_price(app_id)
    if quota is None or quota < 1:
        await update.message.reply_text('Saldo Anda 0.')
        return
    
    if quota < price:
        await update.message.reply_text('Saldo Anda tidak mencukupi untuk melakukan order.')
        return
    
    calculate = quota-price
    sisa_saldo = format(calculate, ",").replace(",", ".")
    
    if onOrder:
        await update.message.reply_text('Order anda sedang berlangsung, mohon selesaikan orderan terlebih dahulu atau lakukan /cancelorder untuk order nomer baru.')
        return
    
    await update.message.reply_text('Mohon tunggu sebentar...')
    Database.get_instance().clean_order_user(username)
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(f'https://siotp.com/api/order?apikey={apikey}&service={app_id}&operator=any&country=0') as response:
            try:
                text = await response.text()
                data = json.loads(text)
                if response.status == 200:
                    await upsert_data()
                    if data.get('status') == 'success':
                        order_id = data.get('id')
                        sms_number = data.get('number')
                        order_time = datetime.datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Prepare data for insertion
                        order_data = {
                            'id': order_id,
                            'application': 'PRENAGEN',
                            'order_time': order_time,
                            'number': sms_number,
                            'message': '',
                            'status': 'Waiting Sms',
                            'order_status': 'Ongoing'
                        }                        
                        # Insert into database
                        Database.get_instance().add_order(order_data, username)
                        print(f'{username} melakukan order "PRENAGEN", nomer {sms_number}')
                        await update.message.reply_text(f'Order Nomor "PRENAGEN" berhasil, Nomer akan expired jika OTP tidak diterima selama 15 Menit dan Quota akan kembali sesuai dengan harga aplikasi. berikut nomor anda:\n\n <code>{sms_number}</code> \nSisa saldo anda : {sisa_saldo}', parse_mode=ParseMode.HTML) 
                    else:
                        error_message = data.get('message', 'Terjadi kesalahan yang tidak diketahui')
                        if 'saldo tidak mencukupi' in error_message:                            
                            await update.message.reply_text(f'Gagal Memesan Nomer, Saldo Kartu tidak cukup, mohon kontak admin dan jelaskan terkait masalah ini \n https://wa.me/{whatsapp_number}')
                        else:
                            await update.message.reply_text(f'Gagal Memesan Nomer, {error_message}, silahkan coba lagi nanti')
                else:
                    await update.message.reply_text(f'Gagal Memesan Nomer, silahkan coba beberapa saat lagi, jika masih belum bisa mohon kontak ke https://wa.me/{whatsapp_number}')
            except Exception as e:
                print(f'order "PRENAGEN" ERROR {e}')
                await update.message.reply_text(f'Gagal Memesan Nomer, silahkan coba beberapa saat lagi, jika masih belum bisa mohon kontak ke https://wa.me/{whatsapp_number}')

async def order_sgm(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    quota = Database.get_instance().get_quota(username)
    onOrder = Database.get_instance().check_on_order(username)
    credentials = read_credentials()
    apikey = credentials.get('apikey')
    config = Database.get_instance().get_config() 
    if not config:
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti err : 404 morinaga')
        return
        
    whatsapp_number, sec_conf = config[0]    
    #SGM 119
    app_id = 119
    
    price = Database.get_instance().get_app_price(app_id)
    if quota is None or quota < 1:
        await update.message.reply_text('Saldo Anda 0.')
        return
    
    if quota < price:
        await update.message.reply_text('Saldo Anda tidak mencukupi untuk melakukan order.')
        return
    
    calculate = quota-price
    sisa_saldo = format(calculate, ",").replace(",", ".")
    
    if onOrder:
        await update.message.reply_text('Order anda sedang berlangsung, mohon selesaikan orderan terlebih dahulu atau lakukan /cancelorder untuk order nomer baru.')
        return
    
    await update.message.reply_text('Mohon tunggu sebentar...')
    Database.get_instance().clean_order_user(username)
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(f'https://siotp.com/api/order?apikey={apikey}&service={app_id}&operator=any&country=0') as response:
            try:
                text = await response.text()
                data = json.loads(text)
                if response.status == 200:
                    await upsert_data()
                    if data.get('status') == 'success':
                        order_id = data.get('id')
                        sms_number = data.get('number')
                        order_time = datetime.datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Prepare data for insertion
                        order_data = {
                            'id': order_id,
                            'application': 'SGM / Klubgenmaju / Bebeclub',
                            'order_time': order_time,
                            'number': sms_number,
                            'message': '',
                            'status': 'Waiting Sms',
                            'order_status': 'Ongoing'
                        }                        
                        # Insert into database
                        Database.get_instance().add_order(order_data, username)
                        print(f'{username} melakukan order "SGM / Klubgenmaju / Bebeclub", nomer {sms_number}')
                        await update.message.reply_text(f'Order Nomor "SGM / Klubgenmaju / Bebeclub" berhasil, Nomer akan expired jika OTP tidak diterima selama 15 Menit dan Quota akan kembali sesuai dengan harga aplikasi. berikut nomor anda:\n\n <code>{sms_number}</code> \nSisa saldo anda : {sisa_saldo}', parse_mode=ParseMode.HTML) 
                    else:
                        error_message = data.get('message', 'Terjadi kesalahan yang tidak diketahui')
                        if 'saldo tidak mencukupi' in error_message:                            
                            await update.message.reply_text(f'Gagal Memesan Nomer, Saldo Kartu tidak cukup, mohon kontak admin dan jelaskan terkait masalah ini \n https://wa.me/{whatsapp_number}')
                        else:
                            await update.message.reply_text(f'Gagal Memesan Nomer, {error_message}, silahkan coba lagi nanti')
                else:
                    await update.message.reply_text(f'Gagal Memesan Nomer, silahkan coba beberapa saat lagi, jika masih belum bisa mohon kontak ke https://wa.me/{whatsapp_number}')
            except Exception as e:
                print(f'order "SGM" ERROR {e}')
                await update.message.reply_text(f'Gagal Memesan Nomer, silahkan coba beberapa saat lagi, jika masih belum bisa mohon kontak ke https://wa.me/{whatsapp_number}')
                
async def order_nutriclub(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    quota = Database.get_instance().get_quota(username)
    onOrder = Database.get_instance().check_on_order(username)
    credentials = read_credentials()
    apikey = credentials.get('apikey')
    config = Database.get_instance().get_config() 
    if not config:
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti err : 404 morinaga')
        return
        
    whatsapp_number, sec_conf = config[0]
    #NUTRICLUB 714
    app_id = 714
    
    price = Database.get_instance().get_app_price(app_id)
    if quota is None or quota < 1:
        await update.message.reply_text('Saldo Anda 0.')
        return
    
    if quota < price:
        await update.message.reply_text('Saldo Anda tidak mencukupi untuk melakukan order.')
        return
    
    calculate = quota-price
    sisa_saldo = format(calculate, ",").replace(",", ".")
    
    if onOrder:
        await update.message.reply_text('Order anda sedang berlangsung, mohon selesaikan orderan terlebih dahulu atau lakukan /cancelorder untuk order nomer baru.')
        return
    
    await update.message.reply_text('Mohon tunggu sebentar...')
    Database.get_instance().clean_order_user(username)
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(f'https://siotp.com/api/order?apikey={apikey}&service={app_id}&operator=any&country=0') as response:
            try:
                text = await response.text()
                data = json.loads(text)
                if response.status == 200:
                    await upsert_data()
                    if data.get('status') == 'success':
                        order_id = data.get('id')
                        sms_number = data.get('number')
                        order_time = datetime.datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Prepare data for insertion
                        order_data = {
                            'id': order_id,
                            'application': 'Nutriclub',
                            'order_time': order_time,
                            'number': sms_number,
                            'message': '',
                            'status': 'Waiting Sms',
                            'order_status': 'Ongoing'
                        }                        
                        # Insert into database
                        Database.get_instance().add_order(order_data, username)
                        print(f'{username} melakukan order "Nutriclub", nomer {sms_number}')
                        await update.message.reply_text(f'Order Nomor "Nutriclub" berhasil, Nomer akan expired jika OTP tidak diterima selama 15 Menit dan Quota akan kembali sesuai dengan harga aplikasi. berikut nomor anda:\n\n <code>{sms_number}</code> \nSisa saldo anda : {sisa_saldo}', parse_mode=ParseMode.HTML) 
                    else:
                        error_message = data.get('message', 'Terjadi kesalahan yang tidak diketahui')
                        if 'saldo tidak mencukupi' in error_message:                            
                            await update.message.reply_text(f'Gagal Memesan Nomer, Saldo Kartu tidak cukup, mohon kontak admin dan jelaskan terkait masalah ini \n https://wa.me/{whatsapp_number}')
                        else:
                            await update.message.reply_text(f'Gagal Memesan Nomer, {error_message}, silahkan coba lagi nanti')
                else:
                    await update.message.reply_text(f'Gagal Memesan Nomer, silahkan coba beberapa saat lagi, jika masih belum bisa mohon kontak ke https://wa.me/{whatsapp_number}')
            except Exception as e:
                print(f'order "Nutriclub" ERROR {e}')
                await update.message.reply_text(f'Gagal Memesan Nomer, silahkan coba beberapa saat lagi, jika masih belum bisa mohon kontak ke https://wa.me/{whatsapp_number}')

async def order_entrasol(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    quota = Database.get_instance().get_quota(username)
    onOrder = Database.get_instance().check_on_order(username)
    credentials = read_credentials()
    apikey = credentials.get('apikey')
    config = Database.get_instance().get_config() 
    if not config:
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti err : 404 morinaga')
        return
        
    whatsapp_number, sec_conf = config[0]
    #Entrasol / Benecol 654
    app_id = 654
    
    price = Database.get_instance().get_app_price(app_id)
    if quota is None or quota < 1:
        await update.message.reply_text('Saldo Anda 0.')
        return
    
    if quota < price:
        await update.message.reply_text('Saldo Anda tidak mencukupi untuk melakukan order.')
        return
    
    calculate = quota-price
    sisa_saldo = format(calculate, ",").replace(",", ".")
    
    if onOrder:
        await update.message.reply_text('Order anda sedang berlangsung, mohon selesaikan orderan terlebih dahulu atau lakukan /cancelorder untuk order nomer baru.')
        return
    
    await update.message.reply_text('Mohon tunggu sebentar...')
    Database.get_instance().clean_order_user(username)
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(f'https://siotp.com/api/order?apikey={apikey}&service={app_id}&operator=any&country=0') as response:
            try:
                text = await response.text()
                data = json.loads(text)
                if response.status == 200:
                    await upsert_data()
                    if data.get('status') == 'success':
                        order_id = data.get('id')
                        sms_number = data.get('number')
                        order_time = datetime.datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Prepare data for insertion
                        order_data = {
                            'id': order_id,
                            'application': 'Entrasol / Benecol',
                            'order_time': order_time,
                            'number': sms_number,
                            'message': '',
                            'status': 'Waiting Sms',
                            'order_status': 'Ongoing'
                        }                        
                        # Insert into database
                        Database.get_instance().add_order(order_data, username)
                        print(f'{username} melakukan order "Entrasol / Benecol", nomer {sms_number}')
                        await update.message.reply_text(f'Order Nomor "Entrasol / Benecol" berhasil, Nomer akan expired jika OTP tidak diterima selama 15 Menit dan Quota akan kembali sesuai dengan harga aplikasi. berikut nomor anda:\n\n <code>{sms_number}</code> \nSisa saldo anda : {sisa_saldo}', parse_mode=ParseMode.HTML) 
                    else:
                        error_message = data.get('message', 'Terjadi kesalahan yang tidak diketahui')
                        if 'saldo tidak mencukupi' in error_message:                            
                            await update.message.reply_text(f'Gagal Memesan Nomer, Saldo Kartu tidak cukup, mohon kontak admin dan jelaskan terkait masalah ini \n https://wa.me/{whatsapp_number}')
                        else:
                            await update.message.reply_text(f'Gagal Memesan Nomer, {error_message}, silahkan coba lagi nanti')
                else:
                    await update.message.reply_text(f'Gagal Memesan Nomer, silahkan coba beberapa saat lagi, jika masih belum bisa mohon kontak ke https://wa.me/{whatsapp_number}')
            except Exception as e:
                print(f'order "Entrasol / Benecol" ERROR {e}')
                await update.message.reply_text(f'Gagal Memesan Nomer, silahkan coba beberapa saat lagi, jika masih belum bisa mohon kontak ke https://wa.me/{whatsapp_number}')


async def otpcode_command(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    await update.message.reply_text('Mohon tunggu sebentar...')
    await upsert_data()
    Database.get_instance().clean_order_user(username)
    dataOrders = Database.get_instance().get_orders(username) 
    if dataOrders:
        response = ""
        for orderx in dataOrders:
            statusOrder = orderx[4]
            response += f""" Berikut Order anda : \n- Username: {username}\n- Number: {orderx[0]}\n- Application: {orderx[1]}\n- Order Time: {orderx[2]}\n- Status: {statusOrder}\n- SMS: {orderx[3]}\n"""    
        await update.message.reply_text(response)
        if 'success' in statusOrder.lower():
            print(f'Nomer {orderx[0]} untuk Aplikasi {orderx[1]} berhasil, user penerima {username}. SMS :  {orderx[3]}')
            Database.get_instance().update_finish_order(username, orderx[0])
            #Database.get_instance().reduce_quota(username)
    else:
        await update.message.reply_text('Anda belum memiliki orderan')
    return

async def cancel_order_command(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    try:
        credentials = read_credentials()
        apikey = credentials.get('apikey')
        await update.message.reply_text('Mohon tunggu sebentar...')
        await upsert_data()     
        timeout = aiohttp.ClientTimeout(total=10)
        
        if Database.get_instance().check_ongoing_not_send(username):
            await update.message.reply_text('Anda memiliki orderan yang sedang berlangsung, dan sudah menerima OTP. silahkan akses /otpcode untuk menampilkan OTP')
            return
        
        if Database.get_instance().check_ongoing(username):
            if Database.get_instance().check_order_to_delete(username):
                order_ids = Database.get_instance().get_deleted_id(username)
                for order_id in order_ids:                    
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(f'https://siotp.com/api/changestatus?apikey={apikey}&id={order_id}&status=0') as response:
                            if response.status == 200:
                                print(f'Cancel Order {order_id} Success')
                            else:
                                print(f'Cancel Order {order_id} Failed')
                Database.get_instance().cancel_order_user(username)
                #Database.get_instance().clean_order_user(username)
                await update.message.reply_text('Semua Order dibatalkan')
            else:
                await update.message.reply_text('Anda tidak memiliki orderan yang aktif')
        else:
            await update.message.reply_text('Anda tidak memiliki orderan')
    except Exception as e:
        print(e)
        await update.message.reply_text('Terjadi kesalahan, silahkan coba kembali')
        
async def upsert_data():
    credentials = read_credentials()
    apikey = credentials.get('apikey')
    
    timeout = aiohttp.ClientTimeout(total=10)  # timeout total 10 detik
    async with aiohttp.ClientSession(timeout=timeout) as session:
        order_ids = Database.get_instance().get_sms_empty_id()
        for order_id in order_ids:                
            async with session.get(f'https://siotp.com/api/getotp?apikey={apikey}&id={order_id}') as response2:
                if response2.status == 200:
                    text = await response2.text()
                    data = json.loads(text)
                    json_status = data.get('status')
                    
                    if json_status and 'success' in json_status.lower():
                        json_data = data.get('data')
                        order_id = json_data.get('id')
                        message_col = json_data.get('inbox')
                        api_order_status = json_data.get('status')
                        message = ''
                        status = ''
                        readstatus = ''
                        order_status = ''
                        
                        if api_order_status == '0':
                            message = ''
                            status = 'Timeout'
                            readstatus = 'Read'
                            order_status = 'Canceled'
                            Database.get_instance().update_order_timeout(order_id, message, status, order_status, readstatus)
                        elif api_order_status == '3':
                            async with session.get(f'https://siotp.com/api/changestatus?apikey={apikey}&id={order_id}&status=1') as response3:
                                pass
                            message = message_col
                            status = 'Success'
                            readstatus = 'Unread'       
                            Database.get_instance().update_order(order_id, message, status, readstatus)
                        else:
                            message = ''
                            status = 'Waiting Sms'
                            readstatus = 'New'       
                            Database.get_instance().update_order(order_id, message, status, readstatus)                           
                        
                else:
                    print(f'Gagal mendapatkan data untuk order ID {order_id}, HTTP status: {response2.status}')

#///////////////////////////////////////ADMIN ROUTE/////////////////////////////////////////////////////#
#---------------------------------------KeepAliveCookies----------------------------------------------#
async def keep_alive_cookies():
    while True:
        credentials = read_credentials()
        apikey = credentials.get('apikey')
        #print("-------Keepalive------")
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get('https://cdn-workflows-api.jetadmin.app/hooks/lVtGjBXs0SAuTYppC2z7kc9P0O1fNhDZ') as response2:
                if response2.status == 200:
                    #self.log.debug("Webhook Active")
                    pass
                else:
                    #self.log.debug("Session Expired")
                    pass
        await asyncio.sleep(8)  # Sleep for 1 minutes

async def keep_alive_db():
    while True:
        Database.get_instance().keep_alive()
        await asyncio.sleep(1)

#--------------------------------------CekSaldoKartu----------------------------------------------------#
async def cek_quota_kartu(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    try:
        # Pastikan tidak ada percakapan lain yang berlangsung
        if context.user_data.get('active_conversation'):
            await update.message.reply_text("Mengakhiri percakapan sebelumnya.")
            context.user_data['active_conversation'] = False
            return ConversationHandler.END
        
        context.user_data['active_conversation'] = True
        # Ask for secret key
        await update.message.reply_text("Masukkan secret key: (/cancel untuk membatalkan)")
        # Set conversation state to SECRET_KEY
        return SECRET_KEY
    except Exception as e:
        await update.message.reply_text('Terjadi kesalahan dalam pemrosesan perintah.')

async def get_secret_key_cek_quota_kartu(update: Update, context: CallbackContext) -> int:
    # Retrieve secret key from user input
    secret_key = update.message.text
    config = Database.get_instance().get_config() 
    if not config:
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi')
        return ConversationHandler.END
    
    whatsapp_number, sec_conf = config[0]
        
    if secret_key == sec_conf:
        await update.message.reply_text("Mohon tunggu....")
        return await process_saldo_information(update, context)
    else:
        await update.message.reply_text('Secret key tidak valid.')
        return ConversationHandler.END

async def process_saldo_information(update: Update, context: CallbackContext) -> int:
    try:
        credentials = read_credentials()
        apikey = credentials.get('apikey')
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f'https://siotp.com/api/getbalance?apikey={apikey}') as response:
                if response.status == 200:
                    text = await response.text()
                    data = json.loads(text)
                    if data.get('status') == 'success':
                        saldo = data.get('balance')
                        kartu = round(int(saldo.replace('.',''))/500)
                        await update.message.reply_text(f'Saldo akun anda Rp.{saldo}/{kartu} Pcs')
                    else:                        
                        await update.message.reply_text('Saldo akun tidak ditemukan')
                else:
                    await update.message.reply_text('Gagal mengambil informasi saldo') 
    except Exception as e:
        print(e)
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti')
    return ConversationHandler.END

#------------------------------------------------AddQuota-------------------------------------------------------------------------#
async def add_quota_command(update: Update, context: CallbackContext) -> int:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    try:
        # Pastikan tidak ada percakapan lain yang berlangsung
        if context.user_data.get('active_conversation'):
            await update.message.reply_text("Mengakhiri percakapan sebelumnya.")
            context.user_data['active_conversation'] = False
            return ConversationHandler.END
        context.user_data['active_conversation'] = True
        # Ask for secret key
        await update.message.reply_text("Masukkan secret key: (/cancel untuk membatalkan)")
        # Set conversation state to SECRET_KEY
        return SECRET_KEY
    except Exception as e:
        await update.message.reply_text('Terjadi kesalahan dalam pemrosesan perintah.')

async def get_secret_key(update: Update, context: CallbackContext) -> int:
    # Retrieve secret key from user input
    secret_key = update.message.text
    # Validate secret key
    config = Database.get_instance().get_config()
    if not config:
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti (/cancel untuk membatalkan)')
        return ConversationHandler.END
        
    whatsapp_number, sec_conf = config[0]
    if secret_key != sec_conf:
        await update.message.reply_text('Secret key tidak valid. Pembuatan quota dibatalkan.')
        return ConversationHandler.END
    
    # Save the secret key in context for later use
    context.user_data['secret_key'] = secret_key
    # Ask for username
    await update.message.reply_text("Masukkan username [isi 'myself' untuk username sendiri]: (/cancel untuk membatalkan)")
    # Set conversation state to USERNAME
    return USERNAME

async def get_username(update: Update, context: CallbackContext) -> int:
    # Retrieve username from user input
    username = update.message.text
    if username == 'myself':
        username = update.message.from_user.username
    # Save the username in context for later use
    context.user_data['username'] = username
    # Ask for quantity
    await update.message.reply_text("Masukkan jumlah quota: (/cancel untuk membatalkan)")
    # Set conversation state to QUANTITY
    return QUANTITY

async def get_quantity(update: Update, context: CallbackContext) -> int:
    # Retrieve quantity from user input
    quantity_text = update.message.text
    # Check if quantity is an integer
    if not quantity_text.isdigit():
        await update.message.reply_text("Jumlah quota harus berupa angka. Silakan masukkan kembali. (/cancel untuk membatalkan)")
        return QUANTITY
    # Convert quantity to integer
    quantity = int(quantity_text)
    # Save the quantity in context for later use
    context.user_data['quantity'] = quantity
    # Perform the action with the provided information
    await process_quota_information(update, context)
    # End the conversation
    return ConversationHandler.END

async def process_quota_information(update: Update, context: CallbackContext) -> None:
    try:
        # Retrieve username, quantity, and secret key from context
        username = context.user_data['username']
        quantity = context.user_data['quantity']
        secret_key = context.user_data['secret_key']
        
        Database.get_instance().add_quota(username, quantity)
        await update.message.reply_text(f'Quota berhasil ditambahkan untuk {username}.')
        return ConversationHandler.END
        
    except Exception as e:
        await update.message.reply_text('Terjadi kesalahan menambah quota, silahkan coba lagi nanti')

#------------------------------------------------------DeleteQuota--------------------------------------------------------------------------#
async def delete_quota_command(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    try:
        # Pastikan tidak ada percakapan lain yang berlangsung
        if context.user_data.get('active_conversation'):
            await update.message.reply_text("Mengakhiri percakapan sebelumnya.")
            context.user_data['active_conversation'] = False
            return ConversationHandler.END
        
        context.user_data['active_conversation'] = True
        await update.message.reply_text("Masukkan secret key: (/cancel untuk membatalkan)")
        return SECRET_KEY
    except Exception as e:
        await update.message.reply_text('Terjadi kesalahan dalam pemrosesan perintah.')

async def get_secret_key_delete(update: Update, context: CallbackContext) -> int:
    # Retrieve secret key from user input
    secret_key = update.message.text
    # Validate secret key here
    config = Database.get_instance().get_config() 
    if not config:
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti')
        return ConversationHandler.END
        
    whatsapp_number, sec_conf = config[0]
    if secret_key != sec_conf:
        await update.message.reply_text('Secret key tidak valid.')
        return ConversationHandler.END
        
    # Save the secret key in context for later use
    context.user_data['secret_key'] = secret_key
    # Ask for username
    await update.message.reply_text("Masukkan username [isi 'myself' untuk username sendiri]: (/cancel untuk membatalkan)")
    # Set conversation state to USERNAME
    return USERNAME

async def get_username_delete(update: Update, context: CallbackContext) -> int:
    # Retrieve username from user input
    username = update.message.text
    if username == 'myself':
        username = update.message.from_user.username
    # Save the username in context for later use
    context.user_data['username'] = username
    # Perform the action with the provided information
    await process_delete_quota_information(update, context)
    # End the conversation
    return ConversationHandler.END

async def process_delete_quota_information(update: Update, context: CallbackContext) -> None:
    try:
        # Retrieve username and secret key from context
        username = context.user_data['username']
        secret_key = context.user_data['secret_key']
        
        # Delete quota for the user
        config = Database.get_instance().get_config() 
        if not config:
            await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti')
            return ConversationHandler.END
        
        whatsapp_number, sec_conf = config[0]
        
        if secret_key == sec_conf:
            Database.get_instance().delete_quota(username)
            await update.message.reply_text(f'Quota berhasil dihapus untuk {username}.')
            return ConversationHandler.END
        else:
            await update.message.reply_text('Secret key tidak valid.')
            return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti')
        return ConversationHandler.END
    
#------------------------------------------------TopupKartu-------------------------------------------------------------------------#
async def topup_kartu_command(update: Update, context: CallbackContext) -> int:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    try:
        await update.message.reply_text('This feature currently not available.....')
        return
        # Pastikan tidak ada percakapan lain yang berlangsung
        if context.user_data.get('active_conversation'):
            await update.message.reply_text("Mengakhiri percakapan sebelumnya.")
            context.user_data['active_conversation'] = False
            return ConversationHandler.END
        context.user_data['active_conversation'] = True
        # Ask for secret key
        await update.message.reply_text("Masukkan secret key: (/cancel untuk membatalkan)")
        # Set conversation state to SECRET_KEY
        return SECRET_KEY
    except Exception as e:
        await update.message.reply_text('Terjadi kesalahan dalam pemrosesan perintah.')

async def get_secret_key_topup(update: Update, context: CallbackContext) -> int:
    # Retrieve secret key from user input
    secret_key = update.message.text
    # Validate secret key
    config = Database.get_instance().get_config()
    if not config:
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti (/cancel untuk membatalkan)')
        return ConversationHandler.END
        
    whatsapp_number, sec_conf = config[0]
    if secret_key != sec_conf:
        await update.message.reply_text('Secret key tidak valid. Pembuatan quota dibatalkan.')
        return ConversationHandler.END
    
    # Save the secret key in context for later use
    context.user_data['secret_key'] = secret_key
    # Ask for username
    await update.message.reply_text("Masukkan nominal topup, minimal 5000: (/cancel untuk membatalkan)")
    # Set conversation state to USERNAME
    return QUANTITY

async def get_quantity_topup(update: Update, context: CallbackContext) -> int:
    # Retrieve quantity from user input
    quantity_text = update.message.text
    # Check if quantity is an integer
    if not quantity_text.isdigit():
        await update.message.reply_text("Jumlah quota harus berupa angka tanpa tanda baca. Silakan masukkan kembali. (/cancel untuk membatalkan)")
        return QUANTITY
    # Convert quantity to integer
    quantity = int(quantity_text)

    if quantity < 5000:
        await update.message.reply_text("Minimal topup 5000. Silakan masukkan kembali. (/cancel untuk membatalkan)")
        return QUANTITY
    # Save the quantity in context for later use
    context.user_data['quantity'] = quantity
    # Perform the action with the provided information
    await update.message.reply_text("Mohon tunggu sebentar...")
    await process_topup_kartu_information(update, context)
    # End the conversation
    return ConversationHandler.END

async def process_topup_kartu_information(update: Update, context: CallbackContext) -> None:
    try:
        # Retrieve username, quantity, and secret key from context
        quantity = context.user_data['quantity']
        credentials = read_credentials()
        cookie = credentials.get('cookie')
        token = credentials.get('_token')

        async with aiohttp.ClientSession() as session:
            async with session.post('https://qpanel.org/panel/deposit/new', headers={
                'Cookie': cookie,
                'Dnt': '1',
                'X-Requested-With': 'XMLHttpRequest',
                'X-Csrf-Token': token,
                'Content-Type': 'application/x-www-form-urlencoded'
            }, data={
                'deposit_method_id': '1',
                'amount': quantity,
                '_token': token
            }) as response:
                if response.status == 200:
                    await update.message.reply_text('Respond server berhasil, sedang membuat QR Code...')
                    response_json = await response.json()
                    if response_json['status']:
                        hti = Html2Image(size=(230, 450))
                        html_content = response_json['message']
                        hti.screenshot(html_content, save_as='qrcode.png')
                        await update.message.reply_photo(photo=open('qrcode.png', 'rb'))
                        os.remove('qrcode.png')
                    else:
                        await update.message.reply_text("Gagal membuat QR Code, QR tidak ditemukan")
                    return ConversationHandler.END
                else:
                    await update.message.reply_text(f'Gagal melakukan topup, respond server gagal, silahkan coba lagi nanti')
                    return ConversationHandler.END

    except Exception as e:
        print(e)
        await update.message.reply_text('Terjadi kesalahan sistem, silahkan coba lagi nanti')

#------------------------------------------------GetEmailPass-------------------------------------------------------------------------#
async def get_user_data_command(update: Update, context: CallbackContext) -> int:
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text('Anda belum membuat username, mohon buat username akun Telegram anda terlebih dahulu')
        return
    try:
        # Pastikan tidak ada percakapan lain yang berlangsung
        if context.user_data.get('active_conversation'):
            await update.message.reply_text("Mengakhiri percakapan sebelumnya.")
            context.user_data['active_conversation'] = False
            return ConversationHandler.END
        context.user_data['active_conversation'] = True
        # Ask for secret key
        await update.message.reply_text("Masukkan secret key: (/cancel untuk membatalkan)")
        # Set conversation state to SECRET_KEY
        return SECRET_KEY
    except Exception as e:
        await update.message.reply_text('Terjadi kesalahan dalam pemrosesan perintah.')

async def get_secret_key_user_data(update: Update, context: CallbackContext) -> int:
    # Retrieve secret key from user input
    secret_key = update.message.text
    # Validate secret key
    config = Database.get_instance().get_config()
    if not config:
        await update.message.reply_text('Terjadi kesalahan, silahkan coba lagi nanti (/cancel untuk membatalkan)')
        return ConversationHandler.END
        
    whatsapp_number, sec_conf = config[0]
    if secret_key != sec_conf:
        await update.message.reply_text('Secret key tidak valid. GetUser dibatalkan.')
        return ConversationHandler.END
    
    # Save the secret key in context for later use
    context.user_data['secret_key'] = secret_key
    # Ask for username
    await update.message.reply_text("Masukkan username [isi 'myself' untuk username sendiri]: (/cancel untuk membatalkan)")
    # Set conversation state to USERNAME
    return USERNAME

async def get_username_user_data(update: Update, context: CallbackContext) -> int:
    # Retrieve username from user input
    username = update.message.text
    if username == 'myself':
        username = update.message.from_user.username
    # Save the username in context for later use
    context.user_data['username'] = username
    await update.message.reply_text('Mohon tunggu sebentar..')
    await process_get_user_data(update, context)
    return ConversationHandler.END

async def process_get_user_data(update: Update, context: CallbackContext) -> None:
    try:
        response = ""  # Define response variable
        # Retrieve username, quantity, and secret key from context
        username = context.user_data['username']
        secret_key = context.user_data['secret_key']        
        user_data = Database.get_instance().get_user_data(username) 
        if user_data:
            for data in user_data:
                response += f"""Data anda adalah :\n- Username: {username}\n- Email: {data[0]}\n- Password: {data[1]}\n"""    
            await update.message.reply_text(response)
        else:
            await update.message.reply_text('Gagal mengambil UserData, coba lagi beberapa saat')
        
        return ConversationHandler.END
    
    except Exception as e:
        await update.message.reply_text('Terjadi kesalahan mengambil UserData, silahkan coba lagi nanti')
 
 
#-------------------------------------------------CancelConversation-----------------------------------------------#
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Percakapan dibatalkan.')
    return ConversationHandler.END
    
#-------------------------------------------------ConversationHandler-----------------------------------------------#

fallbacks = [
    CommandHandler('cancel', cancel),
    CommandHandler('addquota', add_quota_command),
    CommandHandler('deletequota', delete_quota_command),
    CommandHandler('ceksisakartu', cek_quota_kartu),
    CommandHandler('topupsaldokartu', topup_kartu_command)
]

conversation_handler_add_quota = ConversationHandler(
    entry_points=[CommandHandler('addquota', add_quota_command)],
    states={
        SECRET_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_secret_key)],
        USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
        QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity)]
    },
    fallbacks=fallbacks
)
delete_quota_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('deletequota', delete_quota_command)],
    states={
        SECRET_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_secret_key_delete)],
        USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username_delete)]
    },
    fallbacks=fallbacks
)

conversation_handler_cek_quota_kartu = ConversationHandler(
    entry_points=[CommandHandler('ceksisakartu', cek_quota_kartu)],
    states={
        SECRET_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_secret_key_cek_quota_kartu)]
    },
    fallbacks=fallbacks
)

conversation_handler_topup_kartu = ConversationHandler(
    entry_points=[CommandHandler('topupsaldokartu', topup_kartu_command)],
    states={
        SECRET_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_secret_key_topup)],
        QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity_topup)]
    },
    fallbacks=fallbacks
)

conversation_handler_get_user_data = ConversationHandler(
    entry_points=[CommandHandler('getuser', get_user_data_command)],
    states={
        SECRET_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_secret_key_user_data)],
        USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username_user_data)]
    },
    fallbacks=fallbacks
)
   
async def main():
    db = Database.get_instance()
    application = Application.builder().token('7342916393:AAGxXC8mNSkUbOCTnzE_gqG_AwiAMO-mbpo').build()
    
    #-------------------------CommandHandler--------------------------------#
    application.add_handler(CommandHandler('myusername', myusername_command))
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('notes', notes_command))
    application.add_handler(CommandHandler('notes_admin', notes_admin))
    application.add_handler(CommandHandler('cekquota', cek_quota))
    application.add_handler(CommandHandler('beliquota', beli_quota))
    application.add_handler(CommandHandler('morinaga', order_morinaga))
    application.add_handler(CommandHandler('prenagen', order_prenagen))
    application.add_handler(CommandHandler('sgm', order_sgm))
    application.add_handler(CommandHandler('nutriclub', order_nutriclub))
    application.add_handler(CommandHandler('entrasol', order_entrasol))
    application.add_handler(CommandHandler('pricelist', cek_harga))
    application.add_handler(CommandHandler('otpcode', otpcode_command))
    application.add_handler(CommandHandler('cancelorder', cancel_order_command))
    #-------------------------AddQuota------------------------------------------#
    application.add_handler(conversation_handler_add_quota)
    #-------------------------DeleteQuota----------------------------------------#
    application.add_handler(delete_quota_conversation_handler)
    #-------------------------CekSaldoKartu---------------------------------------#
    application.add_handler(conversation_handler_cek_quota_kartu)    
    #-------------------------TopupKartu---------------------------------------#
    application.add_handler(conversation_handler_topup_kartu)
    #-------------------------GetUser---------------------------------------#
    application.add_handler(conversation_handler_get_user_data)
    #-------------------------KeepAliveCookies---------------------------------------#
    #asyncio.create_task(keep_alive_cookies())
    #-------------------------KeepAliveDB---------------------------------------#
    asyncio.create_task(keep_alive_db())

    await application.run_polling()

if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())
