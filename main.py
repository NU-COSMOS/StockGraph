import requests
import tkinter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import configparser


class Application(tkinter.Frame):
    def __init__(self, root: tkinter.Tk = None, config=None, w=None, h=None):
        super().__init__(root, width=w, height=h)
        self.root = root
        self.config = config
        self.screen_width = w
        self.screen_height = h

        self.displayed_list = []  # 表示中の株名一覧を格納する
        self.pack()
        self.pack_propagate(0)
        self.create_widgets()

        # Tkinterのwindowが閉じられるときの処理
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self, w_rate: float = 0.7):
        self.create_graph()
        self.create_control_pannel()

    def create_control_pannel(self):
        self.control_pannel = tkinter.Frame(self)

        # 表示する株のシンボルを入力するテキストボックス
        self.create_text_box()

        # 入力されたシンボルに対応する表示を行うボタン
        self.create_show_btn()

        # 表示しているものをすべて削除するボタン
        self.create_clear_btn()

        # 描画中のシンボル一覧を表示するリスト
        self.create_stock_list()

        self.control_pannel.pack(fill=tkinter.BOTH, expand=True)

    def create_text_box(self):
        self.text_box = tkinter.Entry(self.control_pannel)
        self.text_box["width"] = 10
        self.text_box.pack()

    def create_show_btn(self):
        self.show_btn = tkinter.Button(self.control_pannel)
        self.show_btn["text"] = "show"
        self.show_btn["command"] = self.click_show_btn
        self.show_btn.pack()

    def create_clear_btn(self):
        self.clear_btn = tkinter.Button(self.control_pannel)
        self.clear_btn["text"] = "clear"
        self.clear_btn["command"] = self.clear
        self.clear_btn["state"] = "disabled"
        self.clear_btn.pack()

    def clear(self):
        self.clear_graph()
        self.clear_list()

    def clear_list(self):
        self.displayed_list = []
        self.stock_list.delete(0, tkinter.END)

    def create_stock_list(self):
        self.stock_list = tkinter.Listbox(self.control_pannel)
        self.scrollbar = tkinter.Scrollbar(
            self.stock_list, orient=tkinter.VERTICAL, command=self.stock_list.yview
        )
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.stock_list.pack(expand=True, fill=tkinter.BOTH)
        self.stock_list.config(yscrollcommand=self.scrollbar.set)

    def create_graph(self, w_rate: float = 0.7):
        self.graph_area = tkinter.Frame(self)

        plt.rcParams["font.size"] = 7
        self.fig, self.ax = plt.subplots()
        # 画面サイズに合わせて図のサイズを設定
        canvas_width = int(self.screen_width * w_rate)
        canvas_height = self.screen_height
        self.fig.set_size_inches(
            canvas_width / self.fig.dpi, canvas_height / self.fig.dpi
        )
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_area)
        self.canvas.get_tk_widget().pack(fill=tkinter.BOTH, expand=True)

        self.graph_area.pack(side="left")

    def clear_graph(self):
        self.ax.clear()
        self.ax.grid()
        self.canvas.draw()
        self.clear_btn["state"] = "disabled"

    def on_close(self):
        plt.close()
        self.root.destroy()

    def add_displayed_list(self, symbol: str):
        self.displayed_list.append(symbol)

    def click_show_btn(self):
        if (symbol := self.text_box.get()) not in self.displayed_list:
            # リクエスト制限のため、開発中はコメントアウト
            # self.display_graph()
            self.add_displayed_list(symbol)
            self.show_stock_list(symbol)

            # showボタン押下に成功した場合、clearボタンが押せるようにならなければならない
            self.clear_btn["state"] = "normal"

    def show_stock_list(self, symbol: str):
        self.stock_list.insert(tkinter.END, f"{symbol}")

    def display_graph(self):
        symbol = self.text_box.get()
        api_key = self.config["ALPHA_VANTAGE_KEY"]
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
        response = requests.get(url)
        data = response.json()

        daily_data: dict = dict(reversed(data["Time Series (Daily)"].items()))
        date_list = daily_data.keys()
        close_list = [float(x["4. close"]) for x in daily_data.values()]

        self.ax.plot(date_list, close_list)
        self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=15))
        self.ax.grid()
        self.canvas.draw()

        self.clear_btn["state"] = "normal"


def main():
    config = configparser.ConfigParser()
    config.read("./config.ini")

    root = tkinter.Tk()
    root.title("StockGraph")
    root.state("normal")
    app = Application(
        root=root,
        config=config["DEFAULT"],
        w=root.winfo_screenwidth(),
        h=root.winfo_screenheight(),
    )
    app.mainloop()


if __name__ == "__main__":
    main()
