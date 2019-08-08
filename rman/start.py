#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.start

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.start,  v1.0 2019年4月4日
    FROM:   2019年4月4日
********************************************************************
======================================================================

Provide a function for the automation test

'''

import sys
sys.path.append('/opt/deploy/rock4tools/rtsf-manager')

from rman.app import APP

if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=5000, debug = True)
        