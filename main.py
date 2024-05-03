import requests
import tkinter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import configparser


class Application(tkinter.Frame):
    def __init__(self, root=None, config=None, w=None, h=None):
        super().__init__(root, width=w, height=h)
        self.root = root
        self.config = config
        self.pack()
        self.pack_propagate(0)
        self.create_widgets()

        # Tkinterのwindowが閉じられるときの処理
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        self.text_box = tkinter.Entry(self)
        self.text_box["width"] = 10
        self.text_box.pack()

        submit_btn = tkinter.Button(self)
        submit_btn["text"] = "実行"
        submit_btn["command"] = self.display_graph
        submit_btn.pack()

        plt.rcParams["font.size"] = 7
        self.fig, self.ax = plt.subplots(figsize=(12, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack()

    def on_close(self):
        plt.close()
        self.root.destroy()

    def display_graph(self):
        symbol = self.text_box.get()
        api_key = self.config["ALPHA_VANTAGE_KEY"]
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
        response = requests.get(url)
        data = response.json()

        daily_data: dict = dict(reversed(data["Time Series (Daily)"].items()))
        date_list = daily_data.keys()
        close_list = [float(x["4. close"]) for x in daily_data.values()]

        self.ax.clear()
        self.ax.plot(date_list, close_list)
        self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=15))
        self.ax.grid()
        self.canvas.draw()


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
