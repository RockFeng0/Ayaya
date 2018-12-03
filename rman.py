#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman,  v1.0 2018年11月23日
    FROM:   2018年11月23日
********************************************************************
======================================================================

Provide a function for the automation test

'''

from rman import app


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)