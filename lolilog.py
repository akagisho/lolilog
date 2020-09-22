import sys
import re
import time
import datetime
import threading

import tkinter as tk
import tkinter.ttk
import tkinter.messagebox

import lolipo

class Lolilog:
    VER = 'Ver 1.0.3'

    def __init__(self):
        self.lolipo = lolipo.Lolipo()

        self.root = tk.Tk()
        self.root.title('lolilog ' + self.VER)

    def button01_clicked(self):
        account = self.entry02.get()
        domain = self.combo03.get()
        passwd = self.entry04.get()
        mydomain = self.entry05.get()

        if not mydomain:
            mydomain = account + '.' + domain

        if not re.search(r'^[a-z0-9\-]{3,16}$', account):
            tk.messagebox.showerror('エラー', 'アカウントを正しく入力してください。')
            return

        if not domain:
            tk.messagebox.showerror('エラー', 'ドメインを選択してください。')
            return

        if not re.search(r'^[a-z0-9\-\.]+$', mydomain):
            tk.messagebox.showerror('エラー', '対象ドメインを正しく入力してください。')
            return

        try:
            self.lolipo.login(account, domain, passwd)
        except:
            tk.messagebox.showerror('エラー', 'ログインできません。')
            return

        self.progress01['value'] = 0

        self.button01['state'] = tk.DISABLED
        self.button01.update()

        thread = threading.Thread(target=self.get_access_log, args=(['logs', mydomain]))
        thread.start()

    def get_access_log(self, save_dir, domain):
        self.lolipo.set_domain(domain)

        today = datetime.datetime.today()
        for i in range(-90, 0):
            date = today + datetime.timedelta(days=i)
            slt_date = datetime.datetime.strftime(date, '%y%m%d')

            print('[20' + slt_date + ']')
            file_path = self.lolipo.get_access_log_date(slt_date, save_dir)
            if file_path:
                print('Saved: ' + file_path)
            else:
                print('not exists')

            self.progress01['value'] += 1
            self.progress01.update()

            time.sleep(0.5)

        self.button01['state'] = tk.NORMAL
        self.button01.update()

        tk.messagebox.showinfo('終了', 'ダウンロードが完了しました。')

    def set_lolipo_domains(self, combo):
        try:
            domains = self.lolipo.get_lolipo_domains()
        except:
            tk.messagebox.showerror('エラー', 'インターネットに接続されていません。')
            combo['values'] = '再起動してください。'
            combo.current(0)
            return

        combo['values'] = tuple(domains.values())

    def main(self):
        self.frame01 = tk.Frame(self.root, padx=20, pady=10)
        self.frame01.pack()

        row = 0
        self.label01 = tk.Label(self.frame01, text='lolilog: ロリポップアクセスログ一括ダウンローダー', font=('', 18))
        self.label01.grid(column=0, row=row, columnspan=2, pady=10)

        row = row + 1
        self.label02 = tk.Label(self.frame01, text='アカウント:', font=('', 16))
        self.label02.grid(column=0, row=row, pady=10, sticky='w')
        self.entry02 = tk.Entry(self.frame01, width=30)
        self.entry02.grid(column=1, row=row, sticky='w')

        row = row + 1
        self.label03 = tk.Label(self.frame01, text='ドメイン:', font=('', 16))
        self.label03.grid(column=0, row=row, pady=10, sticky='w')
        self.combo03 = tk.ttk.Combobox(self.frame01, state='readonly')
        self.combo03.grid(column=1, row=row, sticky='w')

        row = row + 1
        self.label04 = tk.Label(self.frame01, text='パスワード:', font=('', 16))
        self.label04.grid(column=0, row=row, pady=10, sticky='w')
        self.entry04 = tk.Entry(self.frame01, width=30, show='*')
        self.entry04.grid(column=1, row=row, sticky='w')

        row = row + 1
        self.label05 = tk.Label(self.frame01, text='対象ドメイン:', font=('', 16))
        self.label05.grid(column=0, row=row, pady=10, sticky='w')
        self.entry05 = tk.Entry(self.frame01, width=30)
        self.entry05.grid(column=1, row=row, sticky='w')

        row = row + 1
        self.progress01 = tk.ttk.Progressbar(self.frame01, orient=tk.HORIZONTAL, length=300, maximum=90, mode='determinate')
        self.progress01.grid(column=0, row=row, columnspan=2, pady=10)

        row = row + 1
        self.button01 = tk.Button(self.frame01, text='ログファイルを一括ダウンロード', command=self.button01_clicked)
        self.button01.grid(column=0, row=row, columnspan=2, pady=10)

        thread = threading.Thread(target=self.set_lolipo_domains, args=([self.combo03]))
        thread.start()

        self.root.mainloop()

if __name__ == '__main__':
    lolilog = Lolilog()
    lolilog.main()