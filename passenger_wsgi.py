import sys, os
INTERP = "/home/jgwlibrary/bibtool.wolba.ch/bin/python"
#INTERP is present twice so that the new python interpreter 
#knows the actual executable path 
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

cwd = os.getcwd()
sys.path.append(cwd)
sys.path.append(cwd + '/cfabib')  #You must add your project here

sys.path.insert(0,cwd+'/bibtool.wolba.ch/bin')
sys.path.insert(0,cwd+'/bibtool.wolba.ch/lib/python3.8/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = "cfabib.settings"
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()