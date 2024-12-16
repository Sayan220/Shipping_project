from django.contrib import admin
from django.urls import path,include
from pdf_labels import views

urlpatterns = [
    path("",views.index, name="index"),
    path("generate/",views.generate_pdf, name="generate_pdf"),
    path('send-email/', views.send_email_addr, name='send_email_addr'),
]
