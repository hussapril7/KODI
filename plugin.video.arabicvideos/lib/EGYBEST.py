# -*- coding: utf-8 -*-
from LIBRARY import *

website0a = 'https://egy.best'
headers = { 'User-Agent' : '' }
script_name = 'EGYBEST'

def MAIN(mode,url,page):
	if   mode==120: MAIN_MENU()
	elif mode==121: FILTERS_MENU(url)
	elif mode==122: TITLES(url,page)
	elif mode==123: PLAY(url)
	elif mode==124: SEARCH()
	elif mode==125: GET_USERNAME_PASSWORD()
	elif mode==126: GET_LOGIN_TOKEN()
	return

def MAIN_MENU():
	addDir('اضغط هنا لاضافة اسم دخول وكلمة السر','',125)
	addDir('بحث في الموقع','',124)
	html = openURL(website0a,'',headers,'','EGYBEST-MAIN_MENU-1st')
	html_blocks=re.findall('id="menu"(.*?)mainLoad',html,re.DOTALL)
	block = html_blocks[0]
	items=re.findall('a><a href="(.*?)".*?></i>(.*?)<',block,re.DOTALL)
	for url,title in reversed(items):
		addDir(title,url,121)
	xbmcplugin.endOfDirectory(addon_handle)
	return

def FILTERS_MENU(link):
	filter = link.split('/')[-1]
	#xbmcgui.Dialog().ok(str(link), str(filter))
	if '/trending/' not in link:
		addDir('اظهار قائمة الفيديو التي تم اختيارها',link,122,'',1)
		addDir('[[ ' + filter + ' ]]',link,122,'',1)
		addDir('===========================',link,9999)
	html = openURL(link,'',headers,'','EGYBEST-FILTERS_MENU-1st')
	html_blocks=re.findall('mainLoad(.*?)</div></div>',html,re.DOTALL)
	if html_blocks:
		block = html_blocks[0]
		items=re.findall('href="(.*?)".*?</i> (.*?)<',block,re.DOTALL)
		for url,title in items:
			if '/movies/' in url and 'فلام' not in title: title = 'افلام ' + title
			elif '/tv/' in url and 'مسلسل' not in title: title = 'مسلسلات ' + title
			if '/trending/' in url:
				title = 'الاكثر مشاهدة ' + title
				addDir(title,url,122,'',1)
			else:
				newfilter = url.split('/')[-1]
				if filter!='': newfilter = '-' + newfilter
				url = link + newfilter
				addDir(title,url,121)
	html_blocks=re.findall('sub_nav(.*?)</div></div></div>',html,re.DOTALL)
	if html_blocks:
		block = html_blocks[0]
		items=re.findall('href="(.*?)" >(.*?)<',block,re.DOTALL)
		for url,title in items:
			if '- الكل -' in title: continue
			if '/movies/' in url: title = 'افلام ' + title
			elif '/tv/' in url: title = 'مسلسلات ' + title
			addDir(title,url,121)
	xbmcplugin.endOfDirectory(addon_handle)
	return

def TITLES(url,page):
	#xbmcgui.Dialog().ok(str(url), str(page))
	if '/explore/' in url: url2 = url + '&'
	else: url2 = url + '?'
	url2 = url2 + 'output_format=json&output_mode=movies_list&page='+str(page)
	html = openURL(url2,'',headers,'','EGYBEST-TITLES-1st')
	import logging
	logging.warning(html)
	items = re.findall('n<a href=\\\\"(.*?)\\\\".*?src=\\\\"(.*?)\\\\".*?title\\\\">(.*?)<',html,re.DOTALL)
	name = ''
	if '/season/' in url:
		name = xbmc.getInfoLabel( "ListItem.Label" ) + ' - '
	for link,img,title in items:
		if '/series/' in url and '/season\/' not in link: continue
		if '/season/' in url and '/episode\/' not in link: continue
		title = name + escapeUNICODE(title).strip(' ')
		link = link.replace('\/','/')
		img = img.replace('\/','/')
		url2 = website0a + link
		if '/movie/' in url2 or '/episode/' in url2:
			addLink(title,url2,123,img)
		else:
			addDir(title,url2,122,img,1)
	pagingLIST = ['/movies/','/tv/','/explore/','/trending/']
	if any(value in url for value in pagingLIST):
		for n in range(0,1000,100):
			if int(page/100)*100==n:
				for i in range(n,n+100,10):
					if int(page/10)*10==i:
						for j in range(i,i+10,1):
							if not page==j and j!=0:
								addDir('صفحة '+str(j),url,122,icon,j)
					elif i!=0: addDir('صفحة '+str(i),url,122,icon,i)
					else: addDir('صفحة '+str(1),url,122,icon,1)
			elif n!=0: addDir('صفحة '+str(n),url,122,icon,n)
			else: addDir('صفحة '+str(1),url,122,icon,1)
	xbmcplugin.endOfDirectory(addon_handle)
	return

def PLAY(url):
	#xbmcgui.Dialog().ok(url, '')
	headers = { 'User-Agent' : '' }
	html = openURL(url,'',headers,'','EGYBEST-PLAY-1st')
	adultLIST = ['R','TVMA','TV-MA'       ,'PG-18','PG-16']
	rating = re.findall('<td>التصنيف</td>.*?">(.*?)<',html,re.DOTALL)
	if any(value in rating[0] for value in adultLIST):
		xbmcgui.Dialog().notification('الفيديو للكبار فقط','البرنامج لا يعرض هكذا افلام')
		return
	html_blocks = re.findall('tbody(.*?)tbody',html,re.DOTALL)
	if not html_blocks:
		xbmcgui.Dialog().notification('خطأ من الموقع الاصلي','ملف الفيديو غير متوفر')
		return
	block = html_blocks[0]
	items = re.findall('</td> <td>(.*?)<.*?data-call="(.*?)"',block,re.DOTALL)
	qualityLIST = []
	datacallLIST = []
	if len(items)>0:
		for qualtiy,datacall in items:
			qualityLIST.append ('mp4   '+qualtiy)
			datacallLIST.append (datacall)
	watchitem = re.findall('source src=\"\/api\?call=(.*?)"',html,re.DOTALL)
	url = website0a + '/api?call=' + watchitem[0]
	EGUserDef = GET_LOGIN_TOKEN()
	if EGUserDef=='': return
	headers = { 'User-Agent':'Googlebot/2.1 (+http)', 'Referer':'https://egy.best', 'Cookie':'EGUserDef='+EGUserDef }
	import requests
	response = requests.get(url, headers=headers, allow_redirects=False)
	html = response.text
	items = re.findall('#EXT-X-STREAM.*?RESOLUTION=(.*?),.*?\n(.*?)\n',html,re.DOTALL)
	if len(items)>0:
		for qualtiy,url in reversed(items):
			qualityLIST.append ('m3u8   '+qualtiy)
			datacallLIST.append (url)
	selection = xbmcgui.Dialog().select('اختر الفيديو المناسب:', qualityLIST)
	if selection == -1 : return ''
	url = datacallLIST[selection]
	if 'http' not in url:
		datacall = datacallLIST[selection]
		url = website0a + '/api?call=' + datacall
		headers = { 'User-Agent':'Googlebot/2.1 (+http)', 'Referer':'https://egy.best', 'Cookie':'EGUserDef='+EGUserDef }
		response = requests.get(url, headers=headers, allow_redirects=False)
		html = response.text
		items = re.findall('"url":"(.*?)"',html,re.DOTALL)
		url = items[0]
	url = url.replace('\/','/')
	PLAY_VIDEO(url,script_name,'yes')
	return

def SEARCH():
	search = KEYBOARD()
	if search == '': return
	new_search = search.replace(' ','+')
	url = website0a + '/explore/?q=' + new_search
	TITLES(url,1)
	return

def GET_USERNAME_PASSWORD():
	text = 'هذا الموقع يحتاج اسم دخول وكلمة السر لكي تستطيع تشغيل ملفات الفيديو. للحصول عليهم قم بفتح حساب مجاني من الموقع الاصلي'
	xbmcgui.Dialog().ok('الموقع الاصلي  http://egy.best',text)
	xbmc.executebuiltin('Addon.OpenSettings(%s)' % addon_id)
	return

def GET_LOGIN_TOKEN():
	import requests
	#url = 'https://ssl.egexa.com/logout/'
	#headers = { 'Cookie': 'PHPSESSID='+PHPSESSID }
	#querystring = { 'domain':'egy.best' }
	#response = requests.get(url, params=querystring, allow_redirects=False)
	#response = requests.get(url, allow_redirects=False)
	#url = 'https://ssl.egexa.com/login/'
	#response = requests.get(url, allow_redirects=False)
	#cookies = response.cookies.get_dict()
	#PHPSESSID = cookies['PHPSESSID']
	PHPSESSID = dummyClientID()
	url = 'https://login.egy.best/setlocalcookie.php'
	querystring = {"domain":"egy.best","LOGIN_SID":PHPSESSID,"url":"https://egy.best"}
	headers = { 'Cookie': 'PHPSESSID='+PHPSESSID }
	response = requests.get(url, headers=headers, params=querystring, allow_redirects=False)
	cookies = response.cookies.get_dict()
	try:
		EGUserDef = cookies['EGUserDef']
		#xbmcgui.Dialog().ok('You already logged in','')
	except:
		import xbmcaddon
		settings = xbmcaddon.Addon(id='plugin.video.arabicvideos')
		username = settings.getSetting('egybest.user')
		password = settings.getSetting('egybest.pass')
		url = 'https://ssl.egexa.com/login/'
		headers = { 'Content-Type': 'application/x-www-form-urlencoded' , 'Cookie': 'PHPSESSID='+PHPSESSID }
		payload = 'LOGIN_SID='+PHPSESSID+'&do=login&login=login&password='+password+'&username='+username
		response = requests.post(url, data=payload, headers=headers, allow_redirects=False)
		cookies = response.cookies.get_dict()
		try:
			EGUserDef = cookies['EGUserDef']
			#xbmcgui.Dialog().ok('success','logged in')
		except:
			xbmcgui.Dialog().ok('خطأ في اسم الدخول او كلمة السر','يجب عليك اصلاح هذا الخطأ لكي تتمكن من تشغيل الفيديو بصورة صحيحة')
			EGUserDef = ''
	return EGUserDef



