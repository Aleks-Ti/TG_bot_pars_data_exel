import requests
from lxml import html


async def price(data: list[tuple]):
    result = ''
    for url, xpath in data:
        response = requests.get(url)
        if response.status_code == 200:
            tree = html.fromstring(response.content)
            # CONTROL = print(
            # html.tostring(tree, pretty_print=True).decode('utf-8')
            # )
            price_data = tree.xpath(xpath)

            if price_data:
                result += str(price_data[0]) + '\n'
            else:
                result += (
                    'Ничего не найдено по '
                    + url
                    + ' - путь xpath: '
                    + xpath
                    + '\n'
                )
        else:
            result += 'Не удалось загрузить страницу.' + url + '\n'

    return result
