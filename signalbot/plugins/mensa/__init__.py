from signalbot.plugins import PluginChat, PluginRouter, chat_entry_point
from threading import Thread, Event
from datetime import datetime, timedelta
import requests
from lxml import html


class MensaChat(PluginChat):

    @chat_entry_point
    def triagemessage(self, message):
        pass

    @chat_entry_point
    def send_info(self, menus):
        reply = "Mensa today:\n\n"
        for menu in menus:
            reply += "{name} {price}\n{desc}\n\n".format(name=menu['name'],
                                                         price=menu['price'],
                                                         desc=menu['desc'])
        self.reply(reply)


class MensaRouter(PluginRouter):

    hour = 13
    minute = 0
    second = 0

    url = "https://www.studentenwerkfrankfurt.de/essen-trinken/speiseplaene/"\
          "cafeteria-darwins/"

    def start(self):
        super().start()
        self._stop_event = Event()
        self._thread = Thread(daemon=True, target=self._schedule_fetch)
        self._thread.start()

    def stop(self):
        super().stop()
        self._stop_event.set()
        self._thread.join()

    def _schedule_fetch(self):
        while not self._stop_event.is_set():
            now = datetime.now()
            date = now.replace(hour=self.hour,
                               minute=self.minute,
                               second=self.second)

            # Check if already passed today's time
            if now >= date:
                date += timedelta(days=1)

            # Don't run on weekends
            if date.isoweekday() in [6, 7]:
                date += timedelta(days=8-date.isoweekday())

            seconds = (date - now).total_seconds()

            stopped = self._stop_event.wait(seconds)
            if not stopped:
                self._fetch()

    def _fetch(self):
        menus = []

        tree = html.fromstring(requests.get(self.url).content)
        panel_today = tree.xpath(
            '//div[@id="c486"]'
            '/div[@class="panel panel-default"]')[0]

        for tr in panel_today.findall('.//tr'):
            tds = tr.findall('.//td')
            name = tds[0].findall('.//strong[@class="menu_name"]')[0].text
            desc = tds[0].findall('.//p')[0].text
            price = tds[1].findall('.//strong')[0].text

            desc = desc.strip(' \n\r\t')
            menus.append({
                'name': name,
                'price': price,
                'desc': desc})

        for chat in self._chats.values():
            chat.send_info(menus)


__plugin_router__ = MensaRouter
__plugin_chat__ = MensaChat
