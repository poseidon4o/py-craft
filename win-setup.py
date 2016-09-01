import os, sys
import urllib.request as dl
import zipfile
import subprocess
import time

DO_PROXY = False
if len(sys.argv) == 2:
	DO_PROXY = sys.argv[1] == 'proxy'
	print("Using proxy")

SDL_RUNTIME = "https://www.libsdl.org/release/SDL2-2.0.4-win32-x86.zip"
SDL_IMAGE_RUNTIME = "https://www.libsdl.org/projects/SDL_image/release/SDL2_image-2.0.1-win32-x86.zip"
SDL_TTF = "https://www.libsdl.org/projects/SDL_ttf/release/SDL2_ttf-2.0.14-win32-x86.zip"
PY_SDL = 'https://bitbucket.org/marcusva/py-sdl2/downloads/PySDL2-0.9.4.zip'

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
SETUP_DIR = os.path.join(SCRIPT_DIR, 'build')
RUNTIME_DIR = os.path.join(SETUP_DIR, "runtime")
PY_SDL_DIR = os.path.join(SETUP_DIR, "pysdl2")
TMP_DIR = os.path.join(SETUP_DIR, "tmp")

print("Creating [{}] for working dir.".format(SETUP_DIR))
if not os.path.exists(SETUP_DIR):
	os.makedirs(SETUP_DIR)

print("Creating [{}] for tmp dir.".format(TMP_DIR))
if not os.path.exists(TMP_DIR):
	os.makedirs(TMP_DIR)

print("Creating [{}] for runtime dir.".format(RUNTIME_DIR))
if not os.path.exists(RUNTIME_DIR):
	os.makedirs(RUNTIME_DIR)

print("Creating [{}] for pysdl2 dir.".format(PY_SDL_DIR))
if not os.path.exists(PY_SDL_DIR):
	os.makedirs(PY_SDL_DIR)

os.environ['PYSDL2_DLL_PATH'] = RUNTIME_DIR
os.environ['PATH'] = RUNTIME_DIR + ";" + os.environ['PATH']
os.environ['PYTHON'] = sys.executable

last = time.time()
def download(url, name):
	cwd = os.getcwd()
	os.chdir(TMP_DIR)
	name = os.path.join(TMP_DIR, name)
	proxies = {
		'http': 'http://10.0.0.1:1234',
		'https': 'https://10.0.0.1:1234',
		'ftp': 'ftp://10.0.0.1:1234',
		'socks': 'ftp://10.0.0.1:1080',
	}
	if DO_PROXY:
		proxy_handler = dl.ProxyHandler(proxies)
	else:
		proxy_handler = dl.ProxyHandler()
	opener = dl.build_opener(proxy_handler)
	dl.install_opener(opener)
	print("Downloading [{}] -> [{}]...".format(url, name))

	def rep(got, block_sz, total_sz):
		global last
		if time.time() - last > 1:
			last = time.time()
			got_pc = ((got * block_sz) / total_sz) * 100
			print("{}% ".format(int(got_pc)))
	path, headers = dl.urlretrieve(url, name, reporthook=rep)
	print("Downloaded to [{}]".format(path))
	os.chdir(cwd)
	return os.path.join(TMP_DIR, path)

def extract(zip_path, dest):
	print("Extracting [{}] to [{}]".format(zip_path, dest))
	fh = open(zip_path, 'rb')
	z = zipfile.ZipFile(fh)
	for name in z.namelist():
		z.extract(name, dest)
	fh.close()


def run_cmd(cmd, wd=None):
	print(cmd)
	cwd = os.getcwd()
	if not wd:
		wd = os.path.join(PY_SDL_DIR, 'PySDL2-0.9.4')
	os.chdir(wd)

	res = "None"
	code = 0
	if hasattr(subprocess, "check_output"):
		try:
			res = subprocess.check_output(cmd)
		except subprocess.CalledProcessError as e:
			code = e.returncode
			res = e.output
	else:
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		res = proc.communicate()[0]
		code = proc.returncode
	res = res.decode().strip(" \n\r\t")

	os.chdir(cwd)

	print("OUTPUT:\n{}\n\nCODE:{}".format(res, code))



if __name__ == '__main__':
	if os.name != 'nt':
		print("Not on windows, bye bye")
		sys.exit(1)

	try:
		import sdl2
	except:
		print("sdl2 cant't be imported proceeding")
	else:
		print("sdl2 already installed - running game")
		run_cmd([sys.executable, 'game.py'], SCRIPT_DIR)
		sys.exit(1)

	sdl_zip = download(SDL_RUNTIME, "sdl2.zip")
	sdl_image_zip = download(SDL_IMAGE_RUNTIME, "sdl2_image.zip")
	py_sdl_zip = download(PY_SDL, "py_sdl.zip")
	sdl_ttf_zip = download(SDL_TTF, "sdl_ttf.zip")

	extract(sdl_zip, RUNTIME_DIR)
	extract(sdl_image_zip, RUNTIME_DIR)
	extract(sdl_ttf_zip, RUNTIME_DIR)
	extract(py_sdl_zip, PY_SDL_DIR)

	run_cmd(['make.bat'])

	site_packs = os.path.join(os.path.dirname(sys.executable))
	run_cmd([sys.executable, 'setup.py', 'install', '--prefix={}'.format(site_packs)])
	print("sdl2 installed - running game")
	run_cmd([sys.executable, 'game.py'], SCRIPT_DIR)