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

from resources.lib import antenna, action, url


if action is None:
    antenna.Indexer().root()

elif action == 'listing':
    antenna.Indexer().listing(url)

elif action == 'videos':
    antenna.Indexer().videos(url)

elif action == 'youtube_channel':
    antenna.Indexer().youtube_channel()

elif action == 'playlists':
    antenna.Indexer().playlists()

elif action == 'play':
    antenna.Indexer().play(url)

elif action == 'addBookmark':
    from tulip import bookmarks
    bookmarks.add(url)

elif action == 'deleteBookmark':
    from tulip import bookmarks
    bookmarks.delete(url)

elif action == 'bookmarks':
    antenna.Indexer().bookmarks()

elif action == 'cache_clear':
    from tulip import cache
    cache.clear(withyes=False)
