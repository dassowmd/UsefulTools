import getpass
import imaplib
import datetime

def connect_imap():
    m = imaplib.IMAP4_SSL("imap.gmail.com")  # server to connect to
    print("{0} Connecting to mailbox via IMAP...".format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
    username = raw_input('Please enter your Gmail user name')
    pw = getpass.getpass('Password:')
    m.login(username, pw)

    return m


def move_to_trash_before_date(m, folder, days_before):
    no_of_msgs = int(m.select(folder)[1][0])  # required to perform search, m.list() for all lables, '[Gmail]/Sent Mail'
    print("- Found a total of {1} messages in '{0}'.".format(folder, no_of_msgs))

    before_date = (datetime.date.today() - datetime.timedelta(days_before)).strftime(
        "%d-%b-%Y")  # date string, 04-Jan-2013
    typ, data = m.search(None, '(BEFORE {0})'.format(before_date))  # search pointer for msgs before before_date

    if data != ['']:  # if not empty list means messages exist
        no_msgs_del = data[0].split()[-1]  # last msg id in the list
        print(
        "- Marked {0} messages for removal with dates before {1} in '{2}'.".format(no_msgs_del, before_date, folder))
        m.store("1:{0}".format(no_msgs_del), '+X-GM-LABELS', '\\Trash')  # move to trash
        # print("Deleted {0} messages.".format(no_msgs_del))
    else:
        print("- Nothing to remove.")

    return

def move_to_trash_from(m, folder, from_string):
    no_of_msgs = int(m.select(folder)[1][0])  # required to perform search, m.list() for all lables, '[Gmail]/Sent Mail'
    print("- Found a total of {1} messages in '{0}'.".format(folder, no_of_msgs))

    # typ, data = m.search(None, '(FROM {0})'.format(from_string))  # search pointer for msgs
    typ, data = m.search(None, '(OR (TO "{0}") (FROM "{0}"))'.format(from_string))  # search pointer for msgs

    if data != ['']:  # if not empty list means messages exist
        index_messages_to_delete = data[0].split()
        print(
        "- Marked {0} messages for removal from {1} in '{2}'.".format(len(index_messages_to_delete), from_string, folder))
        for i in index_messages_to_delete:
            m.store("{0}:{0}".format(i), '+X-GM-LABELS', '\\Trash')  # move to trash
        # print("Deleted {0} messages.".format(no_msgs_del))
    else:
        print("- Nothing to remove.")

    return



def empty_folder(m, folder, do_expunge=True):
    print("- Empty '{0}' & Expunge all mail...".format(folder))
    m.select(folder)  # select all trash
    m.store("1:*", '+FLAGS', '\\Deleted')  # Flag all Trash as Deleted
    if do_expunge:  # See Gmail Settings -> Forwarding and POP/IMAP -> Auto-Expunge
        m.expunge()  # not need if auto-expunge enabled
    else:
        print("Expunge was skipped.")
    return


def disconnect_imap(m):
    print("{0} Done. Closing connection & logging out.".format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
    m.close()
    m.logout()
    # print "All Done."
    return


if __name__ == '__main__':
    m_con = connect_imap()


    move_to_trash_from(m_con, '[Gmail]/All Mail', 'team@mint.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@indeed.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@linkedin.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'newsletter@techcrunch.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'capitalone@notification.capitalone.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'kaggle.intercom-mail.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'calendar-notification@google.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'vehiclediagnostics@onstar.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@spotify.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'subscriptions@subscriptions.usa.gov')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'email@et.npr.org')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'customerservice@emcom.bankofamerica.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'ebanking@bankpeoples.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'matthew.dassow@footlocker.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'USPSInformedDelivery@usps.gov')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'dailyskimm@morning7.theskimm.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'engagesupport@daxkoengage.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'americanexpress@member.americanexpress.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'discover@service.discover.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@gowild.wi.gov')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'citicards@info4.citi.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'dave@ustvnow.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@covepointlodge.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'goto@docker.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'HomeDepotCustomerCare@email.homedepot.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'mknowlan@aflag.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'no-reply@alertsp.chase.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'widnr@service.govdelivery.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'citicards@info6.citi.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'wellsfargoretirementplans@retire1.wellsfargo.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'wellsfargoretirementplans@retire2.wellsfargo.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'news@onxmaps.today')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'Yahoo@communications.yahoo.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'no-reply@email.homedepot.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'Atlassian@eastbay.com ')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'participant_services@eonline.e-vanguard.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'do-not-reply@stackoverflow.email')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'support@codewithmosh.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'gmb1983@gmail.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'support@github.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'partners@mail.outdoorlife.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'ParticipantServices@vanguard.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'EDELIVERY@ivyinvestments.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'noreply@statuspage.io')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'hello@news.gemini.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'discover@card-e.em.discover.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'no-reply@updates.coinbase.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'billpay@billpay.bankofamerica.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'Chase@e.chase.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'Travel.Wisconsin@public.govdelivery.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'aws-marketing-email-replies@amazon.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@milwaukeetool.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'focusinfo@focusonenergy.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'account@nest.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'noreply@mailer.bitbucket.org')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'discover@e.discover.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@sports.yahoo.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'myaccount@we-energies.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'web@cex.io')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'ecards@123greetings.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@johnkasich.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@email.skype.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'noreply@email.kraken.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@atlassian.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'fitbit.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'email@messages.autotrader.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@datascience.smu.edu')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'homedepotdecor@email.homedepot.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@docker.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'hello@talkpython.fm')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'ambassador@anaconda.com ')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'team@kaggle.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'info@lake-link.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'no-reply@dropboxmail.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@quantopian.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'paypal@mail.paypal.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'noreply@wisconsinpublicservice.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'connect@quandl.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@windscribe.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@twitter.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@messages.cargurus.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@namecheap.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@email.cbssports.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'wisconsinpublicservice@us.confirmit.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@mystubhub.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'AmericanExpress@welcome.aexp.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'help@walmart.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@mail.zillow.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'info@meetup.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@emails.chase.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'noreply@qemailserver.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'noreply@getipass.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'amazon-move@amazon.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'no-reply@mymove.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'siriusxm')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'noreply@robinhood.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'stitcher')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'camelcamelcamel')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', '@email.ticketmaster.com')  # inbox cleanup, from user
    move_to_trash_from(m_con, '[Gmail]/All Mail', 'no-reply@gdax.com')  # inbox cleanup, from user

    # move_to_trash_before_date(m_con, '[Gmail]/All Mail', 365)  # inbox cleanup, before 1 yr
    while True:
        try:
            from_string = raw_input('Enter an email address you would like to have purged from All Mail inbox else type "stop" to end')
            if from_string.lower() != 'stop':
                move_to_trash_from(m_con, '[Gmail]/All Mail', from_string)  # inbox cleanup, from user
            else:
                break
        except Exception as e:
            print e


    # empty_folder(m_con, '[Gmail]/Trash', do_expunge=True)  # can send do_expunge=False, default True

    disconnect_imap(m_con)