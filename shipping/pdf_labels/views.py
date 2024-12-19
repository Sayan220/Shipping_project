import csv
from django.shortcuts import *
from pathlib import Path
import io
import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
#from reportlab.lib.units import inch
from django.core.mail import EmailMessage
from reportlab.graphics.shapes import Drawing
from django.conf import settings

filePath=Path("labels.csv")
def index(request):
    if request.method=="POST" and "submit1" in request.POST:
        fcity=request.POST.get("from_city")
        fzip=request.POST.get("from_zip")
        tocity=request.POST.get("to_city")
        tozip=request.POST.get("to_zip")
        id=request.POST.get("product_id")
        product_name=request.POST.get("product_name")
        product_type=request.POST.get("product_type")
        email=request.POST.get("email")

        newDate=datetime.datetime.now().strftime('%d/%m/%Y')
        fileEx=filePath.exists()
        with open(filePath,'a',newline='') as f:
            write=csv.writer(f)
            if not fileEx:
                write.writerow(["FROM CITY","FROM ZIP","TO CITY","TO ZIP","PRODUCT ID","PRODUCT NAME","PRODUCT TYPE","DATE","EMAIL"])

            write.writerow([fcity,fzip,tocity,tozip,id,product_name,product_type,newDate,email])  
        return render(request,"index.html",{"message":"Data added"})

    return render(request,"index.html")

def generate_pdf(request):
    buffer=io.BytesIO()
    pdf=canvas.Canvas(buffer,pagesize=letter)
    
    if filePath.exists():
        with open(filePath,'r') as f:
            reader=csv.reader(f)
            next(reader)
            #y=750
            for r in reader:
                pdf.setFont("Helvetica-Bold",18)
                pdf.drawString(220,750,"SHIPPING BILL")
                pdf.setFont("Times-Bold",11)
                pdf.drawString(454,750,"Bill Number: "+r[4])
                pdf.drawString(454,730,f"Bill Date: {datetime.datetime.now().strftime('%d/%m/%Y')}")
                pdf.line(40,720,560,720)

                #y -= 20
                pdf.setFont("Helvetica-Bold",14)
                pdf.drawString(50,700,"FROM ADDRESS:")
                #pdf.drawString(50,y-40,f"FROM ADDRESS:")
                pdf.setFont("Times-Bold",12)
                pdf.drawString(74,680,"FROM CITY: "+r[0])
                pdf.drawString(74,660,"ZIP CODE: "+r[1])

                pdf.setFont("Helvetica-Bold",14)
                pdf.drawString(380,700,"TO ADDRESS:")
                pdf.setFont("Times-Bold",12)
                pdf.drawString(404,680,"TO CITY: "+r[2])
                pdf.drawString(404,660,"ZIP CODE: "+r[3])

                pdf.setFont("Helvetica-Bold",14)
                pdf.drawString(50,630,"PRODUCT DETAILS")
                pdf.setFont("Times-Bold",12)
                pdf.drawString(74,610,"PRODUCT ID: "+r[4])
                pdf.drawString(74,590,"PRODUCT NAME: "+r[5])
                pdf.drawString(74,570,"PRODUCT TYPE: "+r[6])

                # Barcode
                pdf.setFont("Helvetica-Bold",14)
                pdf.drawString(50,540,"BAR CODE")
                code=f"{r[4]}-{r[0]}-{r[2]}"
                barcode=code128.Code128(code,barHeight=36,barWidth=1.3)
                #barcode_draw=Drawing(200,50)
                #barcode_draw.add(barcode)
                #barcode.drawOn(pdf,60,500)
                #renderPDF.draw(barcode_draw,pdf,60,500)
                barcode.drawOn(pdf,60,500)
                # QR
                qr=QrCodeWidget(code)
                pdf.drawString(380,630,"QR CODE")
                qr_draw=Drawing(56,56)
                qr_draw.add(qr)
                renderPDF.draw(qr_draw,pdf,400,540)
                pdf.line(40,490,560,490)
                pdf.showPage()
    pdf.save()            
    buffer.seek(0)
    response=HttpResponse(buffer,content_type='application/pdf')
    response['Content-Disposition']='attachment; filename="shipping.pdf" '
    return response


def send_email_addr(request):
    if "submit3" in request.POST:
        target_email=request.POST.get("target_email")
        l1=[]
        with open(filePath,'r') as f:
            reader = csv.reader(f)
            next(reader)
            for r in reader:
                if r[8]==target_email:
                    l1.append(r)
        if not l1:
            return render(request,"index.html",{"message":"Email not found"})

        for r in l1:
            buffer=io.BytesIO()
            pdf=canvas.Canvas(buffer,pagesize=letter)

            pdf.setFont("Helvetica-Bold",18)
            pdf.drawString(220,750,"SHIPPING BILL")
            pdf.setFont("Times-Bold",11)
            pdf.drawString(454,750,"Bill Number: "+r[4])
            pdf.drawString(454,730,f"Bill Date: "+r[7])
            pdf.line(40,720,560,720)

            pdf.setFont("Helvetica-Bold",14)
            pdf.drawString(50,700,"FROM ADDRESS:")
            pdf.setFont("Times-Bold",12)
            pdf.drawString(74,680,"FROM CITY: "+r[0])
            pdf.drawString(74,660,"ZIP CODE: "+r[1])

            pdf.setFont("Helvetica-Bold",14)
            pdf.drawString(380,700,"TO ADDRESS:")
            pdf.setFont("Times-Bold",12)
            pdf.drawString(404,680,"TO CITY: " +r[2])
            pdf.drawString(404,660,"ZIP CODE: "+r[3])

            pdf.setFont("Helvetica-Bold",14)
            pdf.drawString(50,630,"PRODUCT DETAILS")
            pdf.setFont("Times-Bold",12)
            pdf.drawString(74,610,"PRODUCT ID: " +r[4])
            pdf.drawString(74,590,"PRODUCT NAME: "+r[5])
            pdf.drawString(74,570,"PRODUCT TYPE: "+r[6])

            pdf.setFont("Helvetica-Bold",14)
            pdf.drawString(50,540,"BAR CODE")
            code=f"{r[4]}-{r[0]}-{r[2]}"
            barcode=code128.Code128(code,barHeight=36,barWidth=1.3)
            barcode.drawOn(pdf,60,500)

            pdf.drawString(380,630,"QR CODE")
            qr=QrCodeWidget(code)
            qr_draw=Drawing(56,56)
            qr_draw.add(qr)
            renderPDF.draw(qr_draw,pdf,400,540)
            pdf.line(40,490,560,490)
            pdf.save()
            buffer.seek(0)
           
            email=EmailMessage(
                 subject="Shipping Label Details",
                 body=f"Dear Customer,\n\nPlease find your shipping bill attached.\n\nProduct ID:{r[4]}\n\nProduct Name:{r[5]}\n\n\nRegards,\nShipping Team.",
                 from_email=settings.EMAIL_HOST_USER,
                 to=[target_email],
                )
            email.attach("shipping.pdf",buffer.getvalue(),"application/pdf")         
            email.send()
            buffer.close() 
        print(l1)
        return render(request,"index.html",{"message":"Email sent with pdf"})    
                       
    return render(request,"index.html")
  
