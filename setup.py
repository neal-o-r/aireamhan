from distutils.core import setup
setup(
  name = 'aireamhan',
  packages = ['aireamhan'], # this must be the same as the name above
  version = '1.2',
  description = 'Teanga Ríomhchlárúchain as Gaeilge',
  author = 'Neal Ó Riain',
  author_email = 'neal@n-o-r.xyz',
  url = 'https://github.com/neal-o-r/aireamhan', # use the URL to the github repo
  download_url = 'https://github.com/neal-o-r/aireamhan/archive/1.2.tar.gz', 
  keywords = ['Irish', 'language', 'programming language'], 
  classifiers = [],
  scripts=['bin/áireamhán']
)
