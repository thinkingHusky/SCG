#! /usr/bin/env python
#coding=utf-8

import time
import os
import tornado.web
import markdown
import random
from models.entity import User, Article, Page, Type, Contact, Inform
from models.entity import getSession
from handlers.admin import SignValidateBase, nameRewrite

#页面通用数据
avatar_path = os.path.join(os.path.abspath('.'), 'static/avatar/')
resume_path = os.path.join(os.path.abspath('.'), 'static/resume/')

class HomeBase(object):
    def __init__(self):
        self.session = getSession()

class homeBase(SignValidateBase):
    def init(self):
        self.session = getSession()
        self.signeduser = SignValidateBase.get_current_user(self)
        if self.signeduser:
            self.user = self.session.query(User).filter(User.username == self.signeduser).first()
            self.signedid = self.user.uid
            self.signavatar = self.user.uavatar
        else:
            self.signedid = None


#用于阅读类界面的渲染
class StaticBase(homeBase):
    def __init__(self):
        homeBase.init(self)
        #所有类型
        self.alltype = self.session.query(Type)
        self.meetinfo = self.session.query(Meetinfo).first()
        self.links = self.session.query(Links).all()
        #归档
        articlelist = self.session.query(Article).order_by(Article.apubtime.desc()).all()
        topyear = articlelist[0].apubtime.year
        bottomyear = articlelist[len(articlelist) - 1].apubtime.year
        self.articlebydate = []
        for year in range(bottomyear, topyear + 1):
            for month in range(1, 13):
                nums = len([article for article in articlelist if article.apubtime.year == year and article.apubtime.month ==month])
                if nums != 0:
                    self.articledate.insert(0, {'year':year, 'month':month, 'num':nums})

class ArticleListObject(object):
    def __init__(self, article):
        self.id = article.aid
        self.title = article.atitle
        self.subcontent = article.acontent[:300]
        self.content = article.acontent
        self.type = article.atype.typename
        self.typelink = ''
        self.pubtime = article.apubtime
        self.chgtime = article.achgtime
        self.user = article.auser.username
        self.useravatar = article.auser.uavatar
        self.userlink = '/members/m/' + str(article.auser.uid)

class Pagination(object):
    def __init__(self):
        self.pre = ''
        self.next = ''
        self.pages = []
        self.current = ''
        self.action = ''

def generatePagination(action, bloglist, targetpage):
    targetpage = int(targetpage)
    pagination = Pagination()
    pagination.current = targetpage
    maxpage = len(bloglist)
    pagination.pages = range(1, maxpage/10+2)
    pagination.pre = str(targetpage-1) if targetpage-1 in pagination.pages else str(targetpage)
    pagination.next = str(targetpage+1) if targetpage+1 in pagination.pages else str(targetpage)
    pagination.action = action
    bloglist = bloglist[(targetpage-1) * 10 : targetpage * 10]
    return bloglist, pagination


class Home(homeBase):
    def get(self):
        homeBase.init(self)
        self.title = 'Home'
        informlist = self.session.query(Inform).order_by(Inform.icettime)[:3]
        pagelist = self.session.query(Page).order_by(Page.ppubtime)[:3]
        self.render('home_index.html', pagelist = pagelist, informlist = informlist)

class ListProjects(homeBase):
    def get(self, pid):
        homeBase.init(self)
        self.title = 'Projects'
        pagelist = self.session.query(Page).all()
        pageList, self.pagination = generatePagination('/projects/', pagelist, pid)
        self.render('home_plist.html', list = pageList)

class ShowProjects(homeBase):
    def get(self, pid):
        homeBase.init(self)
        page = self.session.query(Page).filter(Page.pid == pid).first()
        self.title = page.ptitle
        self.render('home_showpage.html', page = page)

class ListMembers(homeBase):
    def get(self):
        homeBase.init(self)
        self.title = 'Members'
        mtype = ['All', 'Master', 'Ph.D', 'Bachelor', 'Professor', 'Guest Prof']
        degree = self.get_argument('degree', default='All')
        if degree == 'All':
            memberlist = self.session.query(User).all()
        else:
            memberlist = self.session.query(User).filter(User.ugrade == degree).all()
        self.render('home_members.html', memberlist = memberlist, mtype = mtype, degree = degree)

class ListArticles(homeBase):
    def get(self, aid):
        homeBase.init(self)
        self.title = 'Articles'
        articlelist = []
        for one in self.session.query(Article).order_by(Article.apubtime).all():
            articlelist.insert(0, ArticleListObject(one))
        alist, self.pagination = generatePagination('/articles/', articlelist, aid)
        self.render('home_alist.html', list = alist)

class ShowArticles(homeBase):
    def get(self, id):
        homeBase.init(self)
        one = self.session.query(Article).filter(Article.aid == id).first()
        self.title = one.atitle
        article = ArticleListObject(one)
        self.render('home_showarticle.html', article = article)

class ShowAbout(homeBase):
    def get(self):
        homeBase.init(self)
        self.title = 'About us'
        info_path = os.path.join(self.get_template_path(), 'aboutme.md')
        aboutcontent = markdown.markdown(open(info_path).read().decode('utf8'))
        self.render('home_about.html', aboutcontent = aboutcontent)

class ShowContact(homeBase):
    def get(self):
        homeBase.init(self)
        self.title = 'Contact us'
        self.render('home_contact.html')

    def post(self):
        homeBase.init(self)
        cname = self.get_argument('name', default='')
        ccollege = self.get_argument('college', default='')
        cemail = self.get_argument('email', default='')
        creason = self.get_argument('creason', default='')
        contact = Contact(cname, ccollege, cemail, creason)
        if 'file' in self.request.files:
            file_dict_list = self.request.files['file']
            for file_dict in file_dict_list:
                filename = nameRewrite(file_dict["filename"]).encode('utf8')
                data = file_dict["body"]
                with open(resume_path + filename, 'w') as f:
                    f.write(data)
                    print filename
            contact.cresume = resume_path + filename
        self.session.add(contact)
        self.session.commit()
        self.write('<script language="javascript">alert("提交成功");self.location="/";</script>')

class ShowMyPage(homeBase):
    def get(self, uid):
        homeBase.init(self)
        user = self.session.query(User).filter(User.uid == uid).first()
        self.title = user.username
        self.render('home_page.html', user = user)

class EditArticle(homeBase):
    @tornado.web.authenticated
    def get(self, uid):
        homeBase.init(self)
        print uid
        self.title = 'Edit Article'
        typelist = self.session.query(Type).all()
        self.render('home_writepage.html', typelist = typelist, uid = uid)

    def post(self, uid):
        homeBase.init(self)
        self.title = 'Edit Article'
        atitle = self.get_argument('atitle', default='')
        acontent = self.get_argument('acontent', default='')
        taid = self.get_argument('optionsRadios', default='')
        article = Article(atitle, acontent, uid, taid)
        self.session.add(article)
        self.session.commit()
        self.write('<script language="javascript">alert("提交成功");self.location="/members/m/%s"</script>') % str(uid)


class EditProfile(homeBase):
    @tornado.web.authenticated
    def get(self, id):
        homeBase.init(self)
        self.title = 'Edit Profile'
        self.render('home_profile.html', id = id)

    @tornado.web.authenticated
    def post(self, id):
        homeBase.init(self)
        self.title = 'Edit Profile'
        ucollege = self.get_argument('ucollege', default='')
        ugrade = self.get_argument('ugrade', default='')
        udomain = self.get_argument('udomain', default='')
        ubio = self.get_argument('ubio', default='')
        user = self.session.query(User).filter(User.username == self.signeduser).first()
        user.ucollege = ucollege
        user.ugrade = ugrade
        user.udomain = udomain
        user.ubio = ubio
        if 'file' in self.request.files:
            file_dict_list = self.request.files['file']
            for file_dict in file_dict_list:
                filename = nameRewrite(file_dict["filename"]).encode('utf8')
                data = file_dict["body"]
                with open(avatar_path + filename, 'w') as f:
                    f.write(data)
                    print filename
            user.uavatar = '/static/avatar/' + filename
        else:
            user.uavatar = '/static/images/' + 'avatar-'+ str(random.randint(1,16)) +'.svg'
        self.session.commit()
        self.write('<script language="javascript">alert("OK,Entering your own homepage!!");self.location="/";</script>')