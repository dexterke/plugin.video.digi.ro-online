#!/usr/bin/env python
# -*- coding: utf-8 -*-

####################################################
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# 2019 Dexterke, SECRET LABORATORIES  <dexterkexnet@yahoo.com>
####################################################

import HTMLParser as html
import logging
import os
import re
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import requests
import json
from bs4 import BeautifulSoup

"""Settings."""
settings = xbmcaddon.Addon(id='plugin.video.digi.ro-online')
cfg_dir = xbmc.translatePath(settings.getAddonInfo('profile'))
login_Type = settings.getSetting('login_Type')
login_User = settings.getSetting('login_User')
login_Password = settings.getSetting('login_Password')
debug_Enabled = settings.getSetting('debug_Enabled')
osdInfo_Enabled = settings.getSetting('popup_Enabled')

mainHost = 'digionline.ro'
digiwebSite = 'www.digionline.ro'
epgURL = 'https://' + digiwebSite + '/epg-xhr'
apiURL = 'https://' + digiwebSite + '/api/stream'

if login_Type == 'Digi-Online':
    loginURL = 'https://www.digionline.ro/auth/login'
    post_auth = {
      'form-login-email': login_User,
      'form-login-password': login_Password
    }
elif login_Type == 'Digi-Romania':
    loginURL = 'https://www.digionline.ro/auth/login-digiro'
    post_auth = {
      'form-login-digiro-email': login_User,
      'form-login-digiro-password': login_Password
    }
else:
    xbmcgui.Dialog().ok(
      'Add-on config error', 'Please configure this Add-on'
    )

connection = 'keep-alive'
deviceId = None

userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'

log_File = os.path.join(cfg_dir, 'plugin_video_digionline.ro.log')
html_f_1 = os.path.join(cfg_dir, mainHost + '_1.html')
html_f_2 = os.path.join(cfg_dir, mainHost + '_2.html')
html_f_3 = os.path.join(cfg_dir, mainHost + '_3.html')
html_f_4 = os.path.join(cfg_dir, mainHost + '_4.html')
cookiefile = os.path.join(cfg_dir, mainHost + '.cookie')

search_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'search.png')
movies_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'movies.png')
next_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'next.png')
addon_thumb = os.path.join(settings.getAddonInfo('path'), 'icon.png')
addon_fanart = os.path.join(settings.getAddonInfo('path'), 'fanart.jpg')


def setIcon(thumb_file):
    try:
        thumb_file_name = os.path.join(
            settings.getAddonInfo('path'), 'resources', 'media', thumb_file
        )
    except:
        thumb_file_name = movies_thumb

    return thumb_file_name

channels = [
    {'title': 'Digi24', 'path': 'stiri/digi24', 'icon': 'Digi24.png'},
    {'title': 'B1 TV', 'path': 'stiri/b1tv', 'icon': 'B1TV.png'},
    {'title': 'Realitatea TV', 'path': 'stiri/realitatea-tv', 'icon': 'RealitateaTV.png'},
    {'title': 'Romania TV', 'path': 'stiri/romania-tv', 'icon': 'RomaniaTV.png'},
    {'title': 'France 24 [EN]', 'path': 'extern/france-24', 'icon': 'France24.png'},
    {'title': 'TV5 Monde [FR]', 'path': 'extern/tv5-monde', 'icon': 'tv5monde.png'},
    {'title': 'CNN [EN]', 'path': 'extern/cnn', 'icon': 'CNN.png'},
    {'title': 'Travel Channel', 'path': 'lifestyle/travel-channel', 'icon': 'TravelChannel.png'},
    {'title': 'Paprika TV', 'path': 'lifestyle/tv-paprika', 'icon': 'PaprikaTV.png'},
    {'title': 'Digi Life', 'path': 'tematice/digi-life', 'icon': 'DigiLife.png'},
    {'title': 'Digi World', 'path': 'tematice/digi-world', 'icon': 'DigiWorld.png'},
    {'title': 'Viasat Explorer', 'path': 'tematice/viasat-explorer', 'icon': 'ViasatExplore.png'},
    {'title': 'Discovery Channel', 'path': 'tematice/discovery-channel', 'icon': 'DiscoveryChannel.png'},
    {'title': 'National Geographic', 'path': 'tematice/national-geographic', 'icon': 'NatGeographic.png'},
    {'title': 'History Channel', 'path': 'tematice/history-channel', 'icon': 'HistoryChannel.png'},
    {'title': 'Viasat History', 'path': 'tematice/viasat-history', 'icon': 'ViasatHistory.png'},
    {'title': 'National Geographic Wild', 'path': 'tematice/national-geographic-wild', 'icon': 'NatGeoWild.png'},
    {'title': 'BBC Earth', 'path': 'tematice/bbc-earth', 'icon': 'BBC_Earth.png'},
    {'title': 'Digi Animal World', 'path': 'tematice/digi-animal-world', 'icon': 'DigiAnimalWorld.png'},
    {'title': 'Viasat Nature', 'path': 'tematice/viasat-nature', 'icon': 'ViasatNature.png'},
    {'title': 'Cinethronix', 'path': 'tematice/cinethronix', 'icon': 'Cinethronix.png'},
    {'title': 'HGTV', 'path': 'lifestyle/hgtv', 'icon': 'HGTV.png'},
    {'title': 'Fishing & Hunting', 'path': 'lifestyle/fishing-and-hunting', 'icon': 'PVTV.png'},
    {'title': 'CBS Reality', 'path': 'lifestyle/cbs-reality', 'icon': 'CBSReality.png'},
    {'title': 'TLC Entertainment', 'path': 'tematice/tlc', 'icon': 'TLC.png'},
    {'title': 'Travel Mix', 'path': 'lifestyle/travel-mix-channel', 'icon': 'TravelMix.png'},
    {'title': 'E Entertainment', 'path': 'lifestyle/e-entertainment', 'icon': 'EpopDeCulture.png'},
    {'title': 'AXN', 'path': 'filme/axn', 'icon': 'AXN.png'},
    {'title': 'AXN Spin', 'path': 'filme/axn-spin', 'icon': 'AXN_Spin.png'},
    {'title': 'AXN White', 'path': 'filme/axn-white', 'icon': 'AXN_White.png'},
    {'title': 'AXN Black', 'path': 'filme/axn-black', 'icon': 'AXN_Black.png'},
    {'title': 'Film Cafe', 'path': 'filme/film-cafe', 'icon': 'FilmCafe.png'},
    {'title': 'Comedy Central', 'path': 'filme/comedy-central', 'icon': 'Comedy-Central.png'},
    {'title': 'TNT', 'path': 'filme/tnt', 'icon': 'TNT2.png'},
    {'title': 'TV1000', 'path': 'filme/tv-1000', 'icon': 'TV1000.png'},
    {'title': 'Paramount Channel', 'path': 'filme/paramount-channel', 'icon': 'Paramount-Channel.png'},
    {'title': 'AMC', 'path': 'filme/amc', 'icon': 'AMC.png'},
    {'title': 'Epic Drama', 'path': 'filme/epic-drama', 'icon': 'Epic-Drama.png'},
    {'title': 'Bollywood TV', 'path': 'filme/bollywood-tv', 'icon': 'BollywoodTV.png'},
    {'title': 'Cinemaraton', 'path': 'filme/cinemaraton', 'icon': 'CineMaraton.png'},
    {'title': 'Comedy-Est', 'path': 'filme/comedy-est', 'icon': 'ComedyEst.png'},
    {'title': 'UTV', 'path': 'muzica/u-tv', 'icon': 'UTV.png'},
    {'title': 'Music Channel', 'path': 'muzica/music-channel', 'icon': 'MusicChannel.png'},
    {'title': 'Kiss TV', 'path': 'muzica/kiss-tv', 'icon': 'KissTV.png'},
    {'title': 'HitMusic Channel', 'path': 'muzica/hit-music-channel', 'icon': 'HitMusicChannel.png'},
    {'title': 'Mezzo', 'path': 'muzica/mezzo', 'icon': 'Mezzo.png'},
    {'title': 'Slager TV [HU]', 'path': 'muzica/slager-tv', 'icon': 'SlagerTV.png'},
    {'title': 'Disney Channel', 'path': 'copii/disney-channel', 'icon': 'DisneyChannel.png'},
    {'title': 'Nickelodeon', 'path': 'copii/nickelodeon', 'icon': 'Nickelodeon.png'},
    {'title': 'Minimax', 'path': 'copii/minimax', 'icon': 'Minimax.png'},
    {'title': 'Disney Junior', 'path': 'copii/disney-junior', 'icon': 'DisneyJunior.png'},
    {'title': 'Cartoon Network', 'path': 'copii/cartoon-network', 'icon': 'CartoonNetw.png'},
    {'title': 'Boomerang', 'path': 'copii/boomerang', 'icon': 'Boomerang.png'},
    {'title': 'Davinci Learning', 'path': 'copii/davinci-learning', 'icon': 'DaVinciLearning.png'},
    {'title': 'JimJam', 'path': 'copii/jimjam', 'icon': 'JimJam.png'},
    {'title': 'DigiSport 1', 'path': 'sport/digisport-1', 'icon': 'DigiSport1.png'},
    {'title': 'DigiSport 2', 'path': 'sport/digisport-2', 'icon': 'DigiSport2.png'},
    {'title': 'DigiSport 3', 'path': 'sport/digisport-3', 'icon': 'DigiSport3.png'},
    {'title': 'DigiSport 4', 'path': 'sport/digisport-4', 'icon': 'DigiSport4.png'},
    {'title': 'EuroSport 1', 'path': 'sport/eurosport', 'icon': 'EuroSport1.png'},
    {'title': 'EuroSport 2', 'path': 'sport/eurosport2', 'icon': 'EuroSport2.png'},
    {'title': 'TVR 1', 'path': 'general/tvr1', 'icon': 'TVR1.png'},
    {'title': 'TVR 2', 'path': 'general/tvr2', 'icon': 'TVR2.png'},
]


def ROOT():
    """Default view & build channel list."""

    for channel in channels:
        url = ''.join(('https://', digiwebSite, '/', channel['path']))
        addDir(channel['title'], url, setIcon(channel['icon']))

    """
    # DRM
    addDir('Cinemax', 'https://www.digionline.ro/filme/cinemax', setIcon('Cinemax.png'))
    addDir('Cinemax2', 'https://www.digionline.ro/filme/cinemax-2', setIcon('Cinemax2.png'))
    addDir('HBO Ro', 'https://www.digionline.ro/filme/hbo', setIcon('HBO.png'))
    addDir('HBO 2', 'https://www.digionline.ro/filme/hbo2', setIcon('HBO2.png'))
    addDir('HBO 3', 'https://www.digionline.ro/filme/hbo3', setIcon('HBO3.png'))
    """


def addDir(name, url, iconimage):
    iconimage = urllib.unquote(urllib.unquote(iconimage))
    u = (
        sys.argv[0] +
        '?url=' + urllib.quote_plus(url) +
        '&name=' + urllib.quote_plus(name) +
        '&thumb=' + urllib.quote_plus(iconimage)
    )
    listedItem = xbmcgui.ListItem(name, iconImage=movies_thumb, thumbnailImage=iconimage)
    listedItem.setInfo(
        'video', {
            'mediatype': 'video',
            'genre': 'Live Stream',
            'title': name,
            'playcount': '0'
        }
    )
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=listedItem)
    write2file(log_File, "addDir: '" + name + "', '" + url + "', '" + iconimage, 'a')
    return ok


def getParams():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    """
    ------------------------------------------------------------------------
    'url': 'http%3A%2F%2Fdigionline.hu%2Ftv%SOME%2Btv%2F', 'name': 'SOME+TV'
    ------------------------------------------------------------------------
    """
    write2file(log_File, 'getParams: ' + str(param), 'a')
    return param


def processHTML(url):
    """Load HTML, extract playlist URL & 'now playing' info."""
    global result
    global nowPlaying_Info
    global nowPlaying_Plot
    global deviceId
    global session
    global theader

    link = None
    session = None
    category = None
    req = None
    html_text = None
    sp_code = 404
    json_data = None
    html_parser = html.HTMLParser()
    url = html_parser.unescape(url)

    try:
        category = str(re.compile('.ro/(.+?)/').findall(url)[0])
    except:
        pass

    write2file(log_File, 'processHTML received URL: ' + url + ' - Section: ' + str(category) + '\n', 'a')

    """Step 1 - Load login URL, session acquire cookies."""
    headers = {
      'Host': digiwebSite,
      'Connection': connection,
      'Cache-Control': 'max-age=0',
      'Upgrade-Insecure-Requests': '1',
      'User-Agent': userAgent,
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
      'Accept-Encoding': 'identity',
      'Accept-Language': 'en-ie'
    }

    try:
        requests.packages.urllib3.disable_warnings()
        session = requests.Session()
        if debug_Enabled == 'true':
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger('requests.packages.urllib3')
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

        if os.path.isfile(cookiefile) and os.path.getsize(cookiefile) > 0:
            """Load device ID from cookie value."""
            try:
                with open(cookiefile) as f:
                    deviceId = f.readline().strip()
                write2file(log_File, 'processHTML deviceId from file:' + str(deviceId), 'a')
            except Exception as err:
                write2file(log_File, 'processHTML ERROR: ' + str(err), 'a')
        else:
            write2file(log_File, 'processHTML WARNING: File ' + str(cookiefile) + ' does not exist', 'a')

        session.cookies.set('prv_level', '15', domain=digiwebSite, path='/')
        if deviceId is not None:
            session.cookies.set('deviceId', deviceId, domain=digiwebSite, path='/')

        write2file(log_File, 'processHTML session cookies: ' + str(session.cookies.get_dict()), 'a')
        req = session.get(loginURL, headers=headers, verify=False)
        log_http_session(req, headers, 'GET', '', 0)
        write2file(html_f_1, req.content, 'w')

    except Exception as err:
        msg = 'processHTML ERROR: Could not fetch ' + loginURL + " - " + str(err)
        write2file(log_File, msg, 'a')
        xbmcgui.Dialog().ok('Error', msg)

    """Step 2 - Login to https://www.digionline.ro/auth/login."""
    if req.status_code == 200:
        if osdInfo_Enabled == 'true':
            xbmc.executebuiltin('Notification(DigiOnline.ro, ' + nowPlayingTitle + ')')

        headers = {
            'Host': digiwebSite,
            'Connection': connection,
            'Cache-Control': 'max-age=0',
            'Origin': 'https://www.digionline.ro',
            'Upgrade-Insecure-Requests': '1',
            'Content-type': 'application/x-www-form-urlencoded',
            'User-Agent': userAgent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://www.digionline.ro/auth/login',
            'Accept-Encoding': 'identity',
            'Accept-Language': 'en-ie'
        }
        try:
            write2file(log_File, 'processHTML session cookies: ' + str(session.cookies.get_dict()), 'a')
            req = session.post(loginURL, headers=headers, data=post_auth)
            sp_code = req.status_code
            log_http_session(req, headers, 'POST', post_auth, 0)
            write2file(html_f_2, req.content, 'w')

            if re.compile('<div class="form-error mb-10 color-red" style="font-size:18px; font-family: modena-bold;">').findall(req.content):
                errMSG = html_parser.unescape(str((re.compile('<div class="form-error mb-10 color-red" style="font-size:18px; font-family: modena-bold;">\n\s+(.+?)&period;\s+<\/div>').findall(req.content))[0])).replace("&period;", ".")
                write2file(log_File, 'processHTML Login Error: ' + errMSG, 'a')
                xbmcgui.Dialog().ok('Error', errMSG)
                sp_code = 401

            if re.compile('Deja ati inregistrat numarul maxim de dispozitive').findall(req.content):
                msg = 'Deja ati inregistrat numarul maxim de dispozitive. Puteti sa le administrati din Contul Meu Digi.'
                write2file(log_File, msg, 'a')
                xbmcgui.Dialog().ok('Error', msg)

        except Exception as err:
            msg = 'processHTML login Error: ' + str(err)
            write2file(log_File, msg, 'a')
            xbmcgui.Dialog().ok('Error', msg)

        if sp_code != 200:
            msg = 'processHTML login Error: HTTP code ' + str(sp_code)
            write2file(log_File, msg, 'a')
            xbmcgui.Dialog().ok('Error', msg)

        """Save cookie."""
        if sp_code == 200 and category is not None:
            for key, value in session.cookies.get_dict().iteritems():
                write2file(log_File, 'processHTML session cookie: ' + str(key) + ', value: ' + str(value), 'a')
                if str(key) == "deviceId":
                    try:
                        write2file(log_File, 'Saving cookiefile: ' + str(cookiefile), 'a')
                        file = open(cookiefile, 'w')
                        file.write(value)
                        file.close()
                    except Exception as err:
                        write2file(log_File, 'processHTML ERROR: Could not write cookiefile: ' + str(err), 'a')

            """Step 3 - Load TV Channel URL"""
            headers = {
                'Host': digiwebSite,
                'Connection': connection,
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': userAgent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Cache-Control': 'max-age=0',
                'Referer': 'https://' + digiwebSite + '/' + category,
                'Accept-Encoding': 'identity',
                'Accept-Language': 'en-ie'
            }
            theader = headers

            try:
                write2file(log_File, 'processHTML session cookies: ' + str(session.cookies.get_dict()), 'a')
                req = session.get(url, headers=headers, verify=False)
                html_text = req.content
                log_http_session(req, headers, 'GET', '', 0)
                write2file(html_f_3, req.content, 'w')
                if req.status_code != 200:
                    msg = 'processHTML ERROR: Could not fetch ' + str(url) + ', HTTP code ' + str(req.status_code)
                    write2file(log_File, msg, 'a')
                    xbmcgui.Dialog().ok('Error', msg)
            except:
                msg = 'processHTML ERROR: Could not fetch ' + str(url)
                write2file(log_File, msg, 'a')
                xbmcgui.Dialog().ok('Error', msg)

            try:
                """Extract 'now-playing' info from HTML."""
                nowPlaying_Info = " - "
                if osdInfo_Enabled == 'true':
                    txt = str((re.compile('<h2 class="section-title-alt" id="title">(.+?)<\/h2>').findall(html_text))[0])
                    write2file(log_File, 'processHTML nowPlaying txt: ' + txt, 'a')
                    nowPlaying_Info = BeautifulSoup(txt, 'html5lib').text.strip()
            except Exception as err:
                write2file(log_File, 'processHTML ERROR: could not detect nowPlaying_Info: ' + str(err), 'a')

            try:
                """Extract 'now-playing' plot from HTML."""
                nowPlaying_Plot = " - "
                if osdInfo_Enabled == 'true':
                    txt = str((re.compile(r'<p id="synopsis">(.+?)<\/p>', re.DOTALL).findall(html_text))[0])
                    write2file(log_File, 'processHTML nowPlaying plot: ' + txt, 'a')
                    nowPlaying_Plot = BeautifulSoup(txt, 'html5lib').text.strip()
            except Exception as err:
                write2file(log_File, 'processHTML ERROR: could not detect nowPlaying_Plot: ' + str(err), 'a')

            """Step 4 - Process HTTP data"""
            if req.status_code == 200 and html_text is not None:
                streamId = None
                """Get channel ID"""
                try:
                    streamId = str((re.compile('"streamId":(.+?),').findall(html_text))[0])
                    write2file(log_File, 'processHTML nowPlayingTitle: ' + nowPlaying_Info, 'a')
                    write2file(log_File, 'processHTML streamId: ' + streamId, 'a')
                    write2file(log_File, 'processHTML category: ' + category, 'a')
                except:
                    pass

                if streamId is not None:
                    headers = {
                        'Host': digiwebSite,
                        'Connection': connection,
                        'Accept': '*/*',
                        'Origin': 'https://www.digionline.ro',
                        'X-Requested-With': 'XMLHttpRequest',
                        'User-Agent': userAgent,
                        'Upgrade-Insecure-Requests': '1',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Referer': url,
                        'Accept-Encoding': 'identity',
                        'Accept-Language': 'en-ie'
                    }

                    try:
                        write2file(log_File, 'processHTML session cookies: ' + str(session.cookies.get_dict()), 'a')
                        post_data = {'id_stream': streamId, 'quality': 'hq'}
                        req = session.post(apiURL, headers=headers, data=post_data, verify=False)
                        json_data = req.content
                        log_http_session(req, headers, 'POST', post_data, 1)

                    except Exception as err:
                        write2file(log_File, 'processHTML ERROR: Could not POST apiURL: ' + apiURL + ' Error: ' + str(err), 'a')
                        xbmcgui.Dialog().ok('Error', 'Could not POST apiURL: ' + apiURL + ' Error: ' + str(err))

                    """Step 5 - Extract playlist link"""
                    if json_data is not None:
                        stream_url = json.loads(json_data)
                        write2file(log_File, 'processHTML json stream_url: ' + str(stream_url), 'a')
                        link = str(stream_url["stream_url"])
                        if 'https://' not in link:
                            link = ''.join(('https:', link + '|User-Agent=' + userAgent + '&Referer=' + url))
                        write2file(log_File, 'processHTML detected link: ' + str(link), 'a')
                        digiHost = str(re.compile('https://(.+?)/').findall(link)[0])
                        write2file(log_File, 'processHTML digiHost: ' + str(digiHost), 'a')
                        headers = {
                            'Host': digiHost,
                            'Connection': 'keep-alive',
                            'Origin': 'https://www.digionline.ro',
                            'User-Agent': userAgent,
                            'Accept': '*/*',
                            'Referer': url,
                            'Accept-Encoding': 'identity',
                            'Accept-Language': 'en-ie'
                        }
                        write2file(log_File, 'processHTML session cookies: ' + str(session.cookies.get_dict()), 'a')
                        try:
                            req = session.get(link, headers=headers, verify=False)
                            result = req.content
                            log_http_session(req, headers, 'GET', '', 1)
                        except Exception as err:
                            msg = 'processHTML ERROR: Could not acquire playlist: ' + str(err)
                            write2file(log_File, msg, 'a')
                            xbmcgui.Dialog().ok('Error', msg)

    return link


def parseInput(url):
    """Start player"""
    global result

    result = None
    item = None
    logMyVars()
    write2file(log_File, 'parseInput received URL: ' + url, 'a')
    link = processHTML(url)

    if result is not None:
        try:
            item = xbmcgui.ListItem(path=link, iconImage=addon_thumb, thumbnailImage=nowPlayingThumb)
            item.setInfo(
                'video', {
                    'mediatype': 'video',
                    'genre': 'Live Stream',
                    'title': nowPlayingTitle,
                    'tagline': nowPlaying_Info,
                    'plot': nowPlaying_Plot,
                    'playcount': '1'
                }
            )
            write2file(log_File, 'parseInput link ' + str(link), 'a')
        except Exception as err:
            msg = 'parseInput ERROR: ' + str(err)
            write2file(log_File, msg, 'a')
            xbmcgui.Dialog().ok('Error', msg)

        """Step 5 - Play stream."""
        if item is not None and result is not None:
            xbmcplugin.setContent(int(sys.argv[1]), 'videos')
            xbmc.Player().play(link, item)
            write2file(log_File, 'xbmc.Player().play(' + link + ',' + str(item) + ')', 'a')
            if osdInfo_Enabled == 'true':
                xbmc.executebuiltin('Notification(' + nowPlayingTitle + ', ' + nowPlaying_Info + ')')


def write2file(myFile, text, append):
    """
    append param.
    :: w = write
    :: a = append
    """
    if debug_Enabled == 'true':
        try:
            file = open(myFile, append)
            file.write(text + '\n')
            file.close()
        except IOError:
            xbmcgui.Dialog().ok('Error', 'Could not write to logfile')


def log_http_session(session, header, method, post_data, echo):
    """Debug"""
    write2file(log_File, 'processHTML method: ' + method, 'a')
    write2file(log_File, 'processHTML url ' + str(session.url), 'a')
    write2file(log_File, 'processHTML send headers: ' + str(header), 'a')
    if method == 'POST':
        write2file(
            log_File,
            'processHTML post_data: ' + str(post_data), 'a'
        )
    write2file(
        log_File,
        'processHTML status_code: ' + str(session.status_code), 'a'
    )
    write2file(
        log_File,
        'processHTML received headers: ' + str(session.headers), 'a'
    )
    write2file(
        log_File, 'processHTML received cookies: ' +
        str(session.cookies.get_dict()), 'a'
    )
    for cookie in (session.cookies):
        write2file(
            log_File,
            'processHTML cookie: ' + str(cookie.__dict__), 'a'
        )
    write2file(log_File, '\n', 'a')
    if echo:
        write2file(
            log_File,
            'processHTML received data: ---------- \n' +
            str(session.content), 'a'
        )


def logMyVars():
    """Blabla & cleanup"""
    if debug_Enabled == 'true':
        write2file(log_File, "Python version: " + str(sys.version), 'w')
        write2file(log_File, "Python info: " + str(sys.version_info), 'a')
        write2file(
            log_File, "osdInfo_Enabled: " + str(osdInfo_Enabled) +
            "\nuserAgent: " + userAgent +
            "\nLogin_User: " + str(login_User), 'a'
        )
        write2file(log_File, "cfg_dir: " + str(cfg_dir), 'a')
    else:
        try:
            if os.path.isfile(log_File):
                os.remove(log_File)
            if os.path.isfile(html_f_1):
                os.remove(html_f_1)
            if os.path.isfile(html_f_2):
                os.remove(html_f_2)
            if os.path.isfile(html_f_3):
                os.remove(html_f_3)
            if os.path.isfile(html_f_4):
                os.remove(html_f_4)
        except:
            xbmcgui.Dialog().ok('Error', 'Could not clean logs')


"""Run this Add-on"""
params = getParams()
url = None
nowPlayingThumb = None
nowPlayingTitle = None
nowPlaying_Info = None
nowPlaying_Plot = None
logMyVars()

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass

try:
    nowPlayingTitle = urllib.unquote_plus(params["name"])
except:
    nowPlayingTitle = str(url)

try:
    nowPlayingThumb = urllib.unquote_plus(params["thumb"])
except:
    nowPlayingThumb = movies_thumb

if url is None or len(url) < 1:
    ROOT()
else:
    parseInput(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
