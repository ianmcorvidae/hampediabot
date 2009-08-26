
import ldap
import wikipedia

def main():
	server = "localhost"
	port = 2000
	who = ""
	cred = ""
	keyword = "210"
	try:
		l = ldap.open(server,port)
		l.simple_bind_s(who, cred)
		print "Successfully bound to server.\n"
		print "Searching..\n"
		my_search(l, keyword)
	except ldap.LDAPError, error_message:
		print "Couldn't connect. %s " % error_message

def my_search(l, keyword):
	base = "dc=hampshire,dc=edu"
	scope = ldap.SCOPE_SUBTREE
	filter = '(&(gidNumber=200)(uid=*09))'
	retrieve_attributes = None
	count = 0
	result_set = []
	timeout = 0
	uidpages = {}
	userpages = {}
	namepages = {}
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
						home = entry[1]['homeDirectory'][0]
					except:
						pass
					try: 
						gid = entry[1]['gidNumber'][0]
						type = {'200': 'Student', '300': 'Faculty', '220': 'Alumni', '250': 'Staff'}[gid]
					except:
						pass
					try: 
						members = entry[1]['memberUid']
					except:
						pass
					count = count + 1
					uidpages[uid] = "#REDIRECT [[%s]]" % name

					if type == 'Student':
						namepages[name] = """{{studentbox
						|name=%s
						|caption=Hampshire Student
						|image=hampedia_logo_big.jpg
						|email=%s@hampshire.edu
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
#					elif type == 'Faculty':
#						namepages[name] = """{{facultyBox
#						|name=%s
#						|image=hampedia_logo_big.jpg
#						|caption=Hampshire Faculty
#						|email=%s@hampshire.edu
#						|extension=
#						|office=
#						|ohours=
#						|hpage=
#						|position=
#						|school=
#						|alma=
#						}}
#		
#						[[username::user:%s| ]]
#						""" % (name, uid, uid)
#					if type == 'Alumni':
#						namepages[name] = """{{alumnibox
#						|name=%s
#						|caption=
#						|image=
#						|email=%s@hampshire.edu
#						|neighborhood=
#						|year=
#						|gradyear=
#						|concentration=
#						|faculty=
#						|interest=
#						|school=
#						}}
#
#						[[username::user:%s| ]]
#						""" % (name, uid, uid)
#					elif type == 'Staff':
#						namepages[name] = """{{StaffBox
#						|name=%s
#						|image=hampedia_logo_big.jpg
#						|caption=Hampshire Staffperson
#						|email=%s@hampshire.edu
#						|extension=
#						|office=
#						|position=
#						|affiliation=
#						}}
#			
#						[[username::user:%s| ]]
#						""" % (name, uid, uid)
					else:
						namepages[name] = ""
				except:
					pass

					
		for title, contents in namepages.iteritems():
			mysite = wikipedia.getSite()
			page = wikipedia.Page(mysite, title)
			if page.exists():
				wikipedia.output(u"Page %s already exists, not adding!" % title)
				continue
			else:
				try:
					page.put(contents, "*** auto-added by ldapbot.py ***", True)
					wikipedia.output(u"Added page %s" % title)
				except wikipedia.LockedPage:
					wikipedia.output(u"Page %s is locked; skipping." % title)
				except wikipedia.EditConflict:
					wikipedia.output(u'Skipping %s because of edit conflict' % title)
				except wikipedia.SpamfilterError, error:
					wikipedia.output(u'Cannot change %s because of spam blacklist entry %s' % (title, error.url))
		for title, contents in uidpages.iteritems():
			mysite = wikipedia.getSite()
			userpagetitle = "User:" + title
			userpage = wikipedia.Page(mysite, userpagetitle)
			page = wikipedia.Page(mysite, title)
			try:
				page.put(contents, "*** auto-added by ldapbot.py ***", True)
			except wikipedia.LockedPage:
				wikipedia.output(u"Page %s is locked; skipping." % title)
			except wikipedia.EditConflict:
				wikipedia.output(u'Skipping %s because of edit conflict' % title)
			except wikipedia.SpamfilterError, error:
				wikipedia.output(u'Cannot change %s because of spam blacklist entry %s' % (title, error.url))
		
			try:
				userpage.put(contents, "*** auto-added by ldapbot.py ***", True)
			except wikipedia.LockedPage:
				wikipedia.output(u"Page %s is locked; skipping." % userpagetitle)
			except wikipedia.EditConflict:
				wikipedia.output(u'Skipping %s because of edit conflict' % userpagetitle)
			except wikipedia.SpamfilterError, error:
				wikipedia.output(u'Cannot change %s because of spam blacklist entry %s' % (userpagetitle, error.url))
	except ldap.LDAPError, error_message:
		print error_message

if __name__=='__main__':
	main()
