import getpass
import imaplib
import datetime
from multiprocessing.pool import ThreadPool


def connect_imap():
    m = imaplib.IMAP4_SSL("imap.gmail.com")  # server to connect to
    print(
        "{0} Connecting to mailbox via IMAP...".format(
            datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    username = input("Please enter your Gmail user name")
    pw = getpass.getpass("Password:")
    m.login(username, pw)

    return m


def mark_read(m, folder, from_string):
    try:
        no_of_msgs = int(
            m.select(f'"{folder}"')[1][0]
        )  # required to perform search, m.list() for all labels, '[Gmail]/Sent Mail'
        # print("- Found a total of {1} messages in '{0}'.".format(folder, no_of_msgs))

        # typ, data = m.search(None, '(FROM {0})'.format(from_string))  # search pointer for msgs
        typ, data = m.search(
            None, '(FROM "{0}" UNSEEN)'.format(from_string)
        )  # search pointer for msgs

        if data != [""]:  # if not empty list means messages exist
            index_messages = data[0].split()
            print(
                "- Marked {0} messages read from {1} in '{2}'.".format(
                    len(index_messages), from_string, folder
                )
            )
            for i in index_messages:
                m.store(i, "+FLAGS", "\Seen")  # mark as read
                # m.store(i.replace(' ',','),'+FLAGS','\Seen') # mark as read
            return len(index_messages)
        else:
            # print("- Nothing to mark read.")
            return None
    except Exception as e:
        print(e)


def move_to_trash_before_date(m, folder, days_before):
    try:
        no_of_msgs = int(
            m.select(f'"{folder}"')[1][0]
        )  # required to perform search, m.list() for all lables, '[Gmail]/Sent Mail'
        # print("- Found a total of {1} messages in '{0}'.".format(folder, no_of_msgs))

        before_date = (
            datetime.date.today() - datetime.timedelta(days_before)
        ).strftime(
            "%d-%b-%Y"
        )  # date string, 04-Jan-2013
        typ, data = m.search(
            None, "(BEFORE {0})".format(before_date)
        )  # search pointer for msgs before before_date

        if data != [""]:  # if not empty list means messages exist
            no_msgs_del = data[0].split()[-1]  # last msg id in the list
            # print("- Marked {0} messages for removal with dates before {1} in '{2}'.".format(no_msgs_del, before_date, folder))
            m.store(
                "1:{0}".format(no_msgs_del), "+X-GM-LABELS", "\\Trash"
            )  # move to trash
            # print("Deleted {0} messages.".format(no_msgs_del))
        # else:
        # print("- Nothing to remove.")

        return
    except Exception as e:
        print(e)


def move_to_trash_from(m, folder, from_string):
    try:
        no_of_msgs = int(
            m.select(f'"{folder}"')[1][0]
        )  # required to perform search, m.list() for all labels, '[Gmail]/Sent Mail'
        # print("- Found a total of {1} messages in '{0}'.".format(folder, no_of_msgs))

        # typ, data = m.search(None, '(FROM {0})'.format(from_string))  # search pointer for msgs
        typ, data = m.search(
            None, '(OR (TO "{0}") (FROM "{0}"))'.format(from_string)
        )  # search pointer for msgs

        if data != [""]:  # if not empty list means messages exist
            index_messages_to_delete = data[0].split()
            print(
                "- Marked {0} messages for removal from {1} in '{2}'.".format(
                    len(index_messages_to_delete), from_string, folder
                )
            )
            for i in index_messages_to_delete:
                m.store(i, "+X-GM-LABELS", "\\Trash")  # move to trash
            # print("Deleted {0} messages.".format(no_msgs_del))
            return len(index_messages_to_delete)
        else:
            # print("- Nothing to remove.")
            return None
    except Exception as e:
        print(e)


def empty_folder(m, folder, do_expunge=True):
    # print("- Empty '{0}' & Expunge all mail...".format(folder))
    m.select(f'"{folder}"')  # select all trash
    m.store("1:*", "+FLAGS", "\\Deleted")  # Flag all Trash as Deleted
    if do_expunge:  # See Gmail Settings -> Forwarding and POP/IMAP -> Auto-Expunge
        m.expunge()  # not need if auto-expunge enabled
    # else:
    #     print("Expunge was skipped.")


def disconnect_imap(m):
    print(
        "{0} Done. Closing connection & logging out.".format(
            datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    m.close()
    m.logout()
    # print "All Done."
    return


if __name__ == "__main__":
    pool = ThreadPool(1)
    m_con = connect_imap()
    pool.apply_async(
        mark_read,
        args=(m_con, "[Gmail]/All Mail", "do-not-reply@allegis-marketplace.com"),
    )
    pool.apply_async(mark_read, args=(m_con, "[Gmail]/All Mail", "venmo@venmo.com"))
    pool.apply_async(mark_read, args=(m_con, "[Gmail]/All Mail", "jeff.sproul@rcu.org"))
    pool.apply_async(
        mark_read, args=(m_con, "[Gmail]/All Mail", "TimeAndExpense@allegisgroup.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "team@mint.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@indeed.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@linkedin.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "newsletter@techcrunch.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "capitalone@notification.capitalone.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "kaggle.intercom-mail.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "calendar-notification@google.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "vehiclediagnostics@onstar.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@spotify.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "subscriptions@subscriptions.usa.gov"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "email@et.npr.org")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "customerservice@emcom.bankofamerica.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "ebanking@bankpeoples.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "matthew.dassow@footlocker.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "USPSInformedDelivery@usps.gov"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "theskimm.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "engagesupport@daxkoengage.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "americanexpress@member.americanexpress.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "discover@service.discover.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@gowild.wi.gov")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "citicards@info4.citi.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "dave@ustvnow.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@covepointlodge.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(
            m_con,
            "[Gmail]/All Mail",
            "empowerhernet@gmail.com via mailchimpapp.net",
        ),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "goto@docker.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "HomeDepotCustomerCare@email.homedepot.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "mknowlan@aflag.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "no-reply@alertsp.chase.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "widnr@service.govdelivery.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "citicards@info6.citi.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(
            m_con,
            "[Gmail]/All Mail",
            "wellsfargoretirementplans@retire1.wellsfargo.com",
        ),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(
            m_con,
            "[Gmail]/All Mail",
            "wellsfargoretirementplans@retire2.wellsfargo.com",
        ),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "news@onxmaps.today")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "Yahoo@communications.yahoo.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "no-reply@email.homedepot.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "Atlassian@eastbay.com ")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "participant_services@eonline.e-vanguard.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "do-not-reply@stackoverflow.email"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "support@codewithmosh.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "gmb1983@gmail.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "support@github.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "partners@mail.outdoorlife.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "ParticipantServices@vanguard.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "EDELIVERY@ivyinvestments.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "noreply@statuspage.io")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "hello@news.gemini.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "discover@card-e.em.discover.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "no-reply@updates.coinbase.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "billpay@billpay.bankofamerica.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "Chase@e.chase.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "Travel.Wisconsin@public.govdelivery.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "aws-marketing-email-replies@amazon.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@milwaukeetool.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "focusinfo@focusonenergy.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "account@nest.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "noreply@mailer.bitbucket.org"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "discover@e.discover.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@sports.yahoo.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "myaccount@we-energies.com"),
    )
    pool.apply_async(move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "web@cex.io"))
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "ecards@123greetings.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@johnkasich.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@email.skype.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "noreply@email.kraken.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@atlassian.com")
    )
    pool.apply_async(move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "fitbit.com"))
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "email@messages.autotrader.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@datascience.smu.edu")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "homedepotdecor@email.homedepot.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@docker.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "hello@talkpython.fm")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "ambassador@anaconda.com ")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "team@kaggle.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@lake-link.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "email@mail.onedrive.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@northernresort.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "no-reply@dropboxmail.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@quantopian.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "paypal@mail.paypal.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "noreply@wisconsinpublicservice.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "connect@quandl.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@windscribe.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@twitter.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@messages.cargurus.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@namecheap.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@email.cbssports.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "wisconsinpublicservice@us.confirmit.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@mystubhub.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "AmericanExpress@welcome.aexp.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "help@walmart.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@mail.zillow.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "info@meetup.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@emails.chase.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "noreply@qemailserver.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "noreply@getipass.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "amazon-move@amazon.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "no-reply@mymove.com")
    )
    pool.apply_async(move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "siriusxm"))
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "noreply@robinhood.com")
    )
    pool.apply_async(move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "stitcher"))
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "camelcamelcamel")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@email.ticketmaster.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "no-reply@gdax.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "maillist.codeproject.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "cabelas@emails.cabelas.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "support@allclearid.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "upwork@e.upwork.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "@news.digitalocean.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(
            m_con,
            "[Gmail]/All Mail",
            "Participant_Education@eonline.e-vanguard.com",
        ),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "podcast@talkpython.fm")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "mailout@maillist.codeproject.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "editor@toptal.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "Kwikrewards@kwiktrip.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "digest-noreply@quora.com")
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "RANWW@northwestmatrixmail.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "newsletter@news.farmandfleet.com"),
    )
    pool.apply_async(
        move_to_trash_from,
        args=(m_con, "[Gmail]/All Mail", "offers@your.offers.dominos.com"),
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "email@nl.npr.org")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "eTalk@bankpeoples.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "email@nl.npr.org")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "noreply@glassdoor.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "alert@indeed.com")
    )
    pool.apply_async(
        move_to_trash_from, args=(m_con, "[Gmail]/All Mail", "surveys@google.com")
    )

    # Mark read
    pool.apply_async(
        mark_read, args=(m_con, "[Gmail]/All Mail", "support.allclearid@allclearid.com")
    )
    pool.apply_async(
        mark_read,
        args=(
            m_con,
            "[Gmail]/All Mail",
            "ComputershareOnlineServices@cpucommunication.com",
        ),
    )
    pool.apply_async(
        mark_read,
        args=(m_con, "[Gmail]/All Mail", "onlinebanking@ealerts.bankofamerica.com"),
    )
    pool.apply_async(
        mark_read, args=(m_con, "[Gmail]/All Mail", "donotreply@upwork.com")
    )
    pool.apply_async(
        mark_read,
        args=(m_con, "[Gmail]/All Mail", "duluthtrading@duluthtradingemail.com"),
    )

    # move_to_trash_before_date(m_con, '[Gmail]/All Mail', 365)  # inbox cleanup, before 1 yr
    while True:
        try:
            from_string = input(
                'Enter an email address you would like to have purged from All Mail inbox else type "stop" to end'
            )
            if from_string.lower() != "stop":
                pool.apply_async(
                    move_to_trash_from, args=(m_con, "[Gmail]/All Mail", from_string)
                )
            else:
                break
        except Exception as e:
            print(e)

    pool.close()
    pool.join()

    # empty_folder(m_con, '[Gmail]/Trash', do_expunge=True)  # can send do_expunge=False, default True

    disconnect_imap(m_con)
