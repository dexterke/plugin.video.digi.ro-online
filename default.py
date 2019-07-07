#!/usr/bin/env python
# -*- coding: utf-8 -*-

####################################################
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# 2019 Dexterke, SECRET LABORATORIES  <dexterkexnet@yahoo.com>
####################################################
import HTMLParser
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

## Settings
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

if login_Type == "Digi-Online":
    loginURL = 'https://www.digionline.ro/auth/login'
    post_auth={'form-login-email': login_User, 'form-login-password': login_Password}
elif login_Type == "Digi-Romania":
    loginURL = 'https://www.digionline.ro/auth/login-digiro'
    post_auth={'form-login-digiro-email': login_User, 'form-login-digiro-password': login_Password}
else:
    xbmcgui.Dialog().ok('Plugin config error', 'Please configure this plugin')

#deviceId = '03b86b83f30e2e84bd886d89343792e8.Chrome_72_Mac_a3892b32be1a471b2b1c66577299d295_PCBROWSER'
deviceId = None
userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'

log_File   = os.path.join(cfg_dir, 'plugin_video_digionline.ro.log')
html_f_1   = os.path.join(cfg_dir, str(mainHost) + '_1.html')
html_f_2   = os.path.join(cfg_dir, str(mainHost) + '_2.html')
html_f_3   = os.path.join(cfg_dir, str(mainHost) + '_3.html')
html_f_4   = os.path.join(cfg_dir, str(mainHost) + '_4.html')
html_f_5   = os.path.join(cfg_dir, str(mainHost) + '_5.html')
cookiefile = os.path.join(cfg_dir, str(mainHost) + '.cookie')

search_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'search.png')
movies_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'movies.png')
next_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'next.png')
addon_thumb = os.path.join(settings.getAddonInfo('path'), 'icon.png')
addon_fanart = os.path.join(settings.getAddonInfo('path'), 'fanart.jpg')


def setIcon(thumb_file):
  thumb_file_name = thumb_file.replace(' ', '')[:-4].upper()
  try:
    thumb_file_name = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', thumb_file)
  except:
    thumb_file_name = movies_thumb
  return thumb_file_name


def ROOT():
    addDir('Digi24', 'https://www.digionline.ro/stiri/digi24', setIcon('Digi24.png'))
    addDir('B1 TV', 'https://www.digionline.ro/stiri/b1tv', setIcon('B1TV.png'))
    addDir('Realitatea TV', 'https://www.digionline.ro/stiri/realitatea-tv', setIcon('RealitateaTV.png'))
    addDir('Romania TV', 'https://www.digionline.ro/stiri/romania-tv', setIcon('RomaniaTV.png'))
    addDir('France 24 [EN]', 'https://www.digionline.ro/extern/france-24', setIcon('France24.png'))
    addDir('TV5 Monde [FR]', 'https://www.digionline.ro/extern/tv5-monde', setIcon('tv5monde.png'))
    addDir('CNN [EN]', 'https://www.digionline.ro/extern/cnn', setIcon('CNN.png'))

    addDir('Travel Channel', 'https://www.digionline.ro/lifestyle/travel-channel', setIcon('TravelChannel.png'))
    addDir('Paprika TV', 'https://www.digionline.ro/lifestyle/tv-paprika', setIcon('PaprikaTV.png'))
    addDir('Digi Life', 'https://www.digionline.ro/tematice/digi-life', setIcon('DigiLife.png'))
    addDir('Digi World', 'https://www.digionline.ro/tematice/digi-world', setIcon('DigiWorld.png'))
    addDir('Viasat Explorer', 'https://www.digionline.ro/tematice/viasat-explorer', setIcon('ViasatExplore.png'))
    addDir('Discovery Channel', 'https://www.digionline.ro/tematice/discovery-channel', setIcon('DiscoveryChannel.png'))
    addDir('National Geographic', 'https://www.digionline.ro/tematice/national-geographic', setIcon('NatGeographic.png'))
    addDir('History Channel', 'https://www.digionline.ro/tematice/history-channel', setIcon('HistoryChannel.png'))
    addDir('Viasat History', 'https://www.digionline.ro/tematice/viasat-history', setIcon('ViasatHistory.png'))
    addDir('National Geographic Wild', 'https://www.digionline.ro/tematice/national-geographic-wild', setIcon('NatGeoWild.png'))
    addDir('BBC Earth', 'https://www.digionline.ro/tematice/bbc-earth', setIcon('BBC_Earth.png'))
    addDir('Digi Animal World', 'https://www.digionline.ro/tematice/digi-animal-world', setIcon('DigiAnimalWorld.png'))
    addDir('Viasat Nature', 'https://www.digionline.ro/tematice/viasat-nature', setIcon('ViasatNature.png'))
    addDir('Fishing & Hunting', 'https://www.digionline.ro/lifestyle/fishing-and-hunting', setIcon('PVTV.png'))
    addDir('CBS Reality', 'https://www.digionline.ro/lifestyle/cbs-reality', setIcon('CBSReality.png'))
    addDir('TLC Entertainment', 'https://www.digionline.ro/tematice/tlc', setIcon('TLC.png'))
    addDir('Travel Mix', 'https://www.digionline.ro/lifestyle/travel-mix-channel', setIcon('TravelMix.png'))
    addDir('E Entertainment', 'https://www.digionline.ro/lifestyle/e-entertainment', setIcon('EpopDeCulture.png'))

    addDir('AXN', 'https://www.digionline.ro/filme/axn', setIcon('AXN.png'))
    addDir('AXN Spin', 'https://www.digionline.ro/filme/axn-spin', setIcon('AXN_Spin.png'))
    addDir('AXN White', 'https://www.digionline.ro/filme/axn-white', setIcon('AXN_White.png'))
    addDir('AXN Black', 'https://www.digionline.ro/filme/axn-black', setIcon('AXN_Black.png'))
    addDir('Film Cafe', 'https://www.digionline.ro/filme/film-cafe', setIcon('FilmCafe.png'))
    addDir('Comedy Central', 'https://www.digionline.ro/filme/comedy-central', setIcon('Comedy-Central.png'))
    addDir('TNT', 'https://www.digionline.ro/filme/tnt', setIcon('TNT2.png'))
    addDir('TV1000', 'https://www.digionline.ro/filme/tv-1000', setIcon('TV1000.png'))
    addDir('Epic Drama', 'https://www.digionline.ro/filme/epic-drama', setIcon('Epic-Drama.png'))
    addDir('Bollywood TV', 'https://www.digionline.ro/filme/bollywood-tv', setIcon('BollywoodTV.png'))

    ## DRM
    #addDir('FilmNow', 'https://www.digionline.ro/filme/filmnow', setIcon('filmnow.png'))
    #addDir('HBO Ro', 'https://www.digionline.ro/filme/hbo', setIcon('HBO.png'))
    #addDir('HBO 2', 'https://www.digionline.ro/filme/hbo2', setIcon('HBO2.png'))
    #addDir('HBO 3', 'https://www.digionline.ro/filme/hbo3', setIcon('HBO3.png'))

    addDir('UTV', 'https://www.digionline.ro/muzica/u-tv', setIcon('UTV.png'))
    addDir('Music Channel', 'https://www.digionline.ro/muzica/music-channel', setIcon('MusicChannel.png'))
    addDir('Kiss TV', 'https://www.digionline.ro/muzica/kiss-tv', setIcon('KissTV.png'))
    addDir('HitMusic Channel','https://www.digionline.ro/muzica/hit-music-channel', setIcon('HitMusicChannel.png'))
    addDir('Mezzo','https://www.digionline.ro/muzica/mezzo', setIcon('Mezzo.png'))
    addDir('Slager TV [HU]','https://www.digionline.ro/muzica/slager-tv', setIcon('SlagerTV.png'))

    addDir('Disney Channel', 'https://www.digionline.ro/copii/disney-channel', setIcon('DisneyChannel.png'))
    addDir('Megamax', 'https://www.digionline.ro/copii/megamax', setIcon('Megamax.png'))
    addDir('Nickelodeon', 'https://www.digionline.ro/copii/nickelodeon', setIcon('Nickelodeon.png'))
    addDir('Minimax', 'https://www.digionline.ro/copii/minimax', setIcon('Minimax.png'))
    addDir('Disney Junior', 'https://www.digionline.ro/copii/disney-junior', setIcon('DisneyJunior.png'))
    addDir('Cartoon Network', 'https://www.digionline.ro/copii/cartoon-network', setIcon('CartoonNetw.png'))
    addDir('Boomerang', 'https://www.digionline.ro/copii/boomerang', setIcon('Boomerang.png'))
    addDir('Davinci Learning', 'https://www.digionline.ro/copii/davinci-learning', setIcon('DaVinciLearning.png'))

    addDir('DigiSport 1', 'https://www.digionline.ro/sport/digisport-1', setIcon('DigiSport1.png'))
    addDir('DigiSport 2', 'https://www.digionline.ro/sport/digisport-2', setIcon('DigiSport2.png'))
    addDir('DigiSport 3', 'https://www.digionline.ro/sport/digisport-3', setIcon('DigiSport3.png'))
    addDir('DigiSport 4', 'https://www.digionline.ro/sport/digisport-4', setIcon('DigiSport4.png'))
    addDir('EuroSport 1', 'https://www.digionline.ro/sport/eurosport', setIcon('EuroSport1.png'))
    addDir('EuroSport 2', 'https://www.digionline.ro/sport/eurosport2', setIcon('EuroSport2.png'))

    addDir('TVR 1', 'https://www.digionline.ro/general/tvr1', setIcon('TVR1.png'))
    addDir('TVR 2', 'https://www.digionline.ro/general/tvr2', setIcon('TVR2.png'))

    ## dkakat
    #addDir('Digi24 Timisoara', 'https://www.digionline.ro/local/digi24-timisoara', setIcon('Digi24.png'))
    #addDir('Digi24 Oradea', 'https://www.digionline.ro/local/digi24-oradea', setIcon('Digi24.png'))
    #addDir('Digi24 Brasov', 'https://www.digionline.ro/local/digi24-brasov', setIcon('Digi24.png'))
    #addDir('Digi24 Craiova', 'https://www.digionline.ro/local/digi24-craiova', setIcon('Digi24.png'))
    #addDir('Digi24 Constanta', 'https://www.digionline.ro/local/digi24-constanta', setIcon('Digi24.png'))
    #addDir('Digi24 Iasi', 'https://www.digionline.ro/local/digi24-iasi', setIcon('Digi24.png'))


def addDir(name, url, iconimage):
    iconimage = urllib.unquote(urllib.unquote(iconimage))
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&name=" + urllib.quote_plus(name) + "&thumb=" + urllib.quote_plus(iconimage)
    listedItem = xbmcgui.ListItem(name, iconImage=movies_thumb, thumbnailImage=iconimage)
    itemInfo = {
      'type': 'Video',
      'genre': 'Live Stream',
      'title': name,
      'playcount': '0'
	}
    listedItem.setInfo('video', itemInfo)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=listedItem)
    write2file(log_File, "addDir: '" + name + "', '" + url + "', '" + iconimage, 'a', 0, 0)
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
#-----------------------------------------------------------------------------------------------------------
#'url': 'http%3A%2F%2Fdigionline.hu%2Ftv%SOME%2Btv%2F', 'name': 'SOME+TV'
#-----------------------------------------------------------------------------------------------------------
  write2file(log_File, "getParams: " + str(param) , 'a', 0, 1)
  return param


## Load HTML, extract playlist URL & 'now playing' info
def processHTML(url):
    global result
    global nowPlayingInfo
    global deviceId
    global session
    global theader

    match = None
    token = None
    link = None
    session = None
    section = None
    req = None
    html_text = None
    sp_code = 404
    json_data = None
    html_parser = HTMLParser.HTMLParser()
    url = html_parser.unescape(url)
    write2file(log_File, "processHTML received URL: " + url + '\n', 'a', 1, 0)
    section = str(re.compile('.ro/(.+?)/').findall(url)[0])

    ################### Step 1 #########################
    ## Load login URL, session acquire cookies
    headers = {
	'Host': digiwebSite,
	'Connection': 'close',
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
	if debug_Enabled == "true":
	  import logging
	  logging.basicConfig()
	  logging.getLogger().setLevel(logging.DEBUG)
	  requests_log = logging.getLogger("requests.packages.urllib3")
	  requests_log.setLevel(logging.DEBUG)
	  requests_log.propagate = True

	## load device ID from cookie value
	if os.path.isfile(cookiefile):
	  try:
	    with open(cookiefile) as f:
		deviceId = f.readline().strip()
	    write2file(log_File, 'processHTML deviceId from file:' + str(deviceId), 'a', 1, 1)
	  except Exception as err:
	    write2file(log_File, 'processHTML ERROR: Could not read ' + str(cookiefile) + ": " + str(err), 'a', 1, 1)
	else:
	  write2file(log_File, 'processHTML WARNING: File ' + str(cookiefile) + ' does not exist', 'a', 1, 1)

	session.cookies.set('prv_level', '15', domain=digiwebSite, path='/')
	if not deviceId is None:
	  session.cookies.set('deviceId', deviceId, domain=digiwebSite, path='/')

	write2file(log_File, 'processHTML session cookies: ' + str(session.cookies.get_dict()), 'a', 1, 0)
	req = session.get(loginURL, headers=headers, verify=False)
	log_http_session(req, headers, 'GET', '', 0)
	write2file(html_f_1, req.content, 'w', 0, 0)
    except Exception as err:
	write2file(log_File, 'processHTML ERROR: Could not fetch ' + str(loginURL) + " - " + str(err), 'a', 0, 1)
	xbmcgui.Dialog().ok('Error', 'Could not fetch ' + str(loginURL) + " - " + str(err))

    ################### Step 2 #########################
    ## Login to https://www.digionline.ro/auth/login
    if req.status_code == 200:
      if osdInfo_Enabled == "true":
	xbmc.executebuiltin('Notification(DigiOnline.ro, ' + nowPlayingTitle + ')')
      headers = {
	  'Host': digiwebSite,
	  'Connection': 'close',
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
	  write2file(log_File, 'processHTML session cookies: ' + str(session.cookies.get_dict()), 'a', 1, 0)
	  req = session.post(loginURL, headers=headers, data=post_auth)
	  sp_code = req.status_code
	  log_http_session(req, headers, 'POST', post_auth, 0)
	  write2file(html_f_2, req.content, 'w', 0, 0)

	  if re.compile('<div class="form-error mb-10 color-red" style="font-size:18px; font-family: modena-bold;">').findall(req.content):
	    errMSG = html_parser.unescape(str((re.compile('<div class="form-error mb-10 color-red" style="font-size:18px; font-family: modena-bold;">\n\s+(.+?)&period;\s+<\/div>').findall(req.content))[0])).replace("&period;", ".")
	    write2file(log_File, 'processHTML Login Error: ' + errMSG, 'a', 0, 1)
	    xbmcgui.Dialog().ok('Error', errMSG)
	    sp_code = 401

      except Exception as err:
	write2file(log_File, 'processHTML ERROR: Could not perfom login: ' + str(err), 'a', 0, 1)
	xbmcgui.Dialog().ok('Error', 'Could not perfom login: ' + str(err))

      if sp_code != 200:
	  write2file(log_File, 'processHTML ERROR: Could not perfom login, HTTP code: ' + str(sp_code), 'a', 0, 1)
	  xbmcgui.Dialog().ok('Error', 'Could not perfom login, HTTP code: ' + str(sp_code))

      ## Save cookie
      if sp_code == 200 and not section is None:
	for key, value in session.cookies.get_dict().iteritems():
	  write2file(log_File, 'processHTML session cookie: ' + str(key) + ', value: ' + str(value), 'a', 0, 0)
	  if str(key) == "deviceId":
	    newDevID = str(value)
	try:
	  file = open(cookiefile, 'w')
	  file.write(newDevID)
	  file.close()
	except Exception as err:
	  write2file(log_File, 'processHTML ERROR: Could not write cookiefile: ' + str(err), 'a', 0, 1)

      ################### Step 4 #########################
      ## Load URL
      if sp_code == 200 and not section is None:
	    headers = {
	      'Host': digiwebSite,
	      'Connection': 'keep-alive',
	      'Upgrade-Insecure-Requests': '1',
	      'User-Agent': userAgent,
	      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	      'Cache-Control': 'max-age=0',
	      'Referer': 'https://' + digiwebSite + '/' + section,
	      'Accept-Encoding': 'identity',
	      'Accept-Language': 'en-ie'
	    }
	    theader = headers
	    try:
		write2file(log_File, 'processHTML session cookies: ' + str(session.cookies.get_dict()), 'a', 1, 0)
		req = session.get(url, headers=headers, verify=False)
		html_text = req.content
		log_http_session(req, headers, 'GET', '', 0)
		write2file(html_f_4, req.content, 'w', 0, 0)
		if req.status_code != 200:
		    write2file(log_File, 'processHTML ERROR: Could not fetch ' + str(url) + ', HTTP Code ' + str(req.status_code), 'a', 0, 1)
		    xbmcgui.Dialog().ok('Error', 'Could not fetch ' + str(url) + "\nHTTP code " + str(req.status_code))
	    except:
		write2file(log_File, 'processHTML ERROR: Could not fetch ' + str(url), 'a', 0, 1)
		xbmcgui.Dialog().ok('Error', 'Could not fetch ' + str(url))

	    try:
		## Extract 'now-playing'
		nowPlayingInfo = " - "
		if osdInfo_Enabled == "true":
		  txt = str((re.compile('<h2 class="section-title-alt" id="title">(.+?)<\/h2>').findall(html_text))[0])
		  write2file(log_File, 'processHTML nowPlaying txt: ' + txt, 'a', 1, 0)
		  nowPlayingInfo = html_parser.unescape(txt).replace("&period;", ".").replace("&colon;", ":").replace("&amp;", "&").replace("&commat;", "@")
	    except Exception as err:
		  write2file(log_File, 'processHTML ERROR: could not detect nowPlayingInfo: ' + str(err), 'a', 0, 1)
	    ##
	    if req.status_code == 200 and html_text is not None:
	      streamId = None
	      ## CHANNEL ID
	      #########################
	      streamId = str((re.compile('"streamId":(.+?),').findall(html_text))[0])
	      #balancerKey = str((re.compile('"balancerKey":"(.+?)"').findall(html_text))[0])
	      #abr = str((re.compile('"abr":(.+?),').findall(html_text))[0])
	      write2file(log_File, 'processHTML nowPlayingTitle: ' + nowPlayingInfo, 'a', 0, 0)
	      #write2file(log_File, 'processHTML balancerKey: ' + balancerKey, 'a', 0, 0)
	      write2file(log_File, 'processHTML streamId: ' + streamId, 'a', 0, 0)
	      write2file(log_File, 'processHTML section: ' + section, 'a', 0, 0)
	      ##
	      if not streamId is None:
		headers = {
		    'Host': digiwebSite,
		    'Connection': 'close',
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
		## acquire EPG
		#try:
		    #write2file(log_File, 'processHTML session cookies: ' + str(session.cookies.get_dict()), 'a', 1, 0)
		    #post_data={'channelId': streamId}
		    #req = session.post(epgURL, headers=headers, data=post_data, verify=False)
		    #log_http_session(req, headers, 'POST', post_data, 0)
		#except Exception as err:
		  #write2file(log_File, 'processHTML ERROR: Could not POST epgURL: ' + epgURL + ' Error: ' + str(err), 'a', 0, 1)
		  #xbmcgui.Dialog().ok('Error', 'Could not POST epgURL: ' + epgURL + ' Error: ' + str(err))
		##
		try:
		    write2file(log_File, 'processHTML session cookies: ' + str(session.cookies.get_dict()), 'a', 1, 0)
		    #post_data={'id_stream': streamId, 'quality': 'abr'}
		    post_data={'id_stream': streamId, 'quality': 'hq'}
		    req = session.post(apiURL, headers=headers, data=post_data, verify=False)
		    json_data = req.content

		    log_http_session(req, headers, 'POST', post_data, 1)
		except Exception as err:
		  write2file(log_File, 'processHTML ERROR: Could not POST apiURL: ' + apiURL + ' Error: ' + str(err), 'a', 0, 0)
		  xbmcgui.Dialog().ok('Error', 'Could not POST apiURL: ' + apiURL + ' Error: ' + str(err))

		if not json_data is None:
		  stream_url = json.loads(json_data)
		  write2file(log_File, 'processHTML json stream_url: ' + str(stream_url), 'a', 1, 0)
		  link = str(stream_url["stream_url"])
		  if "https://" not in link:
		    link = "".join(("https:", link))
		  write2file(log_File, 'processHTML detected link: ' + str(link), 'a', 0, 0)
		  digiHost = str(re.compile('https://(.+?)/').findall(link)[0])
		  write2file(log_File, 'processHTML digiHost: ' + str(digiHost), 'a', 0, 0)
		  ##
		  headers = {
		      'Host': digiHost,
		      'Connection': 'close',
		      'Origin': 'https://www.digionline.ro',
		      'User-Agent': userAgent,
		      'Accept': '*/*',
		      'Referer': url,
		      'Accept-Encoding': 'identity',
		      'Accept-Language': 'en-ie'
		    }
		  write2file(log_File, 'processHTML session cookies: ' + str(session.cookies.get_dict()), 'a', 1, 0)
		  try:
		      req = session.get(link, headers=headers, verify=False)
		      result = req.content
		      log_http_session(req, headers, 'GET', '', 1)
		  except Exception as err:
		      write2file(log_File, 'processHTML ERROR: Could not acquire playlist: ' + str(err), 'a', 0, 1)
		      xbmcgui.Dialog().ok('Error', 'Could not acquire playlist:'  + str(err))

		  return link


## Start player
def parseInput(url):
    global result
    result = None
    item = None

    logMyVars()
    write2file(log_File, 'parseInput received URL: ' + url, 'a', 0, 0)
    link = processHTML(url)

    ## Build ListItem
    if result is not None:
      try:
	item = xbmcgui.ListItem(path=link, iconImage=addon_thumb, thumbnailImage=nowPlayingThumb)
	itemInfo = {
	  'type': 'Video',
	  'genre': 'Live Stream',
	  'title': nowPlayingTitle,
	  'playcount': '0'
	}
	item.setInfo('video', itemInfo)
	write2file(log_File, 'parseInput link ' + str(link) , 'a', 0, 0)

      except:
	write2file(log_File, 'parseInput ERROR: Could not access media', 'a', 0, 1)
	xbmcgui.Dialog().ok('Error', 'Could not access media')

    ################### Step 5 #########################
    ## Play stream
    if item is not None and result is not None:
      xbmcplugin.setContent(int(sys.argv[1]), 'movies')
      xbmc.Player().play(link, item)
      write2file(log_File, "xbmc.Player().play(" + link + "," + str(item) + ")", 'a', 0, 1)
      if osdInfo_Enabled == "true":
	xbmc.executebuiltin("Notification(" + nowPlayingTitle + ", " + nowPlayingInfo + ")")


####################################################
## Debug
def write2file(myFile, text, append, header, footer):
    ## append: w = write, a = append
    if debug_Enabled == "true":
      try:
	  file = open(myFile, append)
	  if header == 1:
	    file.write('-------------------------------------------- ' + '\n')
	  file.write(text)
	  if footer == 1:
	    file.write('\n' + '-------------------------------------------- ')
	  file.write('\n')
	  file.close()
      except IOError:
	xbmcgui.Dialog().ok('Error', 'Could not write to logfile')


## Debug
def log_http_session(session, header, method, post_data, echo):
  write2file(log_File, 'processHTML method: ' + method, 'a', 0, 0)
  write2file(log_File, 'processHTML url ' + str(session.url), 'a', 0, 0)
  write2file(log_File, 'processHTML send headers: ' + str(header), 'a', 0, 0)
  if method == 'POST':
    write2file(log_File, 'processHTML post_data: ' + str(post_data), 'a', 0, 0)
  write2file(log_File, 'processHTML status_code: ' + str(session.status_code), 'a', 0, 0)
  write2file(log_File, 'processHTML received headers: ' + str(session.headers), 'a', 0, 0)
  write2file(log_File, 'processHTML received cookies: ' + str(session.cookies.get_dict()), 'a', 0, 0)
  for cookie in (session.cookies):
    write2file(log_File, 'processHTML cookie: ' + str(cookie.__dict__), 'a', 0, 0)
  write2file(log_File, '\n', 'a', 0, 0)
  if echo:
    write2file(log_File, 'processHTML received data: ---------- \n' + str(session.content), 'a', 0, 0)


## Blabla & cleanup
def logMyVars():
  if debug_Enabled == "true":
    write2file(log_File, "osdInfo_Enabled: " + str(osdInfo_Enabled) + "\nuserAgent: " + userAgent + "\nLogin_User: " + str(login_User), 'w', 1, 1)
    write2file(log_File, "cfg_dir: " + str(cfg_dir), 'w', 1, 1)
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
      if os.path.isfile(html_f_5):
	os.remove(html_f_5)
    except:
      xbmcgui.Dialog().ok('Error', 'Could not clean logs')

####################################################
#### RUN Addon ###
params = getParams()
url = None
nowPlayingThumb = None
nowPlayingTitle = None
nowPlayingInfo = None
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
