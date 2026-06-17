#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# nebula-cert-maker, version 2

# Released under the terms of the GNU General Public Licence, version 2
# <http://www.gnu.org/licenses/>

# Revision history:
#   1 - Initial release
#   2 - Uses shared libraries with NebulaCertManager.py

__license__ = 'GPL v2'
__version__ = '2'

import shutil
import sys

library_path = "../lib"
if library_path not in sys.path:
    sys.path.insert(0, library_path)

import nebula_cert_executor as executor
import nebula_cert_core as ncm_core

DEST_DIR = "./deploy"

# total arguments
n = len(sys.argv)
if (n > 1 ):
    file_path = sys.argv[1]
    if (n > 2):
         DEST_DIR = sys.argv[2]
else:
    print('Usage: "nebula-cert-maker.py host_list.yaml [destination/directory]"')  
    exit()

core = ncm_core.Core()
nebula_cert_cmd = shutil.which("nebula-cert")
executor = executor.NebulaCertExecutor(nebula_cert_cmd)
executor.set_destination_dir(DEST_DIR)

try:
    core.open_config(file_path)
    executor.generate_certs(
        core.cert_domain,
        core.cert_duration,
        core.lighthouses,
        core.hosts)
    print(f"SUCCESS! The certificates are located here:\n{DEST_DIR}")
except Exception as e:
    print(f"{e}")

