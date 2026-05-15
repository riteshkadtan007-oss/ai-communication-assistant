[app]

# (str) Title of your application
title = AI Keyboard

# (str) Package name
package.name = aikeyboard

# (str) Package domain (needed for android/ios packaging)
package.domain = com.riteshkadtan

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,txt,md

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec

# (list) List of directory to exclude
source.exclude_dirs = tests, bin, venv, .venv, __pycache__, .git, .idea, .vscode

# (str) Application versioning (method 1)
version = 0.1.0

# (list) Application requirements
# Keep this minimal — p4a auto-pulls the right transitive deps for `requests`.
# Adding too many explicit deps causes "no recipe found" failures.
requirements = python3,kivy==2.3.0,requests,openssl

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
#requirements.source.kivy = ../../kivy

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse or landscape-reverse
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
#android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (int) Android NDK API to use. This is the minimum API your app will support.
android.ndk_api = 21

# (str) Pin NDK to a version known-stable with python-for-android.
# Auto-downloading the latest NDK (e.g. r28c) often breaks the toolchain.
android.ndk = 25b

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running buildozer.
android.accept_sdk_license = True

# (list) The Android archs to build for.
# Build only arm64-v8a first — covers ~95% of modern Android phones and halves build time.
# Add armeabi-v7a back later if you need to support older devices.
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) python-for-android branch to use.
# Pinned to v2024.01.21 — this release defaults to Python 3.11, which Kivy 2.3.0
# was built and tested against. Master defaults to Python 3.14, which breaks
# Kivy's C extensions (Py_UNICODE removed, _PyLong_AsByteArray signature changed).
p4a.branch = v2024.01.21

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes =

# (str) Bootstrap to use for android builds
# Valid options are: sdl2, webview, service_only, service_library
p4a.bootstrap = sdl2

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin
