import logging
import optparse

import gettext
from gettext import gettext as _
gettext.textdomain('duckduckgo-lens')

from singlet.lens import SingleScopeLens, IconViewCategory, ListViewCategory

from duckduckgo_lens import duckduckgo_lensconfig

import urllib2, json

from urlparse import urlparse

class DuckduckgoLens(SingleScopeLens):

	class Meta:
		name = 'duckduckgo'
		description = 'DuckDuckGo Lens'
		search_hint = 'Search DuckDuckGo'
		icon = 'duckduckgo.svg'
		search_on_blank = False
		category_order = ["results_category", "related_searches", "related_topics"]

	# TODO: Add your categories
	related_topics = ListViewCategory("Related Topics", 'dialog-information-symbolic')	
	related_searches = ListViewCategory("Related Searches", 'dialog-information-symbolic')
	results_category = ListViewCategory("Results", 'dialog-information-symbolic')

	ddg_url = "http://api.duckduckgo.com/"

	def ddg_query(self, search):
		search = search.replace(" ", "+")
		search_url = "?q=%s&format=json&no_redirect=1" % search
		url = self.ddg_url + search_url
		results = json.loads(urllib2.urlopen(url).read())

		return results

	def search(self, search, results):

		self.ddg_query(search)

		search_results = self.ddg_query(search)
		
		if search_results["Redirect"]:
			parse = urlparse(search_results["Redirect"])
			host = parse.netloc
			results.append(
				search_results["Redirect"],
				'applications-webbrowsers',
				self.results_category,
				"text/html",
				"Search " + host + " for:",
				search,
				search_results["Redirect"]
			)
			return
			
		for related in search_results['RelatedTopics']:
			if "Result" in related:
				if related["Text"] == 'Category Category':
					results.append(
						related['FirstURL'],
						'/usr/local/share/unity/lenses/duckduckgo/duckduckgo.svg',
						self.related_searches,
						"text/html",
						search.title(),
						"Category",
						related['FirstURL'])
				else:
					results.append(
						related['FirstURL'],
						'/usr/local/share/unity/lenses/duckduckgo/duckduckgo.svg',
						 self.related_searches,
						 "text/html",
						 "Search for:",
						 related["Text"],
						 related['FirstURL'])
			elif "Topics" in related:
				name = related["Name"]
				for result in related["Topics"]:
					results.append(
						result['FirstURL'],
						'/usr/local/share/unity/lenses/duckduckgo/duckduckgo.svg',
						self.related_topics,
						"text/html",
						name,
						result["Text"],
						result["FirstURL"]
					)

		if search_results["AbstractURL"]:
			results.append(
				search_results["AbstractURL"],
				'applications-webbrowsers',
				self.results_category,
				"text/html",
				search_results["AbstractSource"],
				search_results["AbstractText"],
				search_results["AbstractURL"]
			)

		if search_results["DefinitionURL"]:
			results.append(
				search_results["DefinitionURL"],
				'applications-webbrowsers',
				self.results_category,
				"text/html",
				search_results["DefinitionSource"],
				search_results["Definition"],
				search_results["AbstractURL"]
			)


		for result in search_results['Results']:
			results.append(result['FirstURL'],
						 'applications-webbrowsers',
						 self.results_category,
						 "text/html",
						 result['Text'],
						 search_results['AbstractText'],
						 result['FirstURL'])
		
