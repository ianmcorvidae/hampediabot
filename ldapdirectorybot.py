# ldapdirectorybot.py : copyright 2008 Ian McEwen (ianmcorvidae@ornia.hampshire.edu)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ldap
import wikipedia
import re
from urllib import urlencode
import urllib2
import cookielib
from BeautifulSoup import BeautifulSoup

def ldap_start():
	server = "ldap.hampshire.edu"
	who = ""
	cred = ""
	try:
		l = ldap.open(server)
		l.simple_bind_s(who, cred)
		print "Successfully bound to server.\n"
		print "Searching..\n"
		ldap_dict = create_ldap_dictionary(l)
		#for name, entry in ldap_dict.iteritems():
		#	print name, " :: ", entry
		for name, entry in create_namepages_dictionary(ldap_dict).iteritems():
			print name, " :: ", entry
		#for name, entry in create_uidpages_dictionary(ldap_dict).iteritems():
		#	wikipedia.output(name + " :: " + entry)

	except ldap.LDAPError, error_message:
		print "Couldn't connect. %s " % error_message

def create_ldap_dictionary(l, dictionary_data={}):
	base = "dc=hampshire,dc=edu"
	scope = ldap.SCOPE_SUBTREE
	filter = '(|(gidNumber=200)(gidNumber=300)(gidNumber=220)(gidNumber=250))'
	retrieve_attributes = None
	count = 0
	result_set = []
	timeout = 0

	try:
		result_id = l.search(base, scope, filter, retrieve_attributes)
		while l:
			result_type, result_data = l.result(result_id, timeout)
			if (result_data == []):
				break
			else:
				if result_type == ldap.RES_SEARCH_ENTRY:
					result_set.append(result_data)
		if len(result_set) == 0:
			print "No Results."
			return
		for i in range(len(result_set)):
			for entry in result_set[i]:
				try:
					try: 
						name = entry[1]['givenName'][0] + " " + entry[1]['sn'][0]
					except:
						pass
					try: 
						uid = entry[1]['uid'][0].lower()
					except:
						pass
					try: 
						gid = entry[1]['gidNumber'][0]
						type = {'200': 'student', '300': 'faculty', '220': 'alumni', '250': 'staff'}[gid]
					except:
						pass

					try:
						dictionary_data[uid]
						dictionary_data[uid]['uid'] = uid
					except KeyError:
						dictionary_data[uid] = {'uid': uid}

					dictionary_data[uid]['ldap-name'] = name
					
					dictionary_data[uid]['ldap-gid'] = gid

					dictionary_data[uid]['ldap-type'] = type
				except:
					pass
	except ldap.LDAPError, error_message:
		print error_message

	return dictionary_data

def create_hampedia_dictionary(dictionary_data):
	for uid, data in dictionary_data.iteritems():
		mysite = wikipedia.getSite()
		pagedata = ''
		pagetitle = "User:" + uid
		page = wikipedia.Page(mysite, pagetitle)
		try:
			pagedata = page.get()
		except wikipedia.IsRedirectPage, redirecterror:
			redirect = wikipedia.Page(mysite, str(redirecterror))
			try:
				pagedata = redirect.get()
			except: continue
		except wikipedia.NoPage:
			continue

		typeregex = re.compile("{(?P<type>[a-z]+)box", re.IGNORECASE)
		nameregex = re.compile("\n\|name=(?P<name>[^\n]+)\n")
		extregex = re.compile("\n\|ext=(?P<ext>[^\n]+)\n")
		neighborhoodregex = re.compile("\n\|neighborhood=(?P<neighborhood>[^\n])\n")
		yearregex = re.compile("\n\|year=(?P<year>[^\n])\n")
		divisionregex = re.compile("\n\|division=(?P<division>[^\n])\n")
		concentrationregex = re.compile("\n\|concentration=(?P<concentration>[^\n])\n")
		facultyregex = re.compile("\n\|faculty=(?P<faculty>[^\n])\n")
		schoolregex = re.compile("\n\|school=(?P<school>[^\n])\n")
		officeregex = re.compile("\n\|office=(?P<office>[^\n])\n")
		ohoursregex = re.compile("\n\|ohours=(?P<ohours>[^\n])\n")
		hpageregex = re.compile("\n\|hpage=(?P<hpage>[^\n])\n")
		positionregex = re.compile("\n\|position=(?P<position>[^\n])\n")
		almaregex = re.compile("\n\|alma=(?P<alma>[^\n])\n")
		gradyearregex = re.compile("\n\|gradyear=(?P<gradyear>[^\n])\n")
		affiliationregex = re.compile("\n\|affiliation=(?P<affiliation>[^\n])\n")

		try:
			dictionary_data[uid]['hampedia-type'] = match_regex(typeregex, pagedata, 'type').lower()
		except:
			dictionary_data[uid]['hampedia-type'] = ''
		dictionary_data[uid]['hampedia-name'] = match_regex(nameregex, pagedata, 'name')
		dictionary_data[uid]['hampedia-ext'] =	match_regex(extregex, pagedata, 'ext')
		dictionary_data[uid]['hampedia-neighborhood'] = match_regex(neighborhoodregex, pagedata, 'neighborhood')
		dictionary_data[uid]['hampedia-year'] = match_regex(yearregex, pagedata, 'year')
		dictionary_data[uid]['hampedia-division'] = match_regex(divisionregex, pagedata, 'division')
		dictionary_data[uid]['hampedia-concentration'] = match_regex(concentrationregex, pagedata, 'concentration')
		dictionary_data[uid]['hampedia-faculty'] = match_regex(facultyregex, pagedata, 'faculty')
		dictionary_data[uid]['hampedia-school'] = match_regex(schoolregex, pagedata, 'school')
		dictionary_data[uid]['hampedia-office'] = match_regex(officeregex, pagedata, 'office')
		dictionary_data[uid]['hampedia-ohours'] = match_regex(ohoursregex, pagedata, 'ohours')
		dictionary_data[uid]['hampedia-hpage'] = match_regex(hpageregex, pagedata, 'hpage')
		dictionary_data[uid]['hampedia-position'] = match_regex(positionregex, pagedata, 'position')
		dictionary_data[uid]['hampedia-alma'] = match_regex(almaregex, pagedata, 'alma')
		dictionary_data[uid]['hampedia-gradyear'] = match_regex(gradyearregex, pagedata, 'gradyear')
		dictionary_data[uid]['hampedia-affiliation'] = match_regex(affiliationregex, pagedata, 'affiliation')

		
	return dictionary_data

def match_regex(regex, data, group):
	try:
		dreturn = regex.search(data).group(group)
		return dreturn
	except:
		pass

def create_uidpages_dictionary(final_dictionary_data, uidpages={}):
	for uid, data in final_dictionary_data.iteritems():
		uidpages[uid] = "#REDIRECT [[%s]]" % data['name']

	return uidpages

def create_namepages_dictionary(final_dictionary_data, namepages = {}):
	for uid, data in final_dictionary_data.iteritems():
		try:
			name = data['name']
		except:
			continue

		try:
			gid = data['gid']
		except:
			gid = ''
		
		try:
			type = data['type']
		except:
			type = ''
		
		if type == 'Student':
			namepages[name] = """{{studentbox
			|name=%s
			|caption=Hampshire Student
			|image=hampedia_logo_big.jpg
			|email=<email>%s@hampshire.edu</email>
			|ext=
			|neighborhood=
			|year=
			|division=
			|concentration=
			|faculty=
			|interest=
			|school=
			}}

			[[username::user:%s| ]]
			""" % (name, uid, uid)
		elif type == 'Faculty':
			namepages[name] = """{{facultyBox
			|name=%s
			|image=hampedia_logo_big.jpg
			|caption=Hampshire Faculty
			|email=<email>%s@hampshire.edu</email>
			|extension=
			|office=
			|ohours=
			|hpage=
			|position=
			|school=
			|alma=
			}}

			[[username::user:%s| ]]
			""" % (name, uid, uid)
		elif type == 'Alumni':
			namepages[name] = """{{alumnibox
			|name=%s
			|caption=
			|image=
			|email=<email>%s@hampshire.edu</email>
			|neighborhood=
			|year=
			|gradyear=
			|concentration=
			|faculty=
			|interest=
			|school=
			}}

			[[username::user:%s| ]]
			""" % (name, uid, uid)
		elif type == 'Staff':
			namepages[name] = """{{StaffBox
			|name=%s
			|image=hampedia_logo_big.jpg
			|caption=Hampshire Staffperson
			|email=<email>%s@hampshire.edu</email>
			|extension=
			|office=
			|position=
			|affiliation=
			}}
			
			[[username::user:%s| ]]
			""" % (name, uid, uid)
		else:
			print "Failed uid %s" % uid
	return namepages

def create_namepages(namepages):
	for title, contents in namepages.iteritems():
		mysite = wikipedia.getSite()
		page = wikipedia.Page(mysite, title)
		if page.exists():
			wikipedia.output(u"Page %s already exists, not adding!" % title)
		else:
			create_wppage(title, contents, page)

def create_uidpages(uidpages):
	for title, contents in uidpages.iteritems():
		mysite = wikipedia.getSite()
		userpagetitle = "User:" + title
		userpage = wikipedia.Page(mysite, userpagetitle)
		page = wikipedia.Page(mysite, title)
		if userpage.exists():
			wikipedia.output(u"Page %s already exists, not adding!" % userpagetitle)
		else:
			create_wppage(userpagetitle, contents, userpage)
		if page.exists():
			wikipedia.output(u"Page %s already exists, not adding!" % title)
		else:
			create_wppage(title, contents, page)

def create_wppage(title, contents, page):
	try:
		page.put(contents, "*** auto-added by ldap-directory-bot.py ***", True)
		wikipedia.output(u"Added page %s" % title)
	except wikipedia.LockedPage:
		wikipedia.output(u"Page %s is locked; skipping." % title)
	except wikipedia.EditConflict:
		wikipedia.output(u'Skipping %s because of edit conflict' % title)
	except wikipedia.SpamfilterError, error:
		wikipedia.output(u'Cannot change %s because of spam blacklist entry %s' % (title, error.url))

if __name__=='__main__':
	ldap_start()
