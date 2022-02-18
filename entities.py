from sys import settrace
from blinker import signal
from datetime import datetime



class Signals:

    def __init__(self, *args, **kwargs):
        self.created.send()

    def __new__(cls, *args, **kwargs):
        
        instance = super(Signals, cls).__new__(cls)
        instance.created = signal('created')
        instance.created.connect(instance.saved)

        instance.delete = signal('delete')
        instance.delete.connect(instance.deleted)

        instance.delete_attribute = signal('delete_attribute')
        instance.delete_attribute.connect(instance.deleted_attribute)

        instance.black_list = signal('black_list')
        instance.black_list.connect(instance.blacklisted)

        return instance
    
    def __del__(self, ):
        self.is_deleted=True
        self.delete.send()

    def __delattr__(self, __name: str) -> None:
        self.delete_attribute.send()

    @property
    def is_blacklisted(self):
         return self._is_blacklisted
       
    @is_blacklisted.setter
    def is_blacklisted(self, a):
        self._is_blacklisted = a
        self.black_list.send()

    def blacklisted(self, *args, **kwargs):
        print("Got a black list signal sent by %r" % self)

    def saved(self, *args, **kwargs):
        print("Got a saved signal sent by %r" % self)

    def deleted(self, *args, **kwargs, ):
        print("Got a delete signal sent by %r" % self)

    def deleted_attribute(self, *args, **kwargs, ):
        print("Got a delete attribute signal sent by %r" % self)

class CRAWLING_STATUSES:
    NOT_CRAWLED = 0
    ERROR_REQUESTING_LINK = 1
    UPDATING_LINK = 2
    MARKED_AS_DUPLICATE = 3
    UPDATED_LINK = 4
    CRAWLING = 5
    CRAWLING_FAILED = 6
    RESCHEDULED_LONG_CRAWLING = 7
    CRAWLING_TOO_LONG = 8
    HAS_NO_PAGES = 9
    TEXT_UPLOADED = 10
    AWAITING_CRAWL = 11
    INDEXED_BY_ELASTIC = 12
    TEXT_ANALYZED = 13
    DOMAIN_INVALID = 14
    NO_LINKS_IN_PAGE = 15
    UNCRAWLABLE = 16


class CrawlableEntity(Signals, ):
    '''
        link: str
        name: str
        crawling_status: int # from CRAWLING_STATUSES
        is_deleted: bool
        is_blacklisted: bool
        last_crawled: Optional[datetime]
    '''

    def __init__(self, link, name, crawling_status=CRAWLING_STATUSES.NOT_CRAWLED, is_deleted=False, is_blacklisted=False, last_crawled=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.link = link
        self.name = name
        self.crawling_status = crawling_status
        self.is_blacklisted = is_blacklisted
        self.is_deleted = is_deleted
        self.last_crawled = last_crawled


class Event(CrawlableEntity):
    '''
        start_date: datetime
        end_date: Optional[datetime]
        description: Optional[str]
        location: Optional[str]
    '''

    def __init__(self, start_date, description=None, location=None, end_date=None, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.location = location


class Webinar(CrawlableEntity):
    '''
        start_date: datetime
        description: Optional[str]
        language: str
    '''

    def __init__(self, start_date, description=None, language="en", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.description = description
        self.language = language


class Company(CrawlableEntity):
    '''
        employees_min: int
        employees_max: int
    '''

    def __init__(self, employees_min, employees_max, **kwargs):
        super().__init__(**kwargs)
        self.employees_min = employees_min
        self.employees_max = employees_max


class ContentItem(CrawlableEntity):
    '''
        snippet: Optional[str]
        company: Company
    '''

    def __init__(self, company, snippet=None, **kwargs):
        super().__init__(**kwargs)
        self.company = company
        self.snippet = snippet


class CompanyForEvent(Signals):
    '''
        event: Event
        company: Company
        is_deleted: bool
        is_blacklisted: bool
    '''

    def __init__(self, event, company, is_deleted=False, is_blacklisted=False, **kwargs):
        super().__init__(**kwargs)
        self.event = event
        self.company = company
        self.is_blacklisted = is_blacklisted
        self.is_deleted = is_deleted


class CompanyForWebinar(Signals):
    '''
        webinar: Webinar
        company: Company
        is_deleted: bool
        is_blacklisted: bool
    '''

    def __init__(self, webinar, company, is_deleted=False, is_blacklisted=False, **kwargs):
        super().__init__(**kwargs)
        self.webinar = webinar
        self.company = company
        self.is_blacklisted = is_blacklisted
        self.is_deleted = is_deleted


class CompanyCompetitor(Signals):
    '''
        company: Company
        competitor: Company
        is_deleted: bool
    '''

    def __init__(self, company, competitor, is_deleted=False, **kwargs):
        super().__init__(**kwargs)
        self.company = company
        self.competitor = competitor
        self.is_deleted = is_deleted


if __name__ == "__main__":

    print("*"*20)
    print("creation signals: ")
    print("*"*20)
    ce = CrawlableEntity("link", "name")
    Event(start_date=datetime.today(), link="link", name="name")
    Webinar(start_date=datetime.today(), link="link", name="name")
    Company(20, 2004, link="link", name="name")
    ContentItem(company="company",link="link", name="name")
    CompanyForEvent(event="event", company="company")
    cfw = CompanyForWebinar(webinar="webinar", company="company", )
    cc = CompanyCompetitor(company="company", competitor="competitor")

    print("*"*20)
    print("deletation signals: ")
    print("*"*20)
    del ce


    print("*"*20)
    print("deletation attribute signals: ")
    print("*"*20)
    delattr(cc, 'company')

    print("*"*20)
    print("deletation black listed signals: ")
    print("*"*20)
    cfw.is_blacklisted=True