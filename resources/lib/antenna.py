# -*- coding: utf-8 -*-

'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from time import sleep
import json, re
from youtube_resolver import resolve as yt_resolver
from tulip import bookmarks, directory, client, cache, workers, control, youtube
from tulip.compat import range, iteritems


class Indexer:

    def __init__(self):

        self.list = [] ; self.data = []
        self.base_link = 'https://www.antenna.gr'
        self.shows_link = ''.join([self.base_link, '/shows/ALL'])
        self.archive_link = ''.join([self.base_link, '/directory/ALL'])
        self.news_link = ''.join([self.base_link, '/ant1news/videos'])
        self.weather_link = ''.join([self.base_link, '/webtv/3091/kairos?showall'])
        self.sports_link = ''.join([self.base_link, '/webtv/3062/athlitika?showall'])
        self.latest_link = ''.join([self.base_link, '/webtv/'])
        self.more_videos = ''.join([self.base_link, '/templates/data/morevideos?aid='])
        self.more_web_videos = ''.join([self.base_link, '/templates/data/WEBTVvideosPerVideoCategory?cid='])
        self.player_link = ''.join([self.base_link, '/templates/data/player?cid={0}'])
        self.live_link = 'https://antennalivesp-lh.akamaihd.net/i/live_1@715138/master.m3u8'
        self.yt_id = 'UC0smvAbfczoN75dP0Hw4Pzw'
        self.yt_key = 'AIzaSyBOS4uSyd27OU0XV2KSdN3vT2UG_v0g9sI'

    def root(self):

        self.list = [
            {
                'title': control.lang(32001),
                'action': 'play',
                'isFolder': 'False',
                'icon': 'live.png',
                'url': self.live_link
            }
            ,
            {
                'title': control.lang(32002),
                'action': 'listing',
                'icon': 'shows.png',
                'url': self.shows_link
            }
            ,
            {
                'title': control.lang(32003),
                'action': 'listing',
                'icon': 'archive.png',
                'url': self.archive_link
            }
            ,
            {
                'title': control.lang(32006),
                'action': 'videos',
                'icon': 'news.png',
                'url': self.news_link
            }
            ,
            {
                'title': control.lang(32007),
                'action': 'videos',
                'icon': 'weather.png',
                'url': self.weather_link
            }
            ,
            {
                'title': control.lang(32010),
                'action': 'videos',
                'icon': 'sports.png',
                'url': self.sports_link
            }
            ,
            {
                'title': control.lang(32004),
                'action': 'videos',
                'icon': 'popular.png',
                'url': self.latest_link
            }
            ,
            {
                'title': control.lang(32016),
                'action': 'webtv',
                'icon': 'webtv.png'
            }
            ,
            {
                'title': control.lang(32005),
                'action': 'youtube_channel',
                'icon': 'youtube.png'
            }
            ,
            {
                'title': control.lang(32008),
                'action': 'bookmarks',
                'icon': 'bookmarks.png'
            }
        ]

        for item in self.list:

            cache_clear = {'title': 32011, 'query': {'action': 'cache_clear'}}
            item.update({'cm': [cache_clear]})

        directory.add(self.list, content='videos')

    def bookmarks(self):

        self.list = bookmarks.get()

        if self.list is None:
            return

        for i in self.list:

            bookmark = dict((k, v) for k, v in iteritems(i) if not k == 'next')
            bookmark['delbookmark'] = i['url']
            i.update({'cm': [{'title': 32502, 'query': {'action': 'deleteBookmark', 'url': json.dumps(bookmark)}}]})

        self.list = sorted(self.list, key=lambda k: k['title'].lower())

        directory.add(self.list, content='videos')

    def youtube_channel(self):

        self.list = [
            {
                'title': 32013,
                'action': 'videos',
                'icon': 'youtube.png',
                'url': self.yt_id

            }
            ,
            {
                'title': 32012,
                'action': 'playlists',
                'icon': 'youtube.png'
            }
        ]

        directory.add(self.list)

    def playlists(self):

        self.list = cache.get(youtube.youtube(key=self.yt_key).playlists, 12, self.yt_id)

        if self.list is None:
            return

        for i in self.list:

            i.update({'action': 'videos'})
            bookmark = dict((k, v) for k, v in iteritems(i) if not k == 'next')
            bookmark['bookmark'] = i['url']
            i.update({'cm': [{'title': 32501, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        directory.add(self.list, content='videos')

    def items_list(self, url):

        html = client.request(url)

        items = client.parseDOM(html, 'article', attrs={'class': 'item overlay grid__col-xs-6 grid__col-lg-4'})

        for item in items:

            title = client.parseDOM(item, 'h2')[0]
            image = client.parseDOM(item, 'img', ret='src')[0]
            url = client.parseDOM(item, 'a', attrs={'rel': 'bookmark'}, ret='href')[0]
            url = ''.join([self.base_link, url, '/videos'])
            plot = client.parseDOM(item, 'p', attrs={'class': 'excerpt visible__md'})[0]

            self.list.append({'title': title, 'image': image, 'url': url, 'plot': plot})

        return self.list

    def listing(self, url):

        self.list = cache.get(self.items_list, 24, url)

        if self.list is None:
            return

        for i in self.list:

            i.update({'action': 'videos'})
            bookmark = dict((k, v) for k, v in iteritems(i) if not k == 'next')
            bookmark['bookmark'] = i['url']
            i.update({'cm': [{'title': 32501, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        directory.add(self.list, content='videos')

    def video_list(self, url):

        html = client.request(url)

        if 'webtv' in url:
            attribute = 'library-add-container.+?'
        else:
            attribute = 'item overlay grid__.+?'

        tag = 'article'

        items = client.parseDOM(html, tag, attrs={'class': attribute})

        if "contentContainer_totalpages" in html or ('totalpages' in html and 'webtv' in url and not 'showall' in url):

            totalPages = int(re.search(r'totalpages = (\d+);', html).group(1))

            if 'webtv' in url:
                pattern = r'var cid = (\d+);'
            else:
                pattern = r'/templates/data/morevideos\?aid=(\d+)'

            seriesId = re.search(pattern, html).group(1)
            threads = []

            for i in list(range(2, totalPages + 1)):
                if 'webtv' in url:
                    threads.append(workers.Thread(self.thread, ''.join([self.more_web_videos, seriesId, "&p=", str(i), '&h=15']), i - 1))
                else:
                    threads.append(workers.Thread(self.thread, ''.join([self.more_videos, seriesId, "&p=", str(i), ]), i - 1))
                self.data.append('')

            [i.start() for i in threads]
            [i.join() for i in threads]

            for i in self.data:
                items.extend(client.parseDOM(i, tag, attrs={'class': attribute}))

        for item in items:

            title = client.parseDOM(item, 'h2')[0]
            image = client.parseDOM(item, 'img', ret='src')[0]

            try:
                url = client.parseDOM(item, 'a', attrs={'rel': 'bookmark'}, ret='href')[0]
            except IndexError:
                url = client.parseDOM(item, 'a', attrs={'class': 'has-video'}, ret='href')[0]

            url = ''.join([self.base_link, url])

            try:
                plot = client.parseDOM(item, 'p', attrs={'class': 'excerpt visible__md.+?'})[0]
            except IndexError:
                plot = title

            self.list.append({'title': title, 'image': image, 'url': url, 'plot': plot})

        return self.list

    def videos(self, url):

        if url == self.yt_id:
            self.list = cache.get(youtube.youtube(key=self.yt_key, replace_url=False).videos, 1, url)
        elif url.startswith('http'):
            self.list = cache.get(self.video_list, 24, url)
        else:
            self.list = cache.get(youtube.youtube(key=self.yt_key, replace_url=False).playlist, 3, url)

        if self.list is None:
            return

        for i in self.list:
            i.update({'action': 'play', 'isFolder': 'False'})

        control.sortmethods()
        control.sortmethods('title')

        if 'webtv' in url and not 'showall' in url and url != self.latest_link:

            more = {
                'title': control.lang(32015),
                'url': url + '?showall',
                'action': 'videos',
                'icon': 'next.png'
            }

            self.list.insert(-1, more)

        directory.add(self.list, content='videos')

    def webtv(self):

        self.list = [
            {
                'title': control.lang(32021), # top
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/4676/top-thema?showall'])
            }
            ,
            {
                'title': control.lang(32017), # politics
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/3049/politiki?showall'])
            }
            ,
            {
                'title': control.lang(32020), # society
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/3060/koinonia?showall'])
            }
            ,
            {
                'title': control.lang(32024), # world
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/3060/koinonia?showall'])
            }
            ,
            {
                'title': control.lang(32028), # newspapers
                'action': 'videos',
                'url': ''.join([self.base_link, 'webtv/4674/efimerides?showall'])
            }
            ,
            {
                'title': control.lang(32023), # strange
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/5274/paraxena?showall'])
            }
            ,
            {
                'title': control.lang(32025), # trailers
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/5104/ant1-trailers?showall'])
            }
            ,
            {
                'title': control.lang(32014), # life
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/5271/life?showall'])
            }
            ,
            {
                'title': control.lang(32026), # interviews
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/4348/synenteyxeis-kalesmenon?showall'])
            }
            ,
            {
                'title': control.lang(32030),  # guests
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/4963/kalesmenoi?showall'])
            }
            ,
            {
                'title': control.lang(32019), # fashion
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/4491/moda?showall'])
            }
            ,
            {
                'title': control.lang(32029), # beauty
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/5089/beauty?showall'])
            }
            ,
            {
                'title': control.lang(32022), # gossip
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/4492/gossip?showall'])
            }
            ,
            {
                'title': control.lang(32018), # recipes
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/4349/syntages?showall'])
            }
            ,
            {
                'title': control.lang(32027), # astrology
                'action': 'videos',
                'url': ''.join([self.base_link, '/webtv/4350/zodia?showall'])
            }
        ]

        directory.add(self.list)

    def play(self, url):

        meta = None

        stream = self.resolve(url)

        if stream == self.live_link:

            meta = {'title': 'Ant1 TV'}

        try:
            addon_enabled = control.addon_details('inputstream.adaptive').get('enabled')
        except KeyError:
            addon_enabled = False

        if int(
                control.infoLabel('System.AddonVersion("xbmc.python")').replace('.', '')
        ) >= 2260 and 'm3u8' in stream and addon_enabled:

            m3u8_dash = True

        else:

            m3u8_dash = False

        directory.resolve(
            stream, meta=meta, dash=stream.endswith('.mpd') or m3u8_dash,
            manifest_type='hls' if m3u8_dash else None, mimetype='application/vnd.apple.mpegurl' if m3u8_dash else None
        )

    def resolve(self, url):

        if url == self.live_link:

            return url

        elif 'youtube' in url or len(url) == 11:

            return self.yt_session(url)

        else:

            id = re.search(r'watch/(\d+)/', url).group(1)
            json_ = json.loads(client.request(self.player_link.format(id)))
            media_url = json_['url']

            return media_url

    @staticmethod
    def yt_session(yt_id):

        streams = yt_resolver(yt_id)

        try:
            addon_enabled = control.addon_details('inputstream.adaptive').get('enabled')
        except KeyError:
            addon_enabled = False

        if not addon_enabled:
            streams = [s for s in streams if 'mpd' not in s['title'].lower()]

        stream = streams[0]['url']

        return stream

    def thread(self, url, i):

        try:
            result = client.request(url, timeout=20)
            self.data[i] = result
            sleep(0.05)
        except Exception:
            return
