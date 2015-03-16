#! /usr/bin/env python
#coding:utf-8

import tornado.web
import time
import os
from models.entity import User, Article, Type, Page, Contact, Upload, Inform, Limits, Links, Meetinfo
from models.entity import getSession
import hashlib
import json

page_path = os.path.join(os.path.abspath('.'), 'static/page/')
inform_path = os.path.join(os.path.abspath('.'), 'static/inform/')

def nameRewrite(filename):
    file_timestamp = int(time.time())
    name_split = filename.split('.')
    if len(name_split) == 1:
        filename = filename + str(file_timestamp)
    else:
        filename = name_split[0] + str(file_timestamp) + '.' + name_split[1]
    return filename

class StaticData(object):
   def __init__(self):
      self.session = getSession()

class SignValidateBase(tornado.web.RequestHandler):
   def get_current_user(self):
      return self.get_secure_cookie('username')

class Signin(SignValidateBase, StaticData):
   def get(self):
      self.title = 'Sign in'
      self.render('signin.html')

   def post(self):
      StaticData.__init__(self)
      username = self.get_argument('username', default='')
      password = self.get_argument('password', default='')
      md5_psw = hashlib.md5(password).hexdigest()
      user = self.session.query(User).filter(User.username==username).one()
      uname = user.username
      psw = user.password
      if username == uname and md5_psw == psw:
          if user.ucheck == True:
              self.set_secure_cookie('username', username)
              self.redirect('/')
          else:
              self.write('<script language="javascript">alert("对不起，账户需管理员确认后方能生效");self.location="/signin";</script>')
      else:
         self.write('<script language="javascript">alert("用户名或密码错误");self.location="/signin";</script>')

class Signout(SignValidateBase):
   def get(self):
      self.clear_cookie('username')
      self.redirect('/')

class Signup(SignValidateBase, StaticData):
   def get(self):
      self.title = 'Sign Up'
      self.render('signup.html')

   def post(self):
      StaticData.__init__(self)
      username = self.get_argument('username', default='')
      password = self.get_argument('password', default='')
      passvali = self.get_argument('passvali', default='')
      uemail = self.get_argument('email', default='')
      if password == passvali:
          uname = self.session.query(User).filter(User.username==username).first()
          if uname != None:
              self.write('<script language="javascript">alert("用户名已被占用");self.location="/signup";</script>')
          else:
              psw = hashlib.md5(password).hexdigest()
              newuser = User(username,psw,uemail)
              self.session.add(newuser)
              self.session.commit()
              self.set_secure_cookie('username', username)
              self.write('<script language="javascript">alert("注册成功");self.location="/";</script>')
      else:
          self.write('<script language="javascript">alert("密码不匹配");self.location="/signup";</script>')

class AdminHome(SignValidateBase, StaticData):
    @tornado.web.authenticated
    def get(self):
        StaticData.__init__(self)
        self.title = 'Dashboard'
        userlist = self.session.query(User).all()
        articlelist = self.session.query(Article).all()
        pagelist = self.session.query(Page).all()
        typelist = self.session.query(Type).all()
        self.render('admin_overview.html', userlist = userlist, articlelist = articlelist, pagelist = pagelist, typelist = typelist)

class EditPage(SignValidateBase, StaticData):
    @tornado.web.authenticated
    def get(self):
        self.title = 'Dashboard Edit'
        self.render('admin_editpage.html', active2 = 'class="active"')

    def post(self):
        self.title = 'Dashboard Edit'
        StaticData.__init__(self)
        ptitle = self.get_argument('ptitle', default='')
        pcontent = self.get_argument('pcontent', default='')
        page = Page(ptitle, pcontent)
        if 'file' in self.request.files:
            file_dict_list = self.request.files['file']
            for file_dict in file_dict_list:
                filename = nameRewrite(file_dict["filename"]).encode('utf8')
                data = file_dict["body"]
                with open(page_path + filename, 'w') as f:
                    f.write(data)
                    print filename
            page.ppic = page_path + filename
        self.session.add(page)
        self.session.commit()
        self.write('<script language="javascript">alert("提交成功");self.location="/admin/editpage"</script>')

class EditLimits(SignValidateBase, StaticData):
    @tornado.web.authenticated
    def get(self):
        self.title = 'Dashboard Limits'
        StaticData.__init__(self)
        limitlist = self.session.query(Limits).all()
        userlist = self.session.query(User).all()
        self.render('admin_limits.html', userlist = userlist, limitlist = limitlist)

class ChangeChecked(tornado.web.RequestHandler, StaticData):
    def post(self):
        uid = self.get_argument('uid')
        uchecked = self.get_argument('uchecked')
        print uid, uchecked, type(uchecked)
        if uchecked == 'false':
            uchecked = False
        else:
            uchecked = True
        user = self.session.query(User).filter(User.uid == uid).first()
        print user.username
        user.ucheck = not uchecked
        print user.ucheck
        self.session.commit()

class ChangeLimit(tornado.web.RequestHandler, StaticData):
    def post(self):
        uid = self.get_argument('uid')
        luid = self.get_argument('luid')
        user = self.session.query(User).filter(User.uid == uid).first()
        user.luid = luid
        self.session.commit()

class ListReports(SignValidateBase, StaticData):
    @tornado.web.authenticated
    def get(self):
        self.title = 'Dashboard Reports'
        StaticData.__init__(self)
        contactlist = self.session.query(Contact).all()
        self.render('admin_reports.html', contactlist = contactlist)

class SlideOption(SignValidateBase, StaticData):
    @tornado.web.authenticated
    def get(self):
        self.title = 'Slide Option'
        self.render("admin_slide.html")

    def post(self):
        self.title = 'Slide Option'
        ititle = self.get_argument('ititle', default='')
        iabstract = self.get_argument('iabstract', default='')
        iurl = self.get_argument('iurl', default='')
        ibtnview = self.get_argument('ibtnview', default='View Detail')
        inform = Inform(ititle, iabstract)
        inform.iurl = iurl
        inform.itynview = ibtnview
        if 'file' in self.request.files:
            file_dict_list = self.request.files['file']
            for file_dict in file_dict_list:
                filename = nameRewrite(file_dict["filename"]).encode('utf8')
                data = file_dict["body"]
                with open(inform_path + filename, 'w') as f:
                    f.write(data)
                    print filename
            inform.ipic = '/static/inform/' + filename
        self.session.add(inform)
        self.session.commit()
        self.write('<script language="javascript">alert("提交成功");self.location="/admin";</script>')

class LinkOption(SignValidateBase, StaticData):
    @tornado.web.authenticated
    def get(self):
        self.title = 'Link Option'
        self.render('admin_link.html')

    def post(self):
        self.title = 'Link Option'
        lkname = self.get_argument('lkname', default='')
        lkurl = self.get_argument('lkurl', default='')
        lkdescribe = self.get_argument('lkdescribe', describe='')
        link = Link(lkname, lkurl)
        link.lkdescribe = lkdescribe
        self.session.add(link)
        self.session.commit()
        self.write('<script language="javascript">alert("提交成功");self.location="/admin";</script>')

class MeetinfoOption(SignValidateBase, StaticData):
    @tornado.web.authenticated
    def get(self):
        self.title = 'Meetinfo Option'
        self.render('admin_meetinfo.html')

    def post(self):
        self.title = 'Meetinfo Option'
        mtitle = self.get_argument('mtitle', default='')
        mcontent = self.get_argument('mcontent', default='')
        meetinfo = Meetinfo(mtitle, mcontent)
        self.session.add(meetinfo)
        self.session.commit()
        self.write('<script language="javascript">alert("提交成功");self.location="/admin";</script>')


class AdminStatistic():
    pass