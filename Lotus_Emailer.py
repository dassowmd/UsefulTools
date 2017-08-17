import smtplib
from datetime import datetime

def prepare_email(subject, body, start_time):

    # Fill these in with the appropriate info...
    fromaddr='matthew.dassow@footlocker.com'
    toaddr=['matthew.dassow@footlocker.com', 'dassowmd@gmail.com']

    # Send notification email
    notice_EMail(start_time, fromaddr, toaddr, subject, body)

def notice_EMail(start_time, fromaddr, toaddr, subject, body):

    # Calculate run time
    runtime=datetime.now() - start_time

    # Initialize SMTP server and port
    server = smtplib.SMTP('MLWSMTP', 25)

    # Send email
    senddate=datetime.strftime(datetime.now(), '%Y-%m-%d')
    m="Date: %s\r\nFrom: %s\r\nTo: %s\r\nSubject: %s\r\nX-Mailer: My-Mail\r\n\r\n" % (senddate, fromaddr, toaddr, subject)

    server.sendmail(fromaddr, toaddr, m+body+' after ' + str(runtime) + ' hours')
    server.quit()

try:
    start_time=datetime.now()
    # Do something here

    
    # Send success email
    prepare_email(subject='Success Test', body='The test program ran and a test email was sent ', start_time=start_time)
except Exception as e:
    # Send failure email
    prepare_email(subject='Failure Test', body='The test program ran and failed with exception %s. Test email was sent' %e, start_time=start_time)
