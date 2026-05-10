from bs4 import BeautifulSoup
from openpyxl import Workbook


def parse():
    path = r"D:\ОПД\питон работы\работа 1.2"

    with open(path + r"\on.html", "r", encoding="cp1251") as file:
        html = file.read()

    soup = BeautifulSoup(html, "html.parser")

    # 👉 берём блоки товаров
    items = soup.find_all("div", class_="indexGoods__item")

    wb = Workbook()
    ws = wb.active
    ws.title = "Оперативная память"
    ws.append(["Название", "Цена", "Ссылка"])

    count = 0

    for item in items:
        name_tag = item.find("a", class_="indexGoods__item__name")
        price_tag = item.find("span", class_="price")

        if name_tag and price_tag:
            name = name_tag.get_text(strip=True)
            price = price_tag.get_text(strip=True)
            link = name_tag.get("href")

            if link.startswith("/"):
                link = "https://www.onlinetrade.ru" + link

            ws.append([name, price, link])
            count += 1

    wb.save(path + r"\оперативная_память.xlsx")

    print("Найдено товаров:", count)
    print("Файл сохранен: оперативная_память.xlsx")


if __name__ == "__main__":
    parse()
