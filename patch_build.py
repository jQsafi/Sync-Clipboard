
import os
from buildozer.targets.android import TargetAndroid

# This is a patch to fix Buildozer's hardcoded environment checks on Termux

# Get the real Termux CFLAGS and LDFLAGS
termux_cflags = os.environ.get('CFLAGS', '')
termux_ldflags = os.environ.get('LDFLAGS', '')

# Monkey-patch the get_target_env method
old_get_target_env = TargetAndroid.get_target_env

def new_get_target_env(self, arch):
    env = old_get_target_env(self, arch)
    env['CFLAGS'] = f"{env.get('CFLAGS', '')} {termux_cflags}"
    env['LDFLAGS'] = f"{env.get('LDFLAGS', '')} {termux_ldflags}"
    # Specifically add the include path for zlib and others
    env['CFLAGS'] += f" -I/data/data/com.termux/files/usr/include"
    env['LDFLAGS'] += f" -L/data/data/com.termux/files/usr/lib"
    return env

TargetAndroid.get_target_env = new_get_target_env

print("Buildozer environment patched for Termux.")
