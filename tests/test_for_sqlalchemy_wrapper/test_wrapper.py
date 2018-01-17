#!/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2018Sogou.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File Name: test_wrapper.py
Author: Tang Bo <tangbo@sogou-inc.com>
Create Time: 2018/01/16 16:41:00
Brief:      
"""

import sys
import os
import logging
import time
import json
import datetime
reload(sys)
sys.setdefaultencoding('utf-8')

from third_party.sqlalchemy_wrapper.sqlalchemy_wrapper import SQLAlchemy
def create_ban_user_model(db):

    class BanUser(db.Model): #TODO
        __tablename__ = "user_ban"
        user_id = db.Column(db.BigInteger, nullable=False, primary_key = True) #用户qq号
        uid = db.Column(db.BigInteger,nullable=False) #用户uid
        orig = db.Column(db.Integer, nullable=False)
        stat = db.Column(db.Integer, nullable = False) #1：解封
        type = db.Column(db.Integer, nullable = False) #0：社区功能，1：登陆
        reason_type = db.Column(db.String(20), nullable = True) #0：社区功能，1：登陆
        reason_desc = db.Column(db.String(255), nullable = True)
        operator = db.Column(db.BigInteger, nullable = False)
        begin_time = db.Column(db.TIMESTAMP, nullable = False, default = datetime.datetime.utcnow)
        end_time = db.Column(db.TIMESTAMP, nullable = False, default = datetime.datetime.utcnow)
        create_time = db.Column(db.TIMESTAMP, nullable = False, default = datetime.datetime.utcnow)
        modify_time = db.Column(db.TIMESTAMP, nullable = False, default = datetime.datetime.utcnow)

        def __init__(self, user_id, uid, orig = 0, stat = 0, type = 0, reason_type = "0", reason_desc = "", operator = 393120777):
            self.user_id = user_id
            self.uid = uid
            self.orig = orig
            self.stat = stat
            self.type = type
            self.reason_type = reason_type
            self.reason_desc = reason_desc
            self.operator = operator

    return BanUser

def main():
    uri = "mysql://wenwen:wenwen@front@10.134.34.69:17706/mainsite_audit?charset=utf8"
    db1 = SQLAlchemy(uri)
    todo = create_ban_user_model(db1)
    db1.create_all()
    print db1.query(todo).count()    

if __name__ == "__main__":
    sys.exit(main())
