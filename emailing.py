import smtplib  # module for sending email messages using Simple Mail Transfer Protocol (SMTP)
import imghdr  # module for determining the image type of file
from email.message import EmailMessage  # module for creating email messages

PASSWORD = "Enter your email password here"  # password for the email account
SENDER = "Enter the sender email"  # email address of the sender
RECEIVER = "Enter the receiver email here"  # email address of the receiver

def send_email(image_path):
    """
    A function that sends an email message with an attached image file.
    """
    print("send_email_function started")
    email_message = EmailMessage()
    email_message["Subject"] = "Alert - camera detected movement"  # subject of the email message
    email_message.set_content("Hey, we just saw a new unrecognized movement trough the camera")  # body of the email message

    # read the image file and add it as an attachment to the email message
    with open(image_path, "rb") as file:
        content = file.read()
    email_message.add_attachment(content, maintype="image", subtype=imghdr.what(None, content))

    # connect to the SMTP server and send the email message
    gmail = smtplib.SMTP("smtp.gmail.com", 587)  # connect to the Gmail SMTP server
    gmail.ehlo()  # identify the client to the server
    gmail.starttls()  # put the SMTP connection in TLS (Transport Layer Security) mode
    gmail.login(SENDER, PASSWORD)  # login to the email account
    gmail.sendmail(SENDER, RECEIVER, email_message.as_string())  # send the email message
    gmail.quit()  # close the SMTP connection

    print("send_email_function ended")

if __name__ == "__main__":
    send_email(image_path="images/1.png")  # call the send_email function with the path of the image file as argument
