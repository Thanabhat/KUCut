from distutils.core import setup
setup(name='kucut',
      version='1.4.3b2',
      scripts=['scripts/kucut'],
      description='Word segmentation tool from Kasetsart University',
      author='Sutee Sudprasert',
      author_email='sutee.s@gmail.com',
      url='http://naist.cpe.ku.ac.th/',
      packages=['kucut', 'kucut/AIMA'],
      package_data={'kucut': ['corpus.db', 'dict/*.txt']})
