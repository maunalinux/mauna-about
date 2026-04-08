#!/usr/bin/python3

import sys

from util import ACPIManager
from util import DualBootManager

if len(sys.argv) >= 2:
    cmd = sys.argv[1]

    if cmd == "acpi":
        if ACPIManager.is_acpi_supported():
            sys.exit(0)
        else:
            sys.exit(1)
    elif cmd == "dualboot":
        print(DualBootManager.get_dualboot_oses())
